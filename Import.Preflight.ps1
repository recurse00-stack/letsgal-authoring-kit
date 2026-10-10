# Shared read-only bundle, destination and installed-version inspection.
function Read-Json([string]$Path) {
    Assert-OrdinaryPath $Path
    return ([IO.File]::ReadAllText($Path, ([Text.Encoding]::UTF8)) | ConvertFrom-Json)
}

function Read-BundleRevision($Record) {
    if ($Record -and $Record.PSObject.Properties['revision'] -and $Record.revision -is [string]) { return $Record.revision }
    return $null
}

function Format-ReleaseLabel([string]$Version, [string]$Revision) {
    if (-not $Version) { return '未知版本' }
    if ($Revision) { return $Version + '（修订 ' + $Revision + '）' }
    return $Version + '（修订未标注）'
}

function Hash-File([string]$Path) {
    $algorithm = [Security.Cryptography.SHA256]::Create()
    $stream = [IO.File]::OpenRead($Path)
    try { return ([BitConverter]::ToString($algorithm.ComputeHash($stream))).Replace('-','').ToLowerInvariant() }
    finally { $stream.Dispose(); $algorithm.Dispose() }
}

function Tree-Map([string]$Root, [switch]$SkipReceipt) {
    Assert-OrdinaryPath $Root
    $map = @{}
    $stack = New-Object 'System.Collections.Generic.Stack[string]'
    $stack.Push($Root)
    while ($stack.Count -gt 0) {
        $dir = $stack.Pop()
        foreach ($item in (Get-ChildItem -LiteralPath $dir -Force)) {
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) {
                throw "Refusing linked content: $($item.FullName)"
            }
            if ($item.PSIsContainer) { $stack.Push($item.FullName); continue }
            $relative = $item.FullName.Substring($Root.Length + 1).Replace('\','/')
            if ($SkipReceipt -and $relative -eq '.install-receipt.json') { continue }
            $map[$relative] = Hash-File $item.FullName
        }
    }
    return $map
}

function Same-Map($Actual, $Expected) {
    if ($Actual.Count -ne $Expected.Count) { return $false }
    foreach ($key in $Expected.Keys) {
        if (-not $Actual.ContainsKey($key) -or $Actual[$key] -ne $Expected[$key]) { return $false }
    }
    return $true
}

function Record-Map($Records) {
    $map = @{}
    foreach ($entry in $Records) {
        if (-not ($entry.path -is [string]) -or $entry.path -notmatch '^[A-Za-z0-9_\-\u4e00-\u9fff./]+$' -or
            $entry.path.StartsWith('/') -or $entry.path.Split('/') -contains '..' -or
            $entry.path.Split('/') -contains '.' -or $entry.path.Split('/') -contains '' -or
            $entry.sha256 -notmatch '^[0-9a-f]{64}$' -or $map.ContainsKey($entry.path)) {
            throw 'Invalid or duplicate manifest path/hash.'
        }
        $map[$entry.path] = $entry.sha256
    }
    return $map
}

function Read-SelectedBundle([string]$BundleRoot, [string]$Channel) {
    if ($Channel) { $Channel = $Channel.ToLowerInvariant() }
    $bundle = Full-Path $BundleRoot
    $index = Read-Json (Join-Path $bundle 'bundle.json')
    $payloadRoot = $bundle
    $manifest = $index
    if ($index.schema -eq 2) {
        if ($Channel -notin @('stable','beta')) { throw '请先选择正式版（stable）或 Beta；安装器不会猜测工程通道。' }
        if ($index.owner -ne 'letsgal-authoring-kit' -or $index.skill -ne 'letsgal-authoring') { throw 'Unsupported channel index identity.' }
        $selected = @($index.channels | Where-Object { $_.id -ceq $Channel })
        if ($selected.Count -ne 1 -or $selected[0].bundle -cne "channels/$Channel/bundle.json") { throw 'Invalid channel manifest location.' }
        $payloadRoot = Join-Path $bundle "channels/$Channel"
        $manifest = Read-Json (Join-Path $payloadRoot 'bundle.json')
        if ($manifest.channel -cne $Channel -or $manifest.version -cne $index.version) { throw 'Channel manifest identity/version mismatch.' }
    }
    if ($manifest.schema -ne 1 -or $manifest.skill -ne 'letsgal-authoring' -or $manifest.owner -ne 'letsgal-authoring-kit' -or
        -not ($manifest.version -is [string]) -or [string]::IsNullOrWhiteSpace($manifest.version)) { throw 'Unsupported bundle identity/schema/version.' }
    $selectedChannel = if ($manifest.PSObject.Properties['channel']) { [string]$manifest.channel } else { 'legacy' }
    if ($selectedChannel -notin @('stable','beta','legacy')) { throw 'Unsupported payload channel.' }
    if ($Channel -and $selectedChannel -ne 'legacy' -and $selectedChannel -cne $Channel) { throw 'Selected channel differs from this single-channel bundle.' }
    return [pscustomobject]@{Manifest=$manifest;Source=(Join-Path $payloadRoot 'skills/letsgal-authoring');Channel=$selectedChannel}
}

