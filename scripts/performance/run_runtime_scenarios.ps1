[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $RuntimeRoot,
    [Parameter(Mandatory = $true)] [string] $RuntimeLabel,
    [Parameter(Mandatory = $true)] [string] $OutputRoot,
    [Parameter(Mandatory = $true)] [string] $UserDataSeed,
    [int] $ScenarioSeconds = 12
)

$ErrorActionPreference = 'Stop'
$RuntimeRoot = (Resolve-Path -LiteralPath $RuntimeRoot).Path
$OutputRoot = [IO.Path]::GetFullPath($OutputRoot)
New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
$processCollector = Join-Path $PSScriptRoot 'collect_process_metrics.ps1'
$gpuCollector = Join-Path $PSScriptRoot 'collect_gpu_metrics.ps1'
$pwsh = (Get-Command pwsh -ErrorAction Stop).Source
$logPath = Join-Path $OutputRoot "$RuntimeLabel-actions.jsonl"

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class RuntimeScenarioNative {
    [DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool SetWindowPos(IntPtr hWnd, IntPtr after, int x, int y, int cx, int cy, uint flags);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extraInfo);
}
'@

function Log([string] $Scenario, [string] $Action, [string] $Result) {
    [pscustomobject]@{timestamp_utc=(Get-Date).ToUniversalTime().ToString('o');runtime=$RuntimeLabel;scenario=$Scenario;action=$Action;result=$Result} |
        ConvertTo-Json -Compress | Add-Content -LiteralPath $logPath -Encoding utf8
}

function Refresh-Window {
    $script:window = $script:process.MainWindowHandle | ForEach-Object { [System.Windows.Automation.AutomationElement]::FromHandle($_) }
    if ($null -eq $script:window) { throw 'WPF window is not available.' }
}

function All-Elements { return $script:window.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition) }

function Find-Element([string] $Name, [System.Windows.Automation.ControlType] $Type) {
    $condition = New-Object System.Windows.Automation.AndCondition(
        (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::NameProperty,$Name)),
        (New-Object System.Windows.Automation.PropertyCondition([System.Windows.Automation.AutomationElement]::ControlTypeProperty,$Type)))
    return $script:window.FindFirst([System.Windows.Automation.TreeScope]::Descendants,$condition)
}

function Click-Element($Element) {
    $rect = $Element.Current.BoundingRectangle
    [RuntimeScenarioNative]::SetCursorPos([int]($rect.Left + ($rect.Width / 2)), [int]($rect.Top + ($rect.Height / 2))) | Out-Null
    [RuntimeScenarioNative]::mouse_event(0x0002,0,0,0,[UIntPtr]::Zero)
    [RuntimeScenarioNative]::mouse_event(0x0004,0,0,0,[UIntPtr]::Zero)
}

function Invoke-Button([string] $Scenario, [string] $Name) {
    Refresh-Window
    $element = Find-Element $Name ([System.Windows.Automation.ControlType]::Button)
    if ($null -eq $element) { Log $Scenario "button:$Name" 'missing'; return $false }
    try { $element.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep -Milliseconds 350; Log $Scenario "button:$Name" 'invoked'; return $true }
    catch {
        try { $pattern = $element.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern); $pattern.Toggle(); Start-Sleep -Milliseconds 350; Log $Scenario "button:$Name" "toggled:$($pattern.Current.ToggleState)"; return $true }
        catch {
            try { Click-Element $element; Start-Sleep -Milliseconds 350; Log $Scenario "button:$Name" 'mouse-clicked'; return $true }
            catch { Log $Scenario "button:$Name" "failed:$($_.Exception.Message)"; return $false }
        }
    }
}

function Toggle-Button([string] $Scenario, [string] $Name) {
    Refresh-Window
    $element = Find-Element $Name ([System.Windows.Automation.ControlType]::Button)
    if ($null -eq $element) { Log $Scenario "toggle:$Name" 'missing'; return $null }
    try {
        $pattern = $element.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern)
        $pattern.Toggle(); Start-Sleep -Milliseconds 350
        $state = $pattern.Current.ToggleState.ToString(); Log $Scenario "toggle:$Name" $state; return $state
    } catch { Log $Scenario "toggle:$Name" "failed:$($_.Exception.Message)"; return $null }
}

