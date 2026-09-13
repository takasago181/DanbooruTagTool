param(
    [Parameter(Mandatory=$true)][string]$Catalog,
    [string]$Output = (Join-Path $PSScriptRoot 'artifacts/portable'),
    [string]$Dotnet = 'dotnet'
)
$ErrorActionPreference = 'Stop'
$catalogPath = (Resolve-Path -LiteralPath $Catalog).Path
$publishPath = [IO.Path]::GetFullPath($Output)
if (Test-Path -LiteralPath $publishPath) { throw 'Output already exists. Choose a new folder to protect UserData.' }
& $Dotnet publish (Join-Path $PSScriptRoot 'DanbooruTagTool.App/DanbooruTagTool.App.csproj') -c Release -r win-x64 --self-contained true -p:PublishSingleFile=false -o $publishPath
if ($LASTEXITCODE -ne 0) { throw 'Portable publish failed' }
New-Item -ItemType Directory -Path (Join-Path $publishPath 'Data'),(Join-Path $publishPath 'UserData') | Out-Null
Copy-Item -LiteralPath $catalogPath -Destination (Join-Path $publishPath 'Data/catalog.db')
Set-Content -LiteralPath (Join-Path $publishPath 'UserData/README.txt') -Value 'user.db is created here on first launch. Copy this folder with the app to carry Prompt and recovery state.'
Write-Output $publishPath
