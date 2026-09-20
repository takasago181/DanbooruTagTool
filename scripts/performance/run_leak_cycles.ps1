[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)] [string] $RuntimeRoot,
    [Parameter(Mandatory = $true)] [string] $RuntimeLabel,
    [Parameter(Mandatory = $true)] [string] $OutputCsv,
    [Parameter(Mandatory = $true)] [string] $UserDataSeed,
    [int] $Cycles = 10,
    [int] $SettleSeconds = 5
)

$ErrorActionPreference = 'Stop'
$RuntimeRoot = (Resolve-Path -LiteralPath $RuntimeRoot).Path
$protectedRuntimeRoots = @(
    [IO.Path]::GetFullPath('C:\Codex\DanbooruTagTool-App'),
    [IO.Path]::GetFullPath('C:\Codex\DanbooruTagTool\artifacts\current')
)
if ($protectedRuntimeRoots -contains $RuntimeRoot.TrimEnd('\')) { throw 'Performance cycle runner accepts staging runtimes only.' }
$OutputCsv = [IO.Path]::GetFullPath($OutputCsv)
New-Item -ItemType Directory -Path (Split-Path -Parent $OutputCsv) -Force | Out-Null
Copy-Item -LiteralPath $UserDataSeed -Destination (Join-Path $RuntimeRoot 'UserData/user.db') -Force

Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
Add-Type -TypeDefinition @'
using System;
using System.Runtime.InteropServices;
public static class LeakCycleNative {
    [DllImport("user32.dll")] public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int x, int y);
    [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extraInfo);
    [DllImport("kernel32.dll")] public static extern bool GetProcessIoCounters(IntPtr processHandle, out IoCounters counters);
    [StructLayout(LayoutKind.Sequential)] public struct IoCounters { public ulong ReadOperationCount; public ulong WriteOperationCount; public ulong OtherOperationCount; public ulong ReadTransferCount; public ulong WriteTransferCount; public ulong OtherTransferCount; }
    [DllImport("user32.dll")] public static extern uint GetGuiResources(IntPtr processHandle, uint flags);
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
function Click-Element($Element) {
    $rect = $Element.Current.BoundingRectangle
    [LeakCycleNative]::SetCursorPos([int]($rect.Left + $rect.Width / 2), [int]($rect.Top + $rect.Height / 2)) | Out-Null
    [LeakCycleNative]::mouse_event(2, 0, 0, 0, [UIntPtr]::Zero)
    [LeakCycleNative]::mouse_event(4, 0, 0, 0, [UIntPtr]::Zero)
}
function Invoke-Button([string] $Name) {
    Refresh-Window; $element = Find-Element $Name ([System.Windows.Automation.ControlType]::Button)
    if ($null -eq $element) { return $false }
    try { $element.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep -Milliseconds 180; return $true } catch {}
    try { $element.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern).Toggle(); Start-Sleep -Milliseconds 180; return $true } catch {}
    try { Click-Element $element; Start-Sleep -Milliseconds 180; return $true } catch { return $false }
}
function Set-Search([string] $Value) {
    Refresh-Window; $element = Find-Element '日本語・English・混在検索' ([System.Windows.Automation.ControlType]::Edit)
    if ($null -eq $element) { return $false }
    try { $element.GetCurrentPattern([System.Windows.Automation.ValuePattern]::Pattern).SetValue($Value); Start-Sleep -Milliseconds 250; return $true } catch { return $false }
}
function Select-Tree([string] $Name) {
    Refresh-Window; $element = Find-Element $Name ([System.Windows.Automation.ControlType]::TreeItem)
    if ($null -eq $element) { $text = Find-Element $Name ([System.Windows.Automation.ControlType]::Text); if ($null -ne $text) { $element = [System.Windows.Automation.TreeWalker]::RawViewWalker.GetParent($text) } }
    if ($null -eq $element) { return $false }
    try { $element.GetCurrentPattern([System.Windows.Automation.SelectionItemPattern]::Pattern).Select(); Start-Sleep -Milliseconds 220; return $true } catch {}
    try { $element.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep -Milliseconds 220; return $true } catch { return $false }
}
function Add-RemovePrompt {
    Refresh-Window; $add = @(All-Elements | Where-Object { $_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button -and $_.Current.Name -eq '＋' })
    if ($add.Count -gt 0) { try { $add[0].GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep -Milliseconds 180 } catch { Click-Element $add[0] } }
    Refresh-Window; $remove = @(All-Elements | Where-Object { $_.Current.ControlType -eq [System.Windows.Automation.ControlType]::Button -and $_.Current.Name -eq '×' })
    if ($remove.Count -gt 0) { try { $remove[0].GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern).Invoke(); Start-Sleep -Milliseconds 180 } catch { Click-Element $remove[0] } }
}
function Read-Metrics([int] $Cycle, [double] $Elapsed, [double] $PreviousCpu, [double] $PreviousRead, [double] $PreviousWrite, [DateTime] $PreviousTime) {
    $p = Get-Process -Id $script:process.Id
    $p.Refresh(); $now = [DateTime]::UtcNow; $wall = ($now - $PreviousTime).TotalSeconds
    $io = New-Object LeakCycleNative+IoCounters
    [LeakCycleNative]::GetProcessIoCounters($p.Handle, [ref]$io) | Out-Null
    $cpu = $p.TotalProcessorTime.TotalSeconds
    $row = [pscustomobject]@{
        Runtime = $RuntimeLabel; Cycle = $Cycle; TimestampUtc = $now.ToString('o'); ElapsedSec = [math]::Round($Elapsed, 3)
        CpuPct = [math]::Round((($cpu - $PreviousCpu) / [math]::Max(.001, $wall) / [Environment]::ProcessorCount) * 100, 4)
        PrivateMemoryMB = [math]::Round($p.PrivateMemorySize64 / 1MB, 3); WorkingSetMB = [math]::Round($p.WorkingSet64 / 1MB, 3)
        ThreadCount = $p.Threads.Count; HandleCount = $p.HandleCount
        GdiObjects = [LeakCycleNative]::GetGuiResources($p.Handle, 0); UserObjects = [LeakCycleNative]::GetGuiResources($p.Handle, 1)
        DiskReadBytesPerSec = [math]::Round(($io.ReadTransferCount - $PreviousRead) / [math]::Max(.001, $wall), 3)
        DiskWriteBytesPerSec = [math]::Round(($io.WriteTransferCount - $PreviousWrite) / [math]::Max(.001, $wall), 3)
    }
    return [pscustomobject]@{ Row = $row; Cpu = $cpu; Read = [double]$io.ReadTransferCount; Write = [double]$io.WriteTransferCount; Time = $now }
}

