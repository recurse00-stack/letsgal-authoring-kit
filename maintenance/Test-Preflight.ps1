# Read-only previews against complete bundles and NEW isolated homes.
# No native GUI, Agent session, real user home or publication is exercised.
param(
    [Parameter(Mandatory=$true)][string]$Scratch,
    [Parameter(Mandatory=$true)][string]$PreviousArchive
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0
$kitRoot = Split-Path $PSScriptRoot -Parent
. (Join-Path $kitRoot 'Import.Paths.ps1')
. (Join-Path $kitRoot 'Import.Preflight.ps1')
$Scratch = Full-Path $Scratch
$PreviousArchive = Full-Path $PreviousArchive
Assert-OrdinaryPath $Scratch
Assert-OptionalFile $PreviousArchive
if (Test-Path -LiteralPath $Scratch) { throw 'Use a NEW absolute scratch directory.' }
if (-not (Test-Path -LiteralPath $PreviousArchive -PathType Leaf)) { throw 'Provide a complete previous-release ZIP.' }
if ($Scratch.Equals($kitRoot,[StringComparison]::OrdinalIgnoreCase) -or
    $Scratch.StartsWith($kitRoot + '\',[StringComparison]::OrdinalIgnoreCase) -or
    $kitRoot.StartsWith($Scratch + '\',[StringComparison]::OrdinalIgnoreCase)) {
    throw 'Scratch must be outside the distribution bundle.'
}
[void][IO.Directory]::CreateDirectory($Scratch)
$checks = New-Object 'System.Collections.Generic.List[object]'
$shell = Join-Path $PSHOME $(if ($PSVersionTable.PSEdition -eq 'Core') { 'pwsh.exe' } else { 'powershell.exe' })

function Record-Check([string]$Name,[bool]$Passed) {
    $checks.Add(@{name=$Name;passed=$Passed})
    if (-not $Passed) { throw "Failed: $Name" }
}
function Snapshot-TestTrees([string[]]$Roots) {
    # Include empty directories and the links themselves, without traversing links.
    $map = @{}
    for ($index=0; $index -lt $Roots.Count; $index++) {
        $root = $Roots[$index]
        if (-not (Test-Path -LiteralPath $root)) { $map["$index/missing"] = 'missing'; continue }
        $map["$index/root"] = 'directory'
        $pending = New-Object 'System.Collections.Generic.Stack[string]'
        $pending.Push($root)
        while ($pending.Count -gt 0) {
            $dir = $pending.Pop()
            foreach ($item in (Get-ChildItem -LiteralPath $dir -Force)) {
                $relative = $item.FullName.Substring($root.Length + 1).Replace('\','/')
                $key = "$index/$relative"
                if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                    $map[$key] = 'reparse:' + [string]$item.Attributes + ':' + (@($item.Target) -join '|')
                } elseif ($item.PSIsContainer) {
                    $map[$key] = 'directory'
                    $pending.Push($item.FullName)
                } else { $map[$key] = Hash-File $item.FullName }
            }
        }
    }
    return $map
}
function Invoke-PreviewCase(
    [string]$Name,[string]$BundleRoot,$Destination,[string]$fixtureHome,
    [string]$ExpectedStatus,[switch]$Reject
) {
    $before = Snapshot-TestTrees @($Scratch,$kitRoot)
    $preview = $null
    $failure = $null
    try { $preview = Get-InstallPreview -BundleRoot $BundleRoot -Destination $Destination -UserHome $fixtureHome -Channel beta -ValidateBundle }
    catch { $failure = $_.Exception.Message }
    $after = Snapshot-TestTrees @($Scratch,$kitRoot)
    Record-Check ($Name + ' leaves all files directories and links unchanged') (Same-Map $before $after)
    if ($Reject) {
        Record-Check ($Name + ' is rejected before mutation') ($null -ne $failure)
    } else {
        if ($null -ne $failure) { throw "$Name preview failed: $failure" }
        Record-Check ($Name + ' status') ($preview.Status -eq $ExpectedStatus)
    }
    return $preview
}
function Invoke-BundleBackend([string]$BundleRoot,[string]$fixtureHome) {
    # Call the backend from its complete bundle; never extract/copy Install.ps1 alone.
    $backend = Join-Path $BundleRoot 'Install.ps1'
    $channelArgs = @()
    if ((Read-Json (Join-Path $BundleRoot 'bundle.json')).schema -eq 2) { $channelArgs = @('-Channel','beta') }
    $output = & $shell -NoLogo -NoProfile -ExecutionPolicy Bypass -File $backend -Harness Codex -Scope User -UserHome $fixtureHome -NonInteractive @channelArgs
    $code = $LASTEXITCODE
    $rows = @($output | Where-Object { $_ -is [string] -and $_.TrimStart().StartsWith('{') })
    $result = $null
    if ($rows.Count -gt 0) { $result = $rows[-1] | ConvertFrom-Json }
    return [pscustomobject]@{Code=$code;Result=$result;Output=($output -join "`n")}
}
function Snapshot-UserFiles([string]$Area) {
    $map = Tree-Map $Area
    [void]$map.Remove('installer-state.json')
    return $map
}

$currentManifest = Read-Json (Join-Path $kitRoot 'bundle.json')
$fixtureHome = Join-Path $Scratch "user's home 测试"
[void][IO.Directory]::CreateDirectory($fixtureHome)
$destination = Resolve-SkillDestination 'Codex' 'User' $fixtureHome '' '' ''
$fresh = Invoke-PreviewCase 'uninstalled complete bundle' $kitRoot $destination $fixtureHome 'not_installed'
Record-Check 'fresh preview reports bundle version without an installed version' (
    -not $fresh.Installed -and -not $fresh.Managed -and -not $fresh.Clean -and
    $fresh.BundleVersion -eq $currentManifest.version -and -not $fresh.InstalledVersion)

# Validate every archive entry before extracting the full immutable previous package.
Add-Type -AssemblyName System.IO.Compression.FileSystem
$oldExtraction = Join-Path $Scratch 'previous-complete-package'
[void][IO.Directory]::CreateDirectory($oldExtraction)
$archive = [IO.Compression.ZipFile]::OpenRead($PreviousArchive)
try {
    foreach ($entry in $archive.Entries) {
        $outputPath = [IO.Path]::GetFullPath((Join-Path $oldExtraction $entry.FullName))
        if (-not $outputPath.StartsWith($oldExtraction + '\',[StringComparison]::OrdinalIgnoreCase)) {
            throw 'Previous archive contains a path outside its extraction folder.'
        }
    }
} finally { $archive.Dispose() }
[IO.Compression.ZipFile]::ExtractToDirectory($PreviousArchive,$oldExtraction)
$oldBundle = Join-Path $oldExtraction 'letsgal-authoring-kit'
$oldManifest = Read-Json (Join-Path $oldBundle 'bundle.json')
Record-Check 'previous archive is a complete distinct release' (
    $oldManifest.owner -eq 'letsgal-authoring-kit' -and $oldManifest.skill -eq 'letsgal-authoring' -and
    $oldManifest.version -ne $currentManifest.version -and
    (Test-Path -LiteralPath (Join-Path $oldBundle 'Import.ps1') -PathType Leaf) -and
    (Test-Path -LiteralPath (Join-Path $oldBundle 'Import.xaml') -PathType Leaf) -and
    (Test-Path -LiteralPath (Join-Path $oldBundle 'Risk.Notice.ps1') -PathType Leaf))
$oldInstall = Invoke-BundleBackend $oldBundle $fixtureHome
Record-Check 'complete previous package installs in isolated home' (
    $oldInstall.Code -eq 0 -and $oldInstall.Result.action -eq 'installed' -and
    $oldInstall.Result.version -eq $oldManifest.version)
$target = $destination.Target
$area = Join-Path $fixtureHome '.letsgal-authoring'
$profile = Join-Path $area 'preferences/user.md'
[IO.File]::WriteAllBytes($profile,[Text.Encoding]::UTF8.GetBytes("个人偏好原文，保留编码与换行。`r`n"))
foreach ($pluginVersion in @('1.0.0','2.0.0-beta.1')) {
    $plugin = Join-Path $area ('plugins/example.plugin/' + $pluginVersion)
    [void][IO.Directory]::CreateDirectory($plugin)
    [IO.File]::WriteAllBytes((Join-Path $plugin 'SKILL.md'),[Text.Encoding]::UTF8.GetBytes('User-owned plugin knowledge ' + $pluginVersion))
    [IO.File]::WriteAllBytes((Join-Path $plugin 'private-notes.bin'),[byte[]](0..255))
}
[IO.File]::WriteAllBytes((Join-Path $area 'plugins/INDEX.md'),[Text.Encoding]::UTF8.GetBytes("Keep user index paragraphs.`r`n"))
[IO.File]::WriteAllBytes((Join-Path $area 'user-notes.bin'),[byte[]](255,0,128,10,13))
$oldFiles = Tree-Map $target
$userFiles = Snapshot-UserFiles $area
$upgradePreview = Invoke-PreviewCase 'complete previous release preview' $kitRoot $destination $fixtureHome 'update_available'
Record-Check 'upgrade preview reports both versions and clean managed status' (
    $upgradePreview.Installed -and $upgradePreview.Managed -and $upgradePreview.Clean -and
    $upgradePreview.InstalledVersion -eq $oldManifest.version -and
    $upgradePreview.BundleVersion -eq $currentManifest.version)
$upgrade = Invoke-BundleBackend $kitRoot $fixtureHome
Record-Check 'complete new package upgrades isolated previous release' (
    $upgrade.Code -eq 0 -and $upgrade.Result.action -eq 'installed' -and
    $upgrade.Result.version -eq $currentManifest.version)
Record-Check 'upgrade retains the complete previous directory including receipt' (
    $upgrade.Result.backup -and (Same-Map $oldFiles (Tree-Map $upgrade.Result.backup)))
Record-Check 'upgrade preserves every user-owned preference and plugin byte' (
    Same-Map $userFiles (Snapshot-UserFiles $area))
$currentPreview = Invoke-PreviewCase 'same release preview' $kitRoot $destination $fixtureHome 'current'
Record-Check 'current preview reports installed version and expected payload map' (
    $currentPreview.Installed -and $currentPreview.Managed -and $currentPreview.Clean -and
    $currentPreview.InstalledVersion -eq $currentManifest.version -and
    (Same-Map $currentPreview.CurrentMap $currentPreview.Expected))
$targetBeforeRepeat = Tree-Map $target
$backupsBeforeRepeat = @(Get-ChildItem -LiteralPath $currentPreview.BackupRoot -Directory -Filter '*-previous').Count
$repeat = Invoke-BundleBackend $kitRoot $fixtureHome
Record-Check 'repeat import is current without creating another previous backup' (
    $repeat.Code -eq 0 -and $repeat.Result.action -eq 'already_current' -and
    (Same-Map $targetBeforeRepeat (Tree-Map $target)) -and
    @(Get-ChildItem -LiteralPath $currentPreview.BackupRoot -Directory -Filter '*-previous').Count -eq $backupsBeforeRepeat)
Record-Check 'repeat import preserves every user-owned byte' (Same-Map $userFiles (Snapshot-UserFiles $area))

[IO.File]::AppendAllText((Join-Path $target 'SKILL.md'),"`nISOLATED LOCAL EDIT`n",[Text.Encoding]::UTF8)
$editedPreview = Invoke-PreviewCase 'locally modified managed release preview' $kitRoot $destination $fixtureHome 'requires_backup'
Record-Check 'edited preview preserves management identity but reports a dirty payload' (
    $editedPreview.Installed -and $editedPreview.Managed -and -not $editedPreview.Clean)
$unmanagedHome = Join-Path $Scratch 'unmanaged home'
[void][IO.Directory]::CreateDirectory($unmanagedHome)
$unmanagedDestination = Resolve-SkillDestination 'Codex' 'User' $unmanagedHome '' '' ''
[void][IO.Directory]::CreateDirectory($unmanagedDestination.Target)
[IO.File]::WriteAllBytes((Join-Path $unmanagedDestination.Target 'user-owned.txt'),[Text.Encoding]::UTF8.GetBytes('Unmanaged user file; preserve it.'))
$unmanagedPreview = Invoke-PreviewCase 'unmanaged release preview' $kitRoot $unmanagedDestination $unmanagedHome 'requires_backup'
Record-Check 'unmanaged preview reports installed but not managed or clean' (
    $unmanagedPreview.Installed -and -not $unmanagedPreview.Managed -and -not $unmanagedPreview.Clean)

$bundleDestination = Resolve-SkillDestination 'Manual' 'User' $fixtureHome '' (Join-Path $kitRoot 'skills') ''
[void](Invoke-PreviewCase 'target inside complete bundle' $kitRoot $bundleDestination $fixtureHome '' -Reject)
$userAreaDestination = Resolve-SkillDestination 'Manual' 'User' $fixtureHome '' (Join-Path $area 'plugins') ''
[void](Invoke-PreviewCase 'target inside personal user area' $kitRoot $userAreaDestination $fixtureHome '' -Reject)
$badBundle = Join-Path $Scratch 'corrupted complete bundle'
Copy-Item -LiteralPath $kitRoot -Destination $badBundle -Recurse
[IO.File]::WriteAllBytes((Join-Path $badBundle 'channels/beta/skills/letsgal-authoring/SKILL.md'),[Text.Encoding]::UTF8.GetBytes('Corrupted payload; manifest remains unchanged.'))
[void](Invoke-PreviewCase 'corrupted complete bundle' $badBundle $destination $fixtureHome '' -Reject)

$linkedHome = Join-Path $Scratch 'linked home'
$outside = Join-Path $Scratch 'outside link destination'
[void][IO.Directory]::CreateDirectory($linkedHome)
[void][IO.Directory]::CreateDirectory($outside)
[IO.File]::WriteAllBytes((Join-Path $outside 'sentinel.bin'),[byte[]](0,128,255))
$linkedDestination = Resolve-SkillDestination 'Codex' 'User' $linkedHome '' '' ''
$link = Join-Path $linkedHome '.agents'
[void](New-Item -ItemType Junction -Path $link -Target $outside)
try { [void](Invoke-PreviewCase 'linked destination appearing after path resolution' $kitRoot $linkedDestination $linkedHome '' -Reject) }
finally {
    # Delete this known fixture link entry only; never follow it or delete its target.
    [IO.Directory]::Delete($link)
}
Record-Check 'linked-path rejection leaves external sentinel intact' (
    [Convert]::ToBase64String([IO.File]::ReadAllBytes((Join-Path $outside 'sentinel.bin'))) -eq [Convert]::ToBase64String([byte[]](0,128,255)))

$report = [ordered]@{
    version=$currentManifest.version;previous_version=$oldManifest.version;
    checks=@($checks.ToArray());passed=$checks.Count;failed=0;
    scope='Isolated complete-package install, real previous-release upgrade, read-only preview hashes including empty directories, and path rejection. No native GUI or live Agent acceptance.'
}
[IO.File]::WriteAllText((Join-Path $Scratch 'preflight-results.json'),($report | ConvertTo-Json -Depth 8),(New-Object Text.UTF8Encoding($false)))
$report | ConvertTo-Json -Depth 8