function Set-Edit([string] $Scenario, [string] $Name, [string] $Value) {
    Refresh-Window
    $element = Find-Element $Name ([System.Windows.Automation.ControlType]::Edit)
    if ($null -eq $element) { Log $Scenario "edit:$Name" 'missing'; return $false }
    try { $element.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).SetValue($Value); Start-Sleep -Milliseconds 500; Log $Scenario "edit:$Name" "set:$Value"; return $true }
    catch { Log $Scenario "edit:$Name" "failed:$($_.Exception.Message)"; return $false }
}

function Select-TreeItem([string] $Scenario, [string] $Name) {
    Refresh-Window
    $element = Find-Element $Name ([System.Windows.Automation.ControlType]::TreeItem)
    if ($null -eq $element) {
        $element = Find-Element $Name ([System.Windows.Automation.ControlType]::Text)
        if ($null -ne $element) { $element = [System.Windows.Automation.TreeWalker]::RawViewWalker.GetParent($element) }
    }
    if ($null -eq $element) { Log $Scenario "tree:$Name" 'missing'; return $false }
    try {
        try { $element.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern).Select() }
        catch { $element.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke() }
        Start-Sleep -Milliseconds 500; Log $Scenario "tree:$Name" 'selected'; return $true
    }
    catch { Log $Scenario "tree:$Name" "failed:$($_.Exception.Message)"; return $false }
}

function Reset-DictionaryFilters([string] $Scenario) {
    Invoke-Button $Scenario 'クリア' | Out-Null
    Invoke-Button $Scenario '全解除' | Out-Null
}

function Scroll-Results([string] $Scenario) {
    Refresh-Window
    $lists = @(All-Elements | Where-Object { $_.Current.ControlType -eq [System.Windows.Automation.ControlType]::List })
    $used = $false
    foreach ($list in $lists) {
        try {
            $pattern = $list.GetCurrentPattern([System.Windows.Automation.ScrollPattern]::Pattern)
            1..4 | ForEach-Object { $pattern.ScrollVertical([System.Windows.Automation.ScrollAmount]::LargeIncrement); Start-Sleep -Milliseconds 150 }
            1..4 | ForEach-Object { $pattern.ScrollVertical([System.Windows.Automation.ScrollAmount]::SmallDecrement); Start-Sleep -Milliseconds 150 }
            $used = $true; break
        } catch {}
    }
    Log $Scenario 'result-scroll' $(if($used){'scrolled'}else{'no-scroll-pattern'})
}

function Add-PromptItems([string] $Scenario, [int] $Count) {
    1..$Count | ForEach-Object {
        Refresh-Window
        $buttons = @(All-Elements | Where-Object { $_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button -and $_.Current.Name -eq '＋' })
        if ($buttons.Count -eq 0) { Log $Scenario 'prompt-add' 'missing'; return }
        try { $buttons[0].GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep -Milliseconds 250; Log $Scenario 'prompt-add' 'invoked' } catch { Log $Scenario 'prompt-add' "failed:$($_.Exception.Message)" }
    }
}

function Remove-PromptItems([string] $Scenario, [int] $Count) {
    1..$Count | ForEach-Object {
        Refresh-Window
        $buttons = @(All-Elements | Where-Object { $_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button -and $_.Current.Name -eq '×' })
        if ($buttons.Count -eq 0) { Log $Scenario 'prompt-remove' 'missing'; return }
        try { $buttons[0].GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep -Milliseconds 250; Log $Scenario 'prompt-remove' 'invoked' } catch { Log $Scenario 'prompt-remove' "failed:$($_.Exception.Message)" }
    }
}

function Select-PromptRow([string] $Scenario) {
    Refresh-Window
    $rows = @(All-Elements | Where-Object { $_.Current.ControlType -eq [System.Windows.Automation.ControlType]::DataItem })
    if ($rows.Count -eq 0) { Log $Scenario 'prompt-select' 'missing'; return $false }
    try {
        try { $rows[0].GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern).Select() }
        catch {
            Click-Element $rows[0]
        }
        Start-Sleep -Milliseconds 350; Log $Scenario 'prompt-select' 'selected'; return $true
    }
    catch { Log $Scenario 'prompt-select' "failed:$($_.Exception.Message)"; return $false }
}