$script:process = Start-Process -FilePath (Join-Path $RuntimeRoot 'DanbooruTagTool.exe') -WorkingDirectory $RuntimeRoot -PassThru
for ($i = 0; $i -lt 80 -and $script:process.MainWindowHandle -eq 0; $i++) { Start-Sleep -Milliseconds 250; $script:process.Refresh() }
if ($script:process.MainWindowHandle -eq 0) { throw 'WPF window did not appear.' }
[LeakCycleNative]::ShowWindowAsync($script:process.MainWindowHandle, 3) | Out-Null
Refresh-Window

$start = [DateTime]::UtcNow
$p = Get-Process -Id $script:process.Id; $p.Refresh(); $previousCpu = $p.TotalProcessorTime.TotalSeconds
$io = New-Object LeakCycleNative+IoCounters; [LeakCycleNative]::GetProcessIoCounters($p.Handle, [ref]$io) | Out-Null
$previousRead = [double]$io.ReadTransferCount; $previousWrite = [double]$io.WriteTransferCount; $previousTime = [DateTime]::UtcNow

for ($cycle = 1; $cycle -le $Cycles; $cycle++) {
    Set-Search '肛門' | Out-Null; Set-Search 'anal' | Out-Null; Set-Search '肛門 anal' | Out-Null
    Invoke-Button 'クリア' | Out-Null
    Select-Tree '身体・部位' | Out-Null
    Invoke-Button '男性器' | Out-Null; Invoke-Button '男性器' | Out-Null
    Invoke-Button '拘束・BDSM' | Out-Null; Invoke-Button '拘束・BDSM' | Out-Null
    Invoke-Button '性的' | Out-Null; Invoke-Button '一般向け' | Out-Null; Invoke-Button 'すべて' | Out-Null
    Invoke-Button '◆ 深掘りのみ' | Out-Null; Invoke-Button '◆ 深掘りのみ' | Out-Null
    Set-Search 'anal' | Out-Null; Add-RemovePrompt
    Start-Sleep -Seconds $SettleSeconds
    $sample = Read-Metrics $cycle ([DateTime]::UtcNow.Subtract($start).TotalSeconds) $previousCpu $previousRead $previousWrite $previousTime
    if (-not (Test-Path -LiteralPath $OutputCsv)) { $sample.Row | Export-Csv -LiteralPath $OutputCsv -NoTypeInformation -Encoding utf8 } else { $sample.Row | Export-Csv -LiteralPath $OutputCsv -NoTypeInformation -Append -Encoding utf8 }
    $previousCpu = $sample.Cpu; $previousRead = $sample.Read; $previousWrite = $sample.Write; $previousTime = $sample.Time
}

try { $script:process.CloseMainWindow() | Out-Null; Start-Sleep -Seconds 2 } catch {}
if (-not $script:process.HasExited) { Stop-Process -Id $script:process.Id -Force }
