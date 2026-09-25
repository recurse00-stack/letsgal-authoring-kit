param([Parameter(Mandatory=$true)][string]$Scratch)
$ErrorActionPreference='Stop'
if (-not [IO.Path]::IsPathRooted($Scratch) -or (Test-Path -LiteralPath $Scratch)) { throw 'Use a new absolute scratch directory.' }
[void][IO.Directory]::CreateDirectory($Scratch)
$kitRoot=Split-Path $PSScriptRoot -Parent
. (Join-Path $kitRoot 'Import.Paths.ps1')
$items=New-Object 'System.Collections.Generic.List[object]'
function Record([string]$Name,[bool]$Passed) { $items.Add(@{name=$Name;passed=$Passed}); if(-not $Passed){throw "Failed: $Name"} }
foreach($path in @('relative','C:relative','\relative','\\?\device','\\.\device')) {
    $rejected=$false
    try { [void](Full-Path $path) } catch { $rejected=$true }
    Record 'ambiguous or device path rejected' $rejected
}
$fixtureHome=Join-Path $Scratch 'home'
[void][IO.Directory]::CreateDirectory($fixtureHome)
$exe=Join-Path $PSHOME $(if($PSVersionTable.PSEdition -eq 'Core'){'pwsh.exe'}else{'powershell.exe'})
$backend=Join-Path $kitRoot 'Install.ps1'
$installArgs=@('-NoProfile','-ExecutionPolicy','Bypass','-File',$backend,'-Harness','Codex','-Scope','User','-UserHome',$fixtureHome,'-NonInteractive')
$output=& $exe @installArgs
Record 'initial fixture install' ($LASTEXITCODE -eq 0)
$targetFile=Join-Path $fixtureHome '.agents/skills/letsgal-authoring/SKILL.md'
$original=[IO.File]::ReadAllBytes($targetFile)
$lockFile=Join-Path $fixtureHome '.agents/.letsgal-authoring-backups/installer.lock'
$held=[IO.File]::Open($lockFile,[IO.FileMode]::Open,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None)
try {
    $output=& $exe @installArgs
    Record 'concurrent installer refuses target while lock held' ($LASTEXITCODE -ne 0 -and ($output -join "`n").Contains('Another installer'))
    Record 'concurrent attempt preserves installed bytes' ([Convert]::ToBase64String([IO.File]::ReadAllBytes($targetFile)) -eq [Convert]::ToBase64String($original))
} finally {$held.Dispose()}
$output=& $exe @installArgs
Record 'released lock permits next import' ($LASTEXITCODE -eq 0)
$badHome=Join-Path $Scratch 'bad-profile-home'
[void][IO.Directory]::CreateDirectory((Join-Path $badHome '.letsgal-authoring/user.md'))
$output=& $exe -NoProfile -ExecutionPolicy Bypass -File $backend -Harness Codex -Scope User -UserHome $badHome -NonInteractive
Record 'directory masquerading as profile is rejected before install' ($LASTEXITCODE -ne 0 -and -not (Test-Path -LiteralPath (Join-Path $badHome '.agents/skills/letsgal-authoring')))
# Reproduce a real hard-link alias: writing remembered choices must not alter the other file.
$linkedHome=Join-Path $Scratch 'hardlink-home'
$linkedArea=Join-Path $linkedHome '.letsgal-authoring'
[void][IO.Directory]::CreateDirectory($linkedArea)
$otherFile=Join-Path $Scratch 'other-user-file.json'
$originalChoices='{"Harness":"Claude","Scope":"User"}'
[IO.File]::WriteAllText($otherFile,$originalChoices)
$linkedState=Join-Path $linkedArea 'installer-state.json'
[void](New-Item -ItemType HardLink -Path $linkedState -Target $otherFile)
$output=& $exe -NoProfile -ExecutionPolicy Bypass -File $backend -Harness Codex -Scope User -UserHome $linkedHome -NonInteractive
Record 'state replacement preserves external hard-linked user file' ($LASTEXITCODE -eq 0 -and [IO.File]::ReadAllText($otherFile) -eq $originalChoices -and (Read-InstallerChoices $linkedState).Harness -eq 'Codex')