function Start-Metrics([string] $Scenario, [int] $Seconds) {
    $processCsv = Join-Path $OutputRoot "$RuntimeLabel-$Scenario-process.csv"
    $gpuCsv = Join-Path $OutputRoot "$RuntimeLabel-$Scenario-gpu.csv"
    $metric = Start-Process -FilePath $pwsh -ArgumentList @('-NoProfile','-File',$processCollector,'-ProcessId',$script:process.Id,'-OutputCsv',$processCsv,'-RuntimeLabel',$RuntimeLabel,'-Scenario',$Scenario,'-Seconds',$Seconds,'-IntervalMs','1000') -PassThru
    $gpu = Start-Process -FilePath $pwsh -ArgumentList @('-NoProfile','-File',$gpuCollector,'-TargetProcessId',$script:process.Id,'-OutputCsv',$gpuCsv,'-RuntimeLabel',$RuntimeLabel,'-Scenario',$Scenario,'-Seconds',$Seconds,'-IntervalSeconds','5') -PassThru
    return [pscustomobject]@{Metric=$metric;Gpu=$gpu;Seconds=$Seconds}
}

function Stop-Metrics($handles) {
    Wait-Process -Id $handles.Metric.Id -Timeout ($handles.Seconds + 30) -ErrorAction SilentlyContinue
    Wait-Process -Id $handles.Gpu.Id -Timeout ($handles.Seconds + 60) -ErrorAction SilentlyContinue
}

function Measure-Scenario([string] $Name, [int] $Seconds, [scriptblock] $Action) {
    $handles = Start-Metrics $Name $Seconds
    $start = [Diagnostics.Stopwatch]::StartNew()
    & $Action
    $remaining = $Seconds - [math]::Ceiling($start.Elapsed.TotalSeconds)
    if ($remaining -gt 0) { Start-Sleep -Seconds $remaining }
    Stop-Metrics $handles
}

Copy-Item -LiteralPath $UserDataSeed -Destination (Join-Path $RuntimeRoot 'UserData/user.db') -Force
$script:process = Start-Process -FilePath (Join-Path $RuntimeRoot 'DanbooruTagTool.exe') -WorkingDirectory $RuntimeRoot -PassThru
$s1 = Start-Metrics 'S1-launch' 30
for ($i=0; $i -lt 80 -and $script:process.MainWindowHandle -eq 0; $i++) { Start-Sleep -Milliseconds 250; $script:process.Refresh() }
Refresh-Window
[RuntimeScenarioNative]::ShowWindowAsync($script:process.MainWindowHandle, 3) | Out-Null
try {
    $dictionaryTab = Find-Element '辞書・検索' ([System.Windows.Automation.ControlType]::TabItem)
    $dictionaryTab.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern).Select()
    Start-Sleep -Milliseconds 500
} catch { Log 'S1-launch' 'dictionary-tab' 'not-selected' }
Log 'S1-launch' 'startup' 'window-visible'
Start-Sleep -Seconds 30
Stop-Metrics $s1

