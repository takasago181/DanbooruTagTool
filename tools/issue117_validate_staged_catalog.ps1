param(
    [Parameter(Mandatory = $true)]
    [string]$CatalogDirectory,
    [switch]$RequireSqliteCli
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$catalogDirectoryFull = [System.IO.Path]::GetFullPath($CatalogDirectory)
$catalogPath = Join-Path $catalogDirectoryFull "catalog.db"
$reportPath = Join-Path $catalogDirectoryFull "import-report.json"

$checks = New-Object System.Collections.Generic.List[object]

function Add-Check {
    param(
        [string]$Name,
        [bool]$Pass,
        [object]$Actual,
        [object]$Expected,
        [string]$Detail = ""
    )
    $checks.Add([pscustomobject]@{
        name = $Name
        pass = $Pass
        actual = $Actual
        expected = $Expected
        detail = $Detail
    })
}

function Assert-Equal {
    param(
        [string]$Name,
        [object]$Actual,
        [object]$Expected
    )
    Add-Check -Name $Name -Pass ($Actual -eq $Expected) -Actual $Actual -Expected $Expected
}

function Get-JsonProperty {
    param(
        [object]$Object,
        [string]$Name
    )
    if ($null -eq $Object) { return $null }
    $property = $Object.PSObject.Properties[$Name]
    if ($null -eq $property) { return $null }
    return $property.Value
}

if (-not (Test-Path -LiteralPath $catalogPath -PathType Leaf)) {
    throw "Missing staged catalog.db: $catalogPath"
}
if (-not (Test-Path -LiteralPath $reportPath -PathType Leaf)) {
    throw "Missing staged import-report.json: $reportPath"
}

$catalogItem = Get-Item -LiteralPath $catalogPath
$catalogHash = (Get-FileHash -LiteralPath $catalogPath -Algorithm SHA256).Hash.ToLowerInvariant()

$stream = [System.IO.File]::OpenRead($catalogPath)
try {
    $headerBytes = New-Object byte[] 16
    $read = $stream.Read($headerBytes, 0, $headerBytes.Length)
}
finally {
    $stream.Dispose()
}
$header = if ($read -eq 16) { [System.Text.Encoding]::ASCII.GetString($headerBytes) } else { "" }
Assert-Equal -Name "catalog.sqliteHeader" -Actual $header -Expected ("SQLite format 3" + [char]0)
Add-Check -Name "catalog.nonEmpty" -Pass ($catalogItem.Length -gt 4096) -Actual $catalogItem.Length -Expected "> 4096 bytes"

$report = Get-Content -LiteralPath $reportPath -Raw -Encoding UTF8 | ConvertFrom-Json

Assert-Equal -Name "report.Total" -Actual (Get-JsonProperty $report "Total") -Expected 126427
Assert-Equal -Name "report.General" -Actual (Get-JsonProperty $report "General") -Expected 30629
Assert-Equal -Name "report.Special" -Actual (Get-JsonProperty $report "Special") -Expected 3059
Assert-Equal -Name "report.Character" -Actual (Get-JsonProperty $report "Character") -Expected 35890
Assert-Equal -Name "report.Copyright" -Actual (Get-JsonProperty $report "Copyright") -Expected 8536
Assert-Equal -Name "report.Artist" -Actual (Get-JsonProperty $report "Artist") -Expected 48313

$taxonomy = Get-JsonProperty $report "GeneralTaxonomy"
Assert-Equal -Name "generalTaxonomy.Proposed" -Actual (Get-JsonProperty $taxonomy "Proposed") -Expected 28226
Assert-Equal -Name "generalTaxonomy.Unresolved" -Actual (Get-JsonProperty $taxonomy "Unresolved") -Expected 2403
$eligibleForBrowse = Get-JsonProperty $taxonomy "EligibleForBrowse"
Add-Check -Name "generalTaxonomy.EligibleForBrowseRange" -Pass ($null -ne $eligibleForBrowse -and [int64]$eligibleForBrowse -ge 0 -and [int64]$eligibleForBrowse -le 28226) -Actual $eligibleForBrowse -Expected "0..28226" -Detail "Exact value may be reduced by accepted ProductFit gating; it must never exceed PROPOSED."

$intent = Get-JsonProperty $report "SexualIntent"
Assert-Equal -Name "intent.Identities" -Actual (Get-JsonProperty $intent "Identities") -Expected 31752
Assert-Equal -Name "intent.Sexual" -Actual (Get-JsonProperty $intent "Sexual") -Expected 2037
Assert-Equal -Name "intent.Contextual" -Actual (Get-JsonProperty $intent "Contextual") -Expected 1951
Assert-Equal -Name "intent.NonSexual" -Actual (Get-JsonProperty $intent "NonSexual") -Expected 27759
Assert-Equal -Name "intent.Unclassified" -Actual (Get-JsonProperty $intent "Unclassified") -Expected 5
Assert-Equal -Name "intent.BackingRows" -Actual (Get-JsonProperty $intent "BackingRows") -Expected 33688

$reportedCategorySum =
    [int64](Get-JsonProperty $report "General") +
    [int64](Get-JsonProperty $report "Special") +
    [int64](Get-JsonProperty $report "Character") +
    [int64](Get-JsonProperty $report "Copyright") +
    [int64](Get-JsonProperty $report "Artist")
Assert-Equal -Name "report.categorySum" -Actual $reportedCategorySum -Expected 126427

$reportedIntentSum =
    [int64](Get-JsonProperty $intent "Sexual") +
    [int64](Get-JsonProperty $intent "Contextual") +
    [int64](Get-JsonProperty $intent "NonSexual") +
    [int64](Get-JsonProperty $intent "Unclassified")
Assert-Equal -Name "intent.classSum" -Actual $reportedIntentSum -Expected 31752

$reportedTaxonomySum =
    [int64](Get-JsonProperty $taxonomy "Proposed") +
    [int64](Get-JsonProperty $taxonomy "Unresolved")
Assert-Equal -Name "generalTaxonomy.classSum" -Actual $reportedTaxonomySum -Expected 30629

$sources = Get-JsonProperty $report "Sources"
$requiredSources = @(
    "data/source/danbooru-2026-09-02.csv",
    "data/derived/danbooru_alias_normalized_index_VERIFIED_34417.csv",
    "data/special2788/illustrious_tag_knowledge_base_2788.csv",
    "data/derived/special2788_VERIFIED_LINKAGE.csv",
    "data/derived/ruleset2/01_SPECIAL2788_JAPANESE_COMPLETE_CANDIDATE.csv",
    "data/runtime/japanese_overlay.json",
    "data/generation/special2788_generation_profile.csv",
    "docs/issue70/data/runtime/issue70_catalog_overlay.csv",
    "docs/issue118/production_candidate/sexual_intent_v1.csv"
)

foreach ($relative in $requiredSources) {
    $value = Get-JsonProperty $sources $relative
    Add-Check -Name ("sourceHash:" + $relative) -Pass ($value -is [string] -and $value -match '^[0-9a-fA-F]{64}$') -Actual $value -Expected "64-hex SHA-256"
}

$issue70Hash = Get-JsonProperty $sources "docs/issue70/data/runtime/issue70_catalog_overlay.csv"
$issue70HashText = if ($null -eq $issue70Hash) { "" } else { $issue70Hash.ToString().ToLowerInvariant() }
Assert-Equal -Name "sourceHash:#70-overlay" -Actual $issue70HashText -Expected "1d346ad75655ea6091f9bce9a4cf58b1cf6f8fac18c7eb441f8edd009ee81433"

$sqlite = Get-Command sqlite3 -ErrorAction SilentlyContinue
if ($null -eq $sqlite) {
    $sqliteExpected = if ($RequireSqliteCli.IsPresent) { "required" } else { "optional" }
    Add-Check -Name "sqliteCli.available" -Pass (-not $RequireSqliteCli.IsPresent) -Actual "not found" -Expected $sqliteExpected -Detail "Import-report and SQLite-header validation still ran. Install/provide sqlite3.exe for direct row queries."
}
else {
    Add-Check -Name "sqliteCli.available" -Pass $true -Actual $sqlite.Source -Expected "available"

    function Invoke-SqliteScalar {
        param([string]$Sql)
        $output = & $sqlite.Source $catalogPath $Sql 2>&1
        if ($LASTEXITCODE -ne 0) {
            throw "sqlite3 failed for [$Sql]: $($output -join [Environment]::NewLine)"
        }
        return (($output | Select-Object -First 1).ToString()).Trim()
    }

    Assert-Equal -Name "sqlite.userVersion" -Actual (Invoke-SqliteScalar "PRAGMA user_version;") -Expected "1"
    Assert-Equal -Name "sqlite.entries.total" -Actual (Invoke-SqliteScalar "SELECT COUNT(*) FROM entries;") -Expected "126427"
    Assert-Equal -Name "sqlite.entries.General" -Actual (Invoke-SqliteScalar "SELECT COUNT(*) FROM entries WHERE id LIKE 'G:%';") -Expected "30629"
    Assert-Equal -Name "sqlite.entries.Special" -Actual (Invoke-SqliteScalar "SELECT COUNT(*) FROM entries WHERE id LIKE 'S:%';") -Expected "3059"
    Assert-Equal -Name "sqlite.entries.Character" -Actual (Invoke-SqliteScalar "SELECT COUNT(*) FROM entries WHERE id LIKE 'C:%';") -Expected "35890"
    Assert-Equal -Name "sqlite.entries.Copyright" -Actual (Invoke-SqliteScalar "SELECT COUNT(*) FROM entries WHERE id LIKE 'R:%';") -Expected "8536"
    Assert-Equal -Name "sqlite.entries.Artist" -Actual (Invoke-SqliteScalar "SELECT COUNT(*) FROM entries WHERE id LIKE 'A:%';") -Expected "48313"
    Assert-Equal -Name "sqlite.ordinaryIdentityUnion" -Actual (Invoke-SqliteScalar "SELECT COUNT(DISTINCT COALESCE(canonical,id)) FROM entries WHERE id LIKE 'G:%' OR id LIKE 'S:%';") -Expected "31752"
    Assert-Equal -Name "sqlite.metadata.rows" -Actual (Invoke-SqliteScalar "SELECT COUNT(*) FROM metadata;") -Expected "1"
}

$failed = @($checks | Where-Object { -not $_.pass })

$result = [ordered]@{
    generatedAt = (Get-Date).ToString("o")
    mode = "STAGED_CATALOG_VALIDATION"
    catalogDirectory = $catalogDirectoryFull
    catalog = [ordered]@{
        path = $catalogPath
        size = $catalogItem.Length
        sha256 = $catalogHash
    }
    passed = ($failed.Count -eq 0)
    checks = $checks
    failedChecks = $failed
}

$result | ConvertTo-Json -Depth 8

if ($failed.Count -gt 0) {
    exit 1
}
exit 0
