# Windows PowerShell 5.1 / PowerShell 7. No downloads or administrator access.
[CmdletBinding()]
param(
    [ValidateSet('Install','Check','Uninstall')][string]$Action = 'Install',
    [ValidateSet('Codex','Claude','Cursor','Copilot','DSH','Manual')][string]$Harness,
    [ValidateSet('User','Project')][string]$Scope,
    [string]$ProjectPath,
    [string]$SkillsDirectory,
    [string]$DshHome,
    [string]$UserHome = [Environment]::GetFolderPath('UserProfile'),
    [switch]$NonInteractive,
    [switch]$ReplaceModified
)
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version 2.0
$SkillName = 'letsgal-authoring'
$Owner = 'letsgal-authoring-kit'
$Utf8 = New-Object System.Text.UTF8Encoding($false)
$operationLock = $null

. (Join-Path $PSScriptRoot 'Import.Paths.ps1')
function Ensure-Directory([string]$Path) {
    Assert-OrdinaryPath $Path
    [void][IO.Directory]::CreateDirectory($Path)
}
function Initialize-UserArea([string]$HomeRoot) {
    $area = Resolve-UserArea $HomeRoot
    foreach ($dir in @($area.Root,$area.Preferences,$area.Plugins)) { Ensure-Directory $dir }
    # Legacy preferences remain active; never create an empty file that shadows them.
    if (-not (Test-Path -LiteralPath $area.Profile)) {
        $initial = "# 我的 LetsGal 创作偏好`r`n`r`n个人区：仅记录用户明确要求保存的文风、命名与协作习惯。插件接口资料单独放在同级 plugins 目录，项目约定放在工程 LETSGAL.md。更新和卸载公共技能都保留用户区。`r`n`r`n目前没有已确认的额外偏好。`r`n"
        $bytes = $Utf8.GetBytes($initial)
        $stream = $null
        try {
            $stream = [IO.File]::Open($area.Profile,[IO.FileMode]::CreateNew,[IO.FileAccess]::Write)
            $stream.Write($bytes,0,$bytes.Length)
        } catch [IO.IOException] {
            # Another Agent may have created it concurrently. Do not truncate or replace it.
            if ($stream -or -not (Test-Path -LiteralPath $area.Profile -PathType Leaf)) { throw }
            Assert-OptionalFile $area.Profile
        } finally { if ($stream) { $stream.Dispose() } }
    }
}
function Read-Json([string]$Path) {
    Assert-OrdinaryPath $Path
    return ([IO.File]::ReadAllText($Path, $Utf8) | ConvertFrom-Json)
}
function Write-Json([string]$Path, $Value) {
    Assert-OrdinaryPath $Path
    [IO.File]::WriteAllText($Path, ($Value | ConvertTo-Json -Depth 12), $Utf8)
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
function Confirm-Replacement([string]$Reason) {
    if ($ReplaceModified) { return }
    if ($NonInteractive) { throw "Existing content differs or is unmanaged; no changes made. $Reason" }
    Write-Host $Reason -ForegroundColor Yellow
    Write-Host '原目录会完整移到备份；个人配置保留。建议先将 Skill 内特调迁到 user.md。'
    if ((Read-Host '输入 BACKUP-AND-REPLACE 才继续，其他输入取消') -cne 'BACKUP-AND-REPLACE') {
        throw 'Cancelled; original content preserved.'
    }
}

try {
    $homeRoot = Full-Path $UserHome
    if (-not (Test-Path -LiteralPath $homeRoot -PathType Container) -or $homeRoot -eq [IO.Path]::GetPathRoot($homeRoot).TrimEnd('\')) {
        throw 'UserHome must be an existing user directory, not a drive root.'
    }
    Assert-OrdinaryPath $homeRoot
    $userArea = Resolve-UserArea $homeRoot
    $profileRoot = $userArea.Root
    $profileFile = $userArea.Profile
    $pluginsRoot = $userArea.Plugins
    $stateFile = Join-Path $profileRoot 'installer-state.json'
    Assert-OrdinaryPath $profileRoot
    Assert-OptionalFile $profileFile
    Assert-OptionalFile $stateFile
    $previous = $null
    if (Test-Path -LiteralPath $stateFile -PathType Leaf) {
        try { $previous = Read-Json $stateFile } catch { Write-Warning 'Previous installer choices could not be read; choose again.' }
    }
    if (-not $Harness) {
        if ($NonInteractive) { throw 'Harness is required in non-interactive mode.' }
        Write-Host 'LetsGal 创作与协作 - 独立社区技能安装器' -ForegroundColor Cyan
        Write-Host '1 Codex   2 Claude Code   3 Cursor   4 GitHub Copilot   5 DSH   6 自选技能目录'
        $choice = Read-Host '选择工具（回车沿用上次选择；首次默认 Codex）'
        $names = @('Codex','Claude','Cursor','Copilot','DSH','Manual')
        if ($choice -eq '' -and $previous -and $previous.Harness -in $names) { $Harness = $previous.Harness }
        elseif ($choice -eq '') { $Harness = 'Codex' }
        elseif ($choice -match '^[1-6]$') { $Harness = $names[[int]$choice - 1] }
        else { throw 'Invalid selection.' }
    }
    if (-not $Scope) {
        if ($NonInteractive) { $Scope = 'User' }
        else {
            $default = 'User'
            if ($previous -and $previous.Scope -in @('User','Project')) { $default = $previous.Scope }
            $answer = Read-Host "安装范围：1 个人所有工程，2 当前工程（回车沿用 $default）"
            if ($answer -eq '') { $Scope = $default }
            elseif ($answer -eq '1') { $Scope = 'User' }
            elseif ($answer -eq '2') { $Scope = 'Project' }
            else { throw 'Invalid scope.' }
        }
    }
    if ($Scope -eq 'Project' -and $Harness -ne 'Manual') {
        if (-not $ProjectPath -and -not $NonInteractive) {
            $prompt = '输入工程绝对路径'
            if ($previous -and $previous.ProjectPath) { $prompt += "（回车沿用 $($previous.ProjectPath)）" }
            $ProjectPath = Read-Host $prompt
            if (-not $ProjectPath -and $previous) { $ProjectPath = $previous.ProjectPath }
        }
    }
    if ($Harness -eq 'Manual') {
        if (-not $SkillsDirectory -and -not $NonInteractive) {
            $SkillsDirectory = Read-Host '输入 AI 工具的 skills 根目录绝对路径（不要包含技能名称）'
            if (-not $SkillsDirectory -and $previous -and $previous.Harness -eq 'Manual') { $SkillsDirectory = $previous.SkillsDirectory }
        }
    }
    if ($Harness -eq 'DSH' -and $Scope -eq 'User' -and -not $DshHome -and -not $NonInteractive) {
        $defaultDsh = (Get-DshHomeInfo '' $homeRoot).Path
        if ($previous -and $previous.PSObject.Properties['DshHome'] -and $previous.DshHome) { $defaultDsh = $previous.DshHome }
        $DshHome = Read-Host "DSH 数据目录（回车使用 $defaultDsh）"
        if (-not $DshHome) { $DshHome = $defaultDsh }
    }
    $destination = Resolve-SkillDestination $Harness $Scope $homeRoot $ProjectPath $SkillsDirectory $DshHome
    $skillsRoot = $destination.SkillsRoot
    $scopeRoot = $destination.ScopeRoot
    $target = $destination.Target
    if ($destination.DshHome) { $DshHome = $destination.DshHome }
    $bundle = Full-Path $PSScriptRoot
    $source = Join-Path (Join-Path $bundle 'skills') $SkillName
    if ($source.Equals($target, [StringComparison]::OrdinalIgnoreCase) -or
        $source.StartsWith($target + '\', [StringComparison]::OrdinalIgnoreCase) -or
        $target.StartsWith($bundle + '\', [StringComparison]::OrdinalIgnoreCase)) {
        throw 'Installation target must be outside the distribution bundle.'
    }
    if ($target.Equals($profileRoot,[StringComparison]::OrdinalIgnoreCase) -or
        $target.StartsWith($profileRoot + '\', [StringComparison]::OrdinalIgnoreCase) -or
        $profileRoot.StartsWith($target + '\', [StringComparison]::OrdinalIgnoreCase)) { throw 'Target and personal configuration locations must not overlap.' }
    $backupRoot = Join-Path ([IO.Path]::GetDirectoryName($skillsRoot)) '.letsgal-authoring-backups'
    Assert-OrdinaryPath $backupRoot
    if ($Action -eq 'Install') {
        $manifest = Read-Json (Join-Path $bundle 'bundle.json')
        if ($manifest.schema -ne 1 -or $manifest.skill -ne $SkillName -or $manifest.owner -ne $Owner) { throw 'Unsupported bundle identity/schema.' }
        $expected = Record-Map $manifest.files
        if (-not $expected.ContainsKey('SKILL.md') -or -not (Same-Map (Tree-Map $source) $expected)) { throw 'Bundle contents do not match manifest; installation stopped.' }
    }
    if ($Action -ne 'Check') {
        Ensure-Directory $backupRoot
        $lockPath = Join-Path $backupRoot 'installer.lock'
        Assert-OptionalFile $lockPath
        try { $operationLock = [IO.File]::Open($lockPath,[IO.FileMode]::OpenOrCreate,[IO.FileAccess]::ReadWrite,[IO.FileShare]::None) }
        catch { throw 'Another installer may be using this location, or its lock cannot be opened. Close the other installer or check folder access; no skill files changed.' }
    }
    Write-Host "目标：$target"
    Write-Host "保留个人偏好：$profileFile"
    Write-Host "保留插件资料：$pluginsRoot"
    if ($Harness -in @('Codex','Cursor','Copilot')) {
        Write-Host '.agents/skills 是共享目录；同机支持该目录的 AI 工具可能同时发现此技能。'
    }
    foreach ($other in @('.agents','.claude','.cursor','.codex','.github','.copilot','.dsh')) {
        $candidate = Join-Path (Join-Path (Join-Path $scopeRoot $other) 'skills') $SkillName
        if ($candidate -ne $target -and (Test-Path -LiteralPath $candidate)) {
            Write-Warning "Another copy exists at $candidate. It is preserved; verify duplicate discovery in your AI tool."
        }
    }
    $receiptPath = Join-Path $target '.install-receipt.json'
    $installed = Test-Path -LiteralPath $target
    $receipt = $null
    $managed = $false
    $clean = $false
    if ($installed) {
        if (-not (Test-Path -LiteralPath $target -PathType Container)) { throw 'Target exists but is not a directory.' }
        $currentMap = Tree-Map $target -SkipReceipt
        if (Test-Path -LiteralPath $receiptPath -PathType Leaf) {
            try {
                $receipt = Read-Json $receiptPath
                $managed = $receipt.owner -eq $Owner -and $receipt.skill -eq $SkillName
                if ($managed) { $clean = Same-Map $currentMap (Record-Map $receipt.files) }
            } catch { $managed = $false; $clean = $false }
        }
    }
    if ($Action -eq 'Check') {
        [ordered]@{action='check';installed=$installed;managed=$managed;unchanged=$clean;target=$target;profile=$profileFile;plugins=$pluginsRoot;ai_loaded='not_tested'} | ConvertTo-Json -Compress
        if (-not $installed -or -not $managed -or -not $clean) { exit 2 }
        exit 0
    }
    $stamp = (Get-Date -Format 'yyyyMMdd-HHmmss-fff') + '-' + [Guid]::NewGuid().ToString('N').Substring(0,8)
    if ($Action -eq 'Uninstall') {
        if (-not $installed) { throw 'Skill is not installed at this target.' }
        if (-not $managed -or -not $clean) { Confirm-Replacement "The existing skill has local edits or is unmanaged: $target" }
        if (-not $NonInteractive -and (Read-Host '卸载将把技能移到备份，保留特调。输入 YES 继续') -cne 'YES') { throw 'Cancelled.' }
        Ensure-Directory $backupRoot
        $backup = Join-Path $backupRoot ($stamp + '-uninstalled')
        Assert-OrdinaryPath $target
        if (-not (Same-Map (Tree-Map $target -SkipReceipt) $currentMap)) { throw 'Skill changed during uninstall; original left in place.' }
        [IO.Directory]::Move($target, $backup)
        Write-Json (Join-Path $backupRoot ($stamp + '-uninstall.json')) @{target=$target;backup=$backup;profile_preserved=$profileFile;plugins_preserved=$pluginsRoot}
        @{action='uninstalled_to_backup';backup=$backup;profile=$profileFile;plugins=$pluginsRoot} | ConvertTo-Json -Compress
        exit 0
    }
    if ($installed -and (-not $managed -or -not $clean)) { Confirm-Replacement "The existing skill has local edits or is unmanaged: $target" }
    if ($installed -and $managed -and $clean -and (Same-Map $currentMap $expected)) {
        Initialize-UserArea $homeRoot
        Write-Json $stateFile @{Harness=$Harness;Scope=$Scope;ProjectPath=$ProjectPath;SkillsDirectory=$SkillsDirectory;DshHome=$DshHome}
        @{action='already_current';target=$target;profile=$profileFile;plugins=$pluginsRoot;ai_loaded='not_tested'} | ConvertTo-Json -Compress
        exit 0
    }
    if (-not $NonInteractive -and (Read-Host '以上位置正确吗？回车安装，输入 N 取消') -match '^[Nn]') { throw 'Cancelled.' }
    Ensure-Directory $profileRoot
    Ensure-Directory $backupRoot
    $stage = Join-Path $backupRoot ($stamp + '-staging')
    Ensure-Directory $stage
    foreach ($relative in $expected.Keys) {
        $output = Join-Path $stage $relative
        Ensure-Directory ([IO.Path]::GetDirectoryName($output))
        [IO.File]::Copy((Join-Path $source $relative), $output, $false)
    }
    if (-not (Same-Map (Tree-Map $stage) $expected)) { throw 'Staging verification failed; original untouched.' }
    Write-Json (Join-Path $stage '.install-receipt.json') @{owner=$Owner;skill=$SkillName;version=$manifest.version;installed_at=(Get-Date -Format o);files=$manifest.files}
    # Initialize only missing user-area items before moving any installed Skill.
    Initialize-UserArea $homeRoot
    Ensure-Directory $skillsRoot
    Assert-OrdinaryPath $target
    $backup = $null
    if ($installed) {
        # Re-read immediately before mutation, including any new files.
        if (-not (Same-Map (Tree-Map $target -SkipReceipt) $currentMap)) { throw 'Skill changed during installation; original left in place.' }
        $backup = Join-Path $backupRoot ($stamp + '-previous')
        [IO.Directory]::Move($target, $backup)
    } elseif (Test-Path -LiteralPath $target) { throw 'Target appeared during installation; nothing overwritten.' }
    $published = $false
    try {
        [IO.Directory]::Move($stage, $target)
        $published = $true
        if (-not (Same-Map (Tree-Map $target -SkipReceipt) $expected)) { throw 'Installed file verification failed.' }
    } catch {
        if ($published -and (Test-Path -LiteralPath $target)) {
            [IO.Directory]::Move($target, (Join-Path $backupRoot ($stamp + '-failed')))
        }
        if ($backup -and (Test-Path -LiteralPath $backup) -and -not (Test-Path -LiteralPath $target)) { [IO.Directory]::Move($backup, $target) }
        throw
    }
    Write-Json $stateFile @{Harness=$Harness;Scope=$Scope;ProjectPath=$ProjectPath;SkillsDirectory=$SkillsDirectory;DshHome=$DshHome}
    Write-Json (Join-Path $backupRoot ($stamp + '-install.json')) @{target=$target;previous=$backup;version=$manifest.version;profile_preserved=$profileFile;plugins_preserved=$pluginsRoot}
    Write-Host '文件安装并校验完成。打开新的 AI 会话，按 README 的验证提示确认技能与个人配置已加载。' -ForegroundColor Green
    @{action='installed';version=$manifest.version;target=$target;backup=$backup;profile=$profileFile;plugins=$pluginsRoot;ai_loaded='not_tested'} | ConvertTo-Json -Compress
    exit 0
} catch {
    Write-Host ("安装器停止：" + $_.Exception.Message) -ForegroundColor Red
    @{action='error';message=$_.Exception.Message;requires_backup=$_.Exception.Message.StartsWith('Existing content differs or is unmanaged;')} | ConvertTo-Json -Compress
    exit 1
} finally {
    if ($operationLock) { $operationLock.Dispose() }
}
