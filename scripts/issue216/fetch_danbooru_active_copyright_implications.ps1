[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [string] $OutputPath,
    [int] $Limit = 1000,
    [int] $DelayMilliseconds = 1000,
    [int] $MaxPages = 100
)

$ErrorActionPreference = 'Stop'
if ($Limit -lt 1 -or $Limit -gt 1000) { throw 'Limit must be between 1 and 1000.' }
if ($DelayMilliseconds -lt 0) { throw 'DelayMilliseconds must be non-negative.' }

$output = [System.IO.Path]::GetFullPath($OutputPath)
$parent = [System.IO.Path]::GetDirectoryName($output)
if (-not (Test-Path -LiteralPath $parent -PathType Container)) {
    throw "Output directory does not exist: $parent"
}

$apiPrefix = "https://danbooru.donmai.us/tag_implications.json?search%5Bstatus%5D=active&search%5Bcategory%5D=3&limit=$Limit&page="
$fetchedAt = [DateTime]::UtcNow.ToString('yyyy-MM-ddTHH:mm:ssZ')
$pageToken = '1'
$rows = [System.Collections.Generic.List[object]]::new()
$pageRecords = [System.Collections.Generic.List[object]]::new()
$seenIds = [System.Collections.Generic.HashSet[int]]::new()
$previousLastId = [int]::MaxValue

for ($pageNumber = 1; $pageNumber -le $MaxPages; $pageNumber++) {
    $pageUrl = $apiPrefix + [uri]::EscapeDataString($pageToken)
    $response = $null
    for ($attempt = 1; $attempt -le 5; $attempt++) {
        try {
            $response = Invoke-RestMethod -Uri $pageUrl -TimeoutSec 60 -Headers @{
                'User-Agent' = 'DanbooruTagTool-Issue216-Research/1.0'
                'Accept' = 'application/json'
            }
            break
        } catch {
            if ($attempt -eq 5) { throw }
            Start-Sleep -Seconds ([Math]::Min(2 * $attempt, 10))
        }
    }

    # Invoke-RestMethod already enumerates JSON arrays. Wrapping an array in
    # another array can leave a nested Object[] whose .id is itself an array.
    if ($response -is [array]) {
        $pageRows = $response
    } else {
        $pageRows = @($response)
    }
    if ($pageRows.Count -eq 0) {
        $pageRecords.Add([pscustomobject]@{
            page_number = $pageNumber
            page_token = $pageToken
            page_url = $pageUrl
            row_count = 0
            first_id = ''
            last_id = ''
        })
        break
    }

    $ids = @($pageRows | ForEach-Object { [int]$_.id })
    if (($ids | Measure-Object -Minimum).Minimum -ge $previousLastId) {
        throw "Cursor pagination did not move toward older implication IDs at $pageUrl"
    }
    if ($ids.Count -ne ($ids | Select-Object -Unique).Count) {
        throw "Duplicate implication IDs within one API page: $pageUrl"
    }
    foreach ($row in $pageRows) {
        $id = [int]$row.id
        if (-not $seenIds.Add($id)) { throw "Duplicate implication ID across API pages: $id" }
        if ($row.status -ne 'active') { throw "Non-active implication returned by active-only endpoint: $id" }
        $rows.Add([pscustomobject]@{
            implication_id = $id
            antecedent_tag = [string]$row.antecedent_name
            consequent_tag = [string]$row.consequent_name
            status = [string]$row.status
            created_at = [string]$row.created_at
            updated_at = [string]$row.updated_at
            reason = [string]$row.reason
            creator_id = [string]$row.creator_id
            approver_id = [string]$row.approver_id
            source_url = 'https://danbooru.donmai.us/tag_implications.json?search%5Bstatus%5D=active&search%5Bcategory%5D=3'
            source_page_url = $pageUrl
            snapshot_fetched_at_utc = $fetchedAt
        })
    }
    $firstId = [int](($ids | Measure-Object -Maximum).Maximum)
    $lastId = [int](($ids | Measure-Object -Minimum).Minimum)
    if ($lastId -ge $previousLastId) { throw "Implication cursor failed monotonicity check at ID $lastId" }
    $pageRecords.Add([pscustomobject]@{
        page_number = $pageNumber
        page_token = $pageToken
        page_url = $pageUrl
        row_count = $pageRows.Count
        first_id = $firstId
        last_id = $lastId
    })
    Write-Output "Fetched page $pageNumber ($($pageRows.Count) rows; IDs $firstId..$lastId)"

    if ($pageRows.Count -lt $Limit) { break }
    $previousLastId = $lastId
    $pageToken = "b$lastId"
    if ($pageNumber -lt $MaxPages -and $DelayMilliseconds -gt 0) {
        Start-Sleep -Milliseconds $DelayMilliseconds
    }
}

if ($pageRecords.Count -ge $MaxPages -and $pageRecords[$pageRecords.Count - 1].row_count -eq $Limit) {
    throw "Reached MaxPages=$MaxPages without observing the end of the relation snapshot."
}

$rows | Sort-Object implication_id -Descending | Export-Csv -LiteralPath $output -NoTypeInformation -Encoding utf8
$pageManifestPath = [System.IO.Path]::ChangeExtension($output, '.pages.json')
[pscustomobject]@{
    endpoint = 'https://danbooru.donmai.us/tag_implications.json?search%5Bstatus%5D=active&search%5Bcategory%5D=3'
    filter_status = 'active'
    filter_consequent_category_id = 3
    pagination = 'Danbooru page=b<last implication id> cursor; IDs descend monotonically'
    snapshot_fetched_at_utc = $fetchedAt
    page_size = $Limit
    row_count = $rows.Count
    page_count = $pageRecords.Count
    implication_id_min = ($rows | Measure-Object implication_id -Minimum).Minimum
    implication_id_max = ($rows | Measure-Object implication_id -Maximum).Maximum
    pages = @($pageRecords)
} | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $pageManifestPath -Encoding utf8
Write-Output "Wrote $($rows.Count) active consequent-Copyright implications to $output"
Write-Output "Wrote pagination manifest to $pageManifestPath"