$lockedHome=Join-Path $Scratch 'state-locked-home'
$lockedArea=Join-Path $lockedHome '.letsgal-authoring'
[void][IO.Directory]::CreateDirectory($lockedArea)
$lockedState=Join-Path $lockedArea 'installer-state.json'
[IO.File]::WriteAllText($lockedState,$originalChoices)
$heldState=[IO.File]::Open($lockedState,[IO.FileMode]::Open,[IO.FileAccess]::Read,[IO.FileShare]::Read)
try {
    $output=& $exe -NoProfile -ExecutionPolicy Bypass -File $backend -Harness Codex -Scope User -UserHome $lockedHome -NonInteractive
    $reportLine=@($output | Where-Object { $_.StartsWith('{') })[-1] | ConvertFrom-Json
    Record 'locked state reports completed install with separate warning' ($LASTEXITCODE -eq 0 -and $reportLine.action -eq 'installed' -and @($reportLine.completion_warnings).Count -eq 1)
    Record 'locked state retains original record and valid installed skill' ([IO.File]::ReadAllText($lockedState) -eq $originalChoices -and (Test-Path -LiteralPath (Join-Path $lockedHome '.agents/skills/letsgal-authoring/SKILL.md')))
    $output=& $exe -NoProfile -ExecutionPolicy Bypass -File $backend -Harness Codex -Scope User -UserHome $lockedHome -NonInteractive
    $reportLine=@($output | Where-Object { $_.StartsWith('{') })[-1] | ConvertFrom-Json
    Record 'repeat import separates state warning from installation result' ($LASTEXITCODE -eq 0 -and $reportLine.action -eq 'already_current' -and @($reportLine.completion_warnings).Count -eq 1)
} finally { $heldState.Dispose() }
$output=& $exe -NoProfile -ExecutionPolicy Bypass -File $backend -Harness Codex -Scope User -UserHome $lockedHome -NonInteractive
$reportLine=@($output | Where-Object { $_.StartsWith('{') })[-1] | ConvertFrom-Json
Record 'released state lock permits atomic save without stale temp files' ($LASTEXITCODE -eq 0 -and @($reportLine.completion_warnings).Count -eq 0 -and (Read-InstallerChoices $lockedState).Harness -eq 'Codex' -and @(Get-ChildItem -LiteralPath $lockedArea -Filter '*.tmp').Count -eq 0)
[IO.File]::WriteAllText($lockedState,'{"Harness":"Unknown","Scope":false,"ProjectPath":{"bad":"value"}}')
Set-StrictMode -Version 2.0
try {
    $choices=Read-InstallerChoices $lockedState
    Record 'incomplete or invalid saved choices remain safe under strict mode' ($null -eq $choices.Harness -and $null -eq $choices.Scope -and $null -eq $choices.ProjectPath -and $null -eq $choices.DshHome)
} finally { Set-StrictMode -Off }
# Construct the actual GUI with a stale DSH path; users of another Agent must still get a usable window.
. (Join-Path $kitRoot 'Import.ps1') -Harness Codex -Scope User -UserHome $fixtureHome -DshHome 'relative-dsh' -PrepareOnly
try { Record 'invalid DSH path does not prevent Codex GUI startup' ($script:ui.ImportButton.IsEnabled -and $script:ui.DestinationText.Text.EndsWith('letsgal-authoring')) }
finally { $script:window.Close() }
$report=@{checks=@($items.ToArray());passed=$items.Count;failed=0;scope='Isolated path, real cross-process locking and GUI startup regression tests.'}
[IO.File]::WriteAllText((Join-Path $Scratch 'safety-results.json'),($report|ConvertTo-Json -Depth 6),(New-Object Text.UTF8Encoding($false)))
$report|ConvertTo-Json -Depth 6