Measure-Scenario 'S2-idle' 60 { Log 'S2-idle' 'idle' 'no-input' }
Measure-Scenario 'S3-scroll' $ScenarioSeconds { Set-Edit 'S3-scroll' '日本語・English・混在検索' ''; Scroll-Results 'S3-scroll' }
Measure-Scenario 'S4-japanese-input' $ScenarioSeconds { Set-Edit 'S4-japanese-input' '日本語・English・混在検索' '肛門'; Set-Edit 'S4-japanese-input' '日本語・English・混在検索' '肛門周辺'; Set-Edit 'S4-japanese-input' '日本語・English・混在検索' '肛門周辺の毛' }
Measure-Scenario 'S5-english-input' $ScenarioSeconds { Set-Edit 'S5-english-input' '日本語・English・混在検索' 'anal'; Set-Edit 'S5-english-input' '日本語・English・混在検索' 'anal_hair'; Set-Edit 'S5-english-input' '日本語・English・混在検索' 'covered_nipples' }
Measure-Scenario 'S6-mixed-input' $ScenarioSeconds { Set-Edit 'S6-mixed-input' '日本語・English・混在検索' '肛門 anal'; Set-Edit 'S6-mixed-input' '日本語・English・混在検索' '胸 breast'; Set-Edit 'S6-mixed-input' '日本語・English・混在検索' '乳房 breast' }
Measure-Scenario 'S7-category-switch' $ScenarioSeconds { Reset-DictionaryFilters 'S7-category-switch'; Select-TreeItem 'S7-category-switch' '身体・部位'; Select-TreeItem 'S7-category-switch' '髪・顔'; Select-TreeItem 'S7-category-switch' '構図・画角'; Select-TreeItem 'S7-category-switch' '身体・部位' }
Measure-Scenario 'S8-body-filter' $ScenarioSeconds { Reset-DictionaryFilters 'S8-body-filter'; Invoke-Button 'S8-body-filter' '男性器'; Reset-DictionaryFilters 'S8-body-filter'; Invoke-Button 'S8-body-filter' '乳房・乳首'; Reset-DictionaryFilters 'S8-body-filter'; Invoke-Button 'S8-body-filter' '男性器' }
Measure-Scenario 'S9-theme-filter' $ScenarioSeconds { Reset-DictionaryFilters 'S9-theme-filter'; Invoke-Button 'S9-theme-filter' '拘束・BDSM'; Reset-DictionaryFilters 'S9-theme-filter'; Invoke-Button 'S9-theme-filter' '損傷・R18G'; Reset-DictionaryFilters 'S9-theme-filter'; Invoke-Button 'S9-theme-filter' '拘束・BDSM' }
Measure-Scenario 'S10-content-filter' $ScenarioSeconds { Reset-DictionaryFilters 'S10-content-filter'; Toggle-Button 'S10-content-filter' 'すべて'; Reset-DictionaryFilters 'S10-content-filter'; Toggle-Button 'S10-content-filter' '一般向け'; Reset-DictionaryFilters 'S10-content-filter'; Toggle-Button 'S10-content-filter' '性的'; Reset-DictionaryFilters 'S10-content-filter'; Toggle-Button 'S10-content-filter' 'すべて' }
Measure-Scenario 'S11-deep-only' $ScenarioSeconds { Toggle-Button 'S11-deep-only' '◆ 深掘りのみ'; Toggle-Button 'S11-deep-only' '◆ 深掘りのみ'; Toggle-Button 'S11-deep-only' '◆ 深掘りのみ'; Toggle-Button 'S11-deep-only' '◆ 深掘りのみ' }
Measure-Scenario 'S12-prompt-add-remove' $ScenarioSeconds { Set-Edit 'S12-prompt-add-remove' '日本語・English・混在検索' 'anal'; Add-PromptItems 'S12-prompt-add-remove' 4; Remove-PromptItems 'S12-prompt-add-remove' 4 }
Measure-Scenario 'S13-prompt-reorder' $ScenarioSeconds { Set-Edit 'S13-prompt-reorder' '日本語・English・混在検索' 'anal'; Add-PromptItems 'S13-prompt-reorder' 2; Invoke-Button 'S13-prompt-reorder' 'Prompt編集を開く'; Select-PromptRow 'S13-prompt-reorder'; Invoke-Button 'S13-prompt-reorder' '↑'; Invoke-Button 'S13-prompt-reorder' '↓'; Invoke-Button 'S13-prompt-reorder' '↑'; Invoke-Button 'S13-prompt-reorder' '↓' }
Measure-Scenario 'S14-category-display' $ScenarioSeconds { Toggle-Button 'S14-category-display' '並び順表示'; Toggle-Button 'S14-category-display' 'カテゴリ別表示' }
Measure-Scenario 'S15-display-toggle' $ScenarioSeconds { Toggle-Button 'S15-display-toggle' '並び順表示'; Toggle-Button 'S15-display-toggle' 'カテゴリ別表示'; Toggle-Button 'S15-display-toggle' '並び順表示'; Toggle-Button 'S15-display-toggle' 'カテゴリ別表示' }
Measure-Scenario 'S16-prompt-search' $ScenarioSeconds { Set-Edit 'S16-prompt-search' 'Prompt内検索' 'anal'; Set-Edit 'S16-prompt-search' 'Prompt内検索' 'breast'; Set-Edit 'S16-prompt-search' 'Prompt内検索' '' }
Measure-Scenario 'S17-resize' $ScenarioSeconds {
    1..5 | ForEach-Object {
        $size = if ($_ % 2 -eq 0) { @(1280,780) } else { @(1600,950) }
        [RuntimeScenarioNative]::ShowWindowAsync($script:process.MainWindowHandle, 9) | Out-Null
        [RuntimeScenarioNative]::SetWindowPos($script:process.MainWindowHandle,[IntPtr]::Zero,80,80,$size[0],$size[1],0x0040) | Out-Null
        Start-Sleep -Milliseconds 300
    }
    Log 'S17-resize' 'window-resize' '5-cycles'
}
Measure-Scenario 'S18-post-operation-idle' 120 { Log 'S18-post-operation-idle' 'idle' 'no-input-120s' }

try { $script:process.CloseMainWindow() | Out-Null; Start-Sleep -Seconds 2 } catch {}
if (-not $script:process.HasExited) { Stop-Process -Id $script:process.Id -Force }
Log 'complete' 'process-exit' 'stopped'