function Get-InstallPreview([string]$BundleRoot, $Destination, [string]$UserHome, [switch]$ValidateBundle, [string]$Channel) {
    $homeRoot = Full-Path $UserHome
    Assert-OrdinaryPath $homeRoot
    if (-not (Test-Path -LiteralPath $homeRoot -PathType Container)) { throw 'User home does not exist.' }
    $area = Resolve-UserArea $homeRoot
    Assert-OptionalFile (Join-Path $area.Root 'installer-state.json')
    $bundle = Full-Path $BundleRoot
    Assert-OrdinaryPath $bundle
    $selection = Read-SelectedBundle $bundle $Channel
    $source = $selection.Source
    $target = Full-Path $Destination.Target
    Assert-OrdinaryPath $target
    if ($source.Equals($target,[StringComparison]::OrdinalIgnoreCase) -or
        $source.StartsWith($target + '\',[StringComparison]::OrdinalIgnoreCase) -or
        $target.StartsWith($bundle + '\',[StringComparison]::OrdinalIgnoreCase)) {
        throw 'Installation target must be outside the distribution bundle.'
    }
    if ($target.Equals($area.Root,[StringComparison]::OrdinalIgnoreCase) -or
        $target.StartsWith($area.Root + '\',[StringComparison]::OrdinalIgnoreCase) -or
        $area.Root.StartsWith($target + '\',[StringComparison]::OrdinalIgnoreCase)) {
        throw 'Target and personal configuration locations must not overlap.'
    }
    $backupRoot = Join-Path ([IO.Path]::GetDirectoryName($Destination.SkillsRoot)) '.letsgal-authoring-backups'
    Assert-OrdinaryPath $backupRoot
    $manifest = $selection.Manifest
    $expected = Record-Map $manifest.files
    if (-not $expected.ContainsKey('SKILL.md')) { throw 'Bundle manifest is missing SKILL.md.' }
    if ($ValidateBundle -and -not (Same-Map (Tree-Map $source) $expected)) {
        throw 'Bundle contents do not match manifest; installation stopped.'
    }
    $installed = Test-Path -LiteralPath $target
    $managed = $false
    $clean = $false
    $receipt = $null
    $installedVersion = $null
    $installedChannel = $null
    $current = @{}
    if ($installed) {
        if (-not (Test-Path -LiteralPath $target -PathType Container)) { throw 'Target exists but is not a directory.' }
        $current = Tree-Map $target -SkipReceipt
        $receiptPath = Join-Path $target '.install-receipt.json'
        if (Test-Path -LiteralPath $receiptPath -PathType Leaf) {
            try {
                $receipt = Read-Json $receiptPath
                $managed = $receipt.owner -eq 'letsgal-authoring-kit' -and $receipt.skill -eq 'letsgal-authoring'
                if ($managed) {
                    $clean = Same-Map $current (Record-Map $receipt.files)
                    if ($receipt.PSObject.Properties['version'] -and $receipt.version -is [string]) { $installedVersion = $receipt.version }
                    $installedChannel = if ($receipt.PSObject.Properties['channel'] -and $receipt.channel -in @('stable','beta')) { [string]$receipt.channel } else { 'legacy' }
                }
            } catch { $managed = $false; $clean = $false; $installedVersion = $null }
        }
    }
    $status = 'not_installed'
    if ($installed) {
        if (-not $managed -or -not $clean) { $status = 'requires_backup' }
        elseif ($installedChannel -ne 'legacy' -and $installedChannel -ne $selection.Channel) { $status = 'channel_change' }
        elseif ((Same-Map $current $expected) -and $installedChannel -eq $selection.Channel) { $status = 'current' }
        else { $status = 'replacement_available' }
    }
    # Detection creates no folders, locks, state, receipts or backups. The caller
    # must recheck immediately before its eventual installation transaction.
    return [pscustomobject]@{
        Target=$target; BundleVersion=$manifest.version; InstalledVersion=$installedVersion;
        BundleRevision=(Read-BundleRevision $manifest); InstalledRevision=(Read-BundleRevision $receipt);
        Channel=$selection.Channel; InstalledChannel=$installedChannel;
        Installed=$installed; Managed=$managed; Clean=$clean; Status=$status;
        Expected=$expected; CurrentMap=$current; Receipt=$receipt; Manifest=$manifest;
        BackupRoot=$backupRoot; Source=$source; BundleRoot=$bundle
    }
}
