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
# Construct the actual GUI with a stale DSH path; users of another Agent must still get a usable window.
. (Join-Path $kitRoot 'Import.ps1') -Harness Codex -Scope User -UserHome $fixtureHome -DshHome 'relative-dsh' -PrepareOnly
try { Record 'invalid DSH path does not prevent Codex GUI startup' ($script:ui.ImportButton.IsEnabled -and $script:ui.DestinationText.Text.EndsWith('letsgal-authoring')) }
finally { $script:window.Close() }
$report=@{checks=@($items.ToArray());passed=$items.Count;failed=0;scope='Isolated path, real cross-process locking and GUI startup regression tests.'}
[IO.File]::WriteAllText((Join-Path $Scratch 'safety-results.json'),($report|ConvertTo-Json -Depth 6),(New-Object Text.UTF8Encoding($false)))
$report|ConvertTo-Json -Depth 6
