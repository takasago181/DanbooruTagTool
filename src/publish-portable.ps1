param(
    [Parameter(Mandatory=$true)][string]$Catalog,
    [ValidateSet('current', 'publish')][string]$Destination = 'current',
    [string]$Dotnet = 'dotnet'
)

$ErrorActionPreference = 'Stop'
$catalogPath = (Resolve-Path -LiteralPath $Catalog).Path
$repositoryRoot = Split-Path -Parent $PSScriptRoot
$artifactRoot = Join-Path $repositoryRoot 'artifacts'
$publishPath = [IO.Path]::GetFullPath((Join-Path $artifactRoot $Destination))
$stagePath = Join-Path ([IO.Path]::GetTempPath()) ("DanbooruTagTool-publish-{0}" -f [guid]::NewGuid().ToString('N'))

New-Item -ItemType Directory -Path $stagePath | Out-Null
try {
    & $Dotnet publish (Join-Path $PSScriptRoot 'DanbooruTagTool.App/DanbooruTagTool.App.csproj') -c Release -r win-x64 --self-contained true -p:PublishSingleFile=false -m:1 -o $stagePath
    if ($LASTEXITCODE -ne 0) { throw 'Portable publish failed' }

    $stageData = Join-Path $stagePath 'Data'
    New-Item -ItemType Directory -Path $stageData -Force | Out-Null
    Copy-Item -LiteralPath $catalogPath -Destination (Join-Path $stageData 'catalog.db') -Force

    $executablePath = Join-Path $publishPath 'DanbooruTagTool.exe'
    $runningApp = @(Get-Process -Name 'DanbooruTagTool' -ErrorAction SilentlyContinue | Where-Object {
        $_.Path -and ([IO.Path]::GetFullPath($_.Path)).Equals($executablePath, [System.StringComparison]::OrdinalIgnoreCase)
    })
    if ($runningApp.Count -gt 0) {
        throw "Close DanbooruTagTool from '$publishPath' before updating this output."
    }

    if (Test-Path -LiteralPath $publishPath -PathType Leaf) {
        throw "Output path is a file: $publishPath"
    }
    New-Item -ItemType Directory -Path $publishPath -Force | Out-Null

    $stageFiles = @(Get-ChildItem -LiteralPath $stagePath -File -Recurse -Force)
    $stageRelativePaths = [System.Collections.Generic.HashSet[string]]::new([System.StringComparer]::OrdinalIgnoreCase)
    foreach ($file in $stageFiles) {
        $relativePath = $file.FullName.Substring($stagePath.Length + 1)
        [void]$stageRelativePaths.Add($relativePath)
    }

    $staleFiles = @(Get-ChildItem -LiteralPath $publishPath -File -Recurse -Force | Where-Object {
        $relativePath = $_.FullName.Substring($publishPath.Length + 1)
        -not $relativePath.StartsWith(('UserData' + [IO.Path]::DirectorySeparatorChar), [System.StringComparison]::OrdinalIgnoreCase) -and
            -not $stageRelativePaths.Contains($relativePath)
    })

    foreach ($file in $stageFiles) {
        $relativePath = $file.FullName.Substring($stagePath.Length + 1)
        if ($relativePath.StartsWith(('UserData' + [IO.Path]::DirectorySeparatorChar), [System.StringComparison]::OrdinalIgnoreCase)) {
            continue
        }
        $destinationPath = Join-Path $publishPath $relativePath
        $destinationDirectory = Split-Path -Parent $destinationPath
        New-Item -ItemType Directory -Path $destinationDirectory -Force | Out-Null
        Copy-Item -LiteralPath $file.FullName -Destination $destinationPath -Force
    }
    foreach ($file in $staleFiles) {
        Remove-Item -LiteralPath $file.FullName -Force
    }

    $userDataPath = Join-Path $publishPath 'UserData'
    New-Item -ItemType Directory -Path $userDataPath -Force | Out-Null
    $userDataReadme = Join-Path $userDataPath 'README.txt'
    if (-not (Test-Path -LiteralPath $userDataReadme)) {
        Set-Content -LiteralPath $userDataReadme -Value 'user.db is created here on first launch. This directory is preserved when this fixed artifact output is updated.'
    }
}
finally {
    if (Test-Path -LiteralPath $stagePath) {
        Remove-Item -LiteralPath $stagePath -Recurse -Force
    }
}

Write-Output $publishPath
