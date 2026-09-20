[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $RuntimeRoot,
    [Parameter(Mandatory = $true)] [string] $OutputJson,
    [Parameter(Mandatory = $true)] [string] $UserDataSeed
)

$ErrorActionPreference = 'Stop'
$resolvedRuntimeRoot = (Resolve-Path -LiteralPath $RuntimeRoot).Path
$protectedRuntimeRoots = @(
    [IO.Path]::GetFullPath('C:\Codex\DanbooruTagTool-App'),
    [IO.Path]::GetFullPath('C:\Codex\DanbooruTagTool\artifacts\current')
)
if ($protectedRuntimeRoots -contains $resolvedRuntimeRoot.TrimEnd('\')) { throw 'Targeted smoke accepts staging runtimes only.' }
Copy-Item -LiteralPath $UserDataSeed -Destination (Join-Path $RuntimeRoot 'UserData/user.db') -Force
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class TargetedSmokeNative {
    [DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);
}
'@

function Refresh-Window { $script:window = [System.Windows.Automation.AutomationElement]::FromHandle($script:process.MainWindowHandle) }
function All-Elements { $script:window.FindAll([System.Windows.Automation.TreeScope]::Descendants, [System.Windows.Automation.Condition]::TrueCondition) }
function Find-Element([string] $Name, [System.Windows.Automation.ControlType] $Type) {
    $condition = New-Object System.Windows.Automation.AndCondition(
        (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty, $Name)),
        (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty, $Type)))
    return $script:window.FindFirst([System.Windows.Automation.TreeScope]::Descendants, $condition)
}
function Invoke-Name([string] $Name) {
    Refresh-Window
    $element = @(All-Elements | Where-Object { $_.Current.Name -eq $Name -and $_.Current.IsEnabled -and $_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button }) | Select-Object -First 1
    if ($null -eq $element) { $element = Find-Element $Name ([System.Windows.Automation.ControlType]::TabItem) }
    if ($null -eq $element) { return $false }
    try { $element.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep -Milliseconds 350; return $true } catch {}
    try { $element.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern).Toggle(); Start-Sleep -Milliseconds 350; return $true } catch {}
    try { $element.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern).Select(); Start-Sleep -Milliseconds 350; return $true } catch { return $false }
}
function Set-Search([string] $Value) {
    Refresh-Window; $element = Find-Element '日本語・English・混在検索' ([System.Windows.Automation.ControlType]::Edit)
    if ($null -eq $element) { return $false }
    try { $element.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).SetValue($Value); Start-Sleep -Milliseconds 400; return $true } catch { return $false }
}

$results = [System.Collections.Generic.List[object]]::new()
function Check([string] $Name, [bool] $Pass, [string] $Detail) { $results.Add([pscustomobject]@{Name=$Name;Pass=$Pass;Detail=$Detail}) }

$script:process = Start-Process -FilePath (Join-Path $RuntimeRoot 'DanbooruTagTool.exe') -WorkingDirectory $RuntimeRoot -PassThru
for ($i = 0; $i -lt 80 -and $script:process.MainWindowHandle -eq 0; $i++) { Start-Sleep -Milliseconds 250; $script:process.Refresh() }
if ($script:process.MainWindowHandle -eq 0) { throw 'WPF window did not appear.' }
[TargetedSmokeNative]::ShowWindowAsync($script:process.MainWindowHandle, 3) | Out-Null
Refresh-Window
Check 'launch' ($null -ne $script:window) 'window-visible'
$allNames = @(All-Elements | ForEach-Object { $_.Current.Name })
Check 'detail-ui-removed' (-not ($allNames -contains 'タグ詳細') -and -not ($allNames -contains '関連タグ')) 'no-detail-or-related-label'
Check 'Japanese-search' (Set-Search '肛門') 'input accepted'
Check 'English-search' (Set-Search 'anal') 'input accepted'
Check 'mixed-search' (Set-Search '肛門 anal') 'input accepted'
Check 'clear' (Invoke-Name 'クリア') 'invoked'
Set-Search 'anal' | Out-Null
Check 'prompt-add' (Invoke-Name '＋') 'invoked'
Check 'undo' (Invoke-Name '元に戻す') 'invoked'
Check 'redo' (Invoke-Name 'やり直す') 'invoked'
Check 'open-prompt-editor' (Invoke-Name 'Prompt編集を開く') 'invoked'
Check 'dictionary-tab' (Invoke-Name '辞書・検索') 'invoked'
Check 'english-copy' ((Invoke-Name '英語Promptをコピー') -or (Invoke-Name '英語Promptをコピー')) 'invoked'

$results | ConvertTo-Json -Depth 4 | Set-Content -LiteralPath $OutputJson -Encoding utf8
try { $script:process.CloseMainWindow() | Out-Null; Start-Sleep -Seconds 2 } catch {}
if (-not $script:process.HasExited) { Stop-Process -Id $script:process.Id -Force }
if (@($results | Where-Object { -not $_.Pass }).Count -gt 0) { exit 1 }
