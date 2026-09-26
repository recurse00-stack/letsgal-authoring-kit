# In-process WPF component tests; not OS mouse automation or live Agent testing.
param([Parameter(Mandatory=$true)][string]$Scratch)
$ErrorActionPreference = 'Stop'
if (-not [IO.Path]::IsPathRooted($Scratch) -or (Test-Path -LiteralPath $Scratch)) { throw 'Use a NEW absolute scratch directory.' }
[void][IO.Directory]::CreateDirectory($Scratch)
$fixtureHome = Join-Path $Scratch "user's home 测试"
[void][IO.Directory]::CreateDirectory($fixtureHome)
$fixtureDsh = Join-Path $Scratch 'dsh data'
[void][IO.Directory]::CreateDirectory($fixtureDsh)
$results = New-Object 'System.Collections.Generic.List[object]'
function Record([string]$Name,[bool]$Passed) {
    $results.Add(@{name=$Name;passed=$Passed})
    if (-not $Passed) { throw "Failed: $Name" }
}
. (Join-Path (Split-Path $PSScriptRoot -Parent) 'Import.ps1') -Harness DSH -Scope User -UserHome $fixtureHome -DshHome $fixtureDsh -PrepareOnly
function Pump {
    $script:frame = New-Object Windows.Threading.DispatcherFrame
    $pumpTimer = New-Object Windows.Threading.DispatcherTimer
    $pumpTimer.Interval = [TimeSpan]::FromMilliseconds(50)
    $pumpTimer.Add_Tick({ $script:frame.Continue = $false })
    $pumpTimer.Start()
    [Windows.Threading.Dispatcher]::PushFrame($script:frame)
    $pumpTimer.Stop()
}
function Capture([string]$Name) {
    $script:window.UpdateLayout()
    $visual = $script:window
    $bitmap = New-Object Windows.Media.Imaging.RenderTargetBitmap([int]$visual.ActualWidth,[int]$visual.ActualHeight,96,96,[Windows.Media.PixelFormats]::Pbgra32)
    $bitmap.Render($visual)
    $encoder = New-Object Windows.Media.Imaging.PngBitmapEncoder
    $encoder.Frames.Add([Windows.Media.Imaging.BitmapFrame]::Create($bitmap))
    $stream = [IO.File]::Create((Join-Path $Scratch $Name))
    try { $encoder.Save($stream) } finally { $stream.Dispose() }
}
function Click-And-Wait($Button) {
    $Button.RaiseEvent((New-Object Windows.RoutedEventArgs([Windows.Controls.Button]::ClickEvent)))
    $until = [DateTime]::UtcNow.AddSeconds(35)
    while ($script:job -and [DateTime]::UtcNow -lt $until) { Pump }
    if ($script:job) { throw 'Backend timeout; child left intact for diagnosis.' }
    Pump
}
try {
    $script:window.Show()
    Pump
    Record 'DSH initial selection and destination' ($script:ui.DestinationText.Text -eq (Join-Path $fixtureDsh 'skills/letsgal-authoring'))
    $expectedNotice = [IO.File]::ReadAllText((Join-Path (Split-Path $PSScriptRoot -Parent) 'skills/letsgal-authoring/references/risk-notice.md'),[Text.Encoding]::UTF8)
    Record 'Risk summary visible before any import' ($script:ui.RiskSummary.IsVisible -and $script:ui.RiskLegal.IsVisible -and $null -eq $script:job)
    $script:ui.RiskExpander.IsExpanded = $true
    Pump
    Record 'Full notice accessible and identical to distributed text' ($script:ui.RiskDetails.IsVisible -and $script:ui.RiskDetails.Text -eq $expectedNotice -and $script:ui.RiskDetails.IsReadOnly)
    Capture 'risk-notice-expanded.png'
    $script:ui.RiskExpander.IsExpanded = $false
    Pump
    Capture 'before-import.png'
    foreach ($choice in @('Codex','Claude','Cursor','Copilot','DSH')) {
        $script:ui.AgentBox.SelectedItem = @($script:ui.AgentBox.Items | Where-Object {$_.Tag -eq $choice})[0]
        Record ("Agent selection " + $choice) ($script:ui.ImportButton.IsEnabled -and $script:ui.ImportButton.Content -like ('*'+$script:ui.AgentBox.SelectedItem.Content))
    }
    $script:ui.ScopeBox.SelectedIndex = 1
    Record 'Missing project disables import' (-not $script:ui.ImportButton.IsEnabled)
    $fixtureProject = Join-Path $Scratch 'project'
    $fixtureNested = Join-Path $fixtureProject 'chapters/nested'
    [void][IO.Directory]::CreateDirectory($fixtureNested)
    [IO.File]::WriteAllText((Join-Path $fixtureProject '.git'),'gitdir: fixture-only')
    $script:ui.ProjectBox.Text = $fixtureNested
    Record 'DSH project preview follows Git root' ($script:ui.DestinationText.Text -eq (Join-Path $fixtureProject '.dsh/skills/letsgal-authoring'))
    $script:ui.ScopeBox.SelectedIndex = 0
    Click-And-Wait $script:ui.ImportButton
    Record 'GUI import launches hidden child and completes' ($script:ui.ResultTitle.Text -eq '导入完成' -and (Test-Path -LiteralPath (Join-Path $fixtureDsh 'skills/letsgal-authoring/SKILL.md')))
    Record 'Success offers correct verification prompt' ($script:ui.CopyButton.Visibility -eq 'Visible' -and $script:prompt.Contains($script:destination.Target))
    Record 'GUI separates actual preference and plugin paths' ($script:ui.ProfileText.Text.Contains((Join-Path $fixtureHome '.letsgal-authoring/preferences/user.md')) -and $script:ui.PluginsText.Text.Contains((Join-Path $fixtureHome '.letsgal-authoring/plugins')))
    Capture 'after-import.png'
    $profile = Join-Path $fixtureHome '.letsgal-authoring/preferences/user.md'
    [IO.File]::WriteAllText($profile,'PRESERVE ME')
    Click-And-Wait $script:ui.ImportButton
    Record 'GUI repeat import retains preferences' ($script:ui.ResultTitle.Text -eq '已经是此包版本' -and [IO.File]::ReadAllText($profile) -eq 'PRESERVE ME')
    Click-And-Wait $script:ui.CheckButton
    Record 'GUI read-only check completes' ($script:ui.ResultTitle.Text -eq '安装文件校验通过')
    $stateFile=Join-Path $fixtureHome '.letsgal-authoring/installer-state.json'
    $stateBefore=[IO.File]::ReadAllText($stateFile)
    $heldState=[IO.File]::Open($stateFile,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read)
    try {
        Click-And-Wait $script:ui.ImportButton
        Record 'GUI shows state-save warning without denying installed result' ($script:ui.ResultTitle.Text -eq '已经是此包版本（有提示）' -and $script:ui.ResultBody.Text.Contains($stateFile) -and $script:ui.CopyButton.Visibility -eq 'Visible')
        Record 'GUI state-save failure preserves previous record' ([IO.File]::ReadAllText($stateFile) -eq $stateBefore)
        Record 'Completion result scrolls into view' ($script:ui.ContentScroll.VerticalOffset -gt 0)
        Capture 'state-save-warning.png'
    } finally { $heldState.Dispose() }
    $skillFile = Join-Path $fixtureDsh 'skills/letsgal-authoring/SKILL.md'
    [IO.File]::AppendAllText($skillFile,"`nLOCAL EDIT")
    Click-And-Wait $script:ui.ImportButton
    Record 'Edited skill shows backup choice without changing files' ($script:ui.BackupButton.Visibility -eq 'Visible' -and [IO.File]::ReadAllText($skillFile).EndsWith('LOCAL EDIT'))
    Capture 'local-edit-protection.png'
    Record 'No hidden child left running' ($null -eq $script:job)
    $report=@{checks=@($results.ToArray());passed=$results.Count;failed=0;scope='In-process WPF events and render; no OS mouse or live Agent acceptance.'}
    [IO.File]::WriteAllText((Join-Path $Scratch 'ui-results.json'),($report | ConvertTo-Json -Depth 6),(New-Object Text.UTF8Encoding($false)))
    $report | ConvertTo-Json -Depth 6
} finally {
    if (-not $script:job) { $script:window.Close() }
}
