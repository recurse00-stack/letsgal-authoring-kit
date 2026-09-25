# Shared, read-only destination resolution for the GUI and command-line installer.
function Full-Path([string]$Value) {
    if ([string]::IsNullOrWhiteSpace($Value) -or $Value -notmatch '^(?:[A-Za-z]:[\\/]|\\\\[^\\/]+[\\/][^\\/]+)' -or $Value -match '^\\\\[?.]\\') { throw 'Please choose an absolute folder path (no drive-relative or device paths).' }
    $full = [IO.Path]::GetFullPath($Value)
    if ($full.TrimEnd([char[]]'\/') -eq [IO.Path]::GetPathRoot($full).TrimEnd([char[]]'\/')) { throw 'A drive/share root is not an installation folder.' }
    return $full.TrimEnd([char[]]'\/')
}
function Assert-OptionalFile([string]$Path) {
    Assert-OrdinaryPath $Path
    if ((Test-Path -LiteralPath $Path) -and -not (Test-Path -LiteralPath $Path -PathType Leaf)) { throw "Expected a file, but found another object: $Path" }
}
function Assert-OrdinaryPath([string]$Path) {
    $current = [IO.Path]::GetFullPath($Path)
    while ($current) {
        if (Test-Path -LiteralPath $current) {
            $item = Get-Item -LiteralPath $current -Force
            if (($item.Attributes -band [IO.FileAttributes]::ReparsePoint) -ne 0) { throw "Refusing a symlink/junction/reparse path: $current" }
        }
        $parent = [IO.Directory]::GetParent($current)
        if ($null -eq $parent) { break }
        $current = $parent.FullName
    }
}
function Resolve-UserArea([string]$UserHome) {
    $root = Join-Path (Full-Path $UserHome) '.letsgal-authoring'
    $preferences = Join-Path $root 'preferences'
    $plugins = Join-Path $root 'plugins'
    foreach ($dir in @($root,$preferences,$plugins)) {
        Assert-OrdinaryPath $dir
        if ((Test-Path -LiteralPath $dir) -and -not (Test-Path -LiteralPath $dir -PathType Container)) { throw "Expected a user-area directory: $dir" }
    }
    $canonical = Join-Path $preferences 'user.md'
    $legacy = Join-Path $root 'user.md'
    Assert-OptionalFile $canonical
    Assert-OptionalFile $legacy
    $profile = $canonical
    if (-not (Test-Path -LiteralPath $canonical) -and (Test-Path -LiteralPath $legacy)) { $profile = $legacy }
    return [pscustomobject]@{Root=$root;Preferences=$preferences;Plugins=$plugins;Profile=$profile;CanonicalProfile=$canonical;LegacyProfile=$legacy}
}
function Get-DshHomeInfo([string]$Value, [string]$HomeRoot) {
    $source = '指定的数据目录'
    if (-not $Value) { $Value = [Environment]::GetEnvironmentVariable('DSH_HOME'); $source = 'DSH_HOME 环境变量' }
    if (-not $Value) { $Value = Join-Path $HomeRoot '.dsh'; $source = '默认目录；若 DSH 已迁移，请选择实际数据目录' }
    if ($Value -eq '~') { $Value = $HomeRoot }
    elseif ($Value.StartsWith('~/') -or $Value.StartsWith('~\')) { $Value = Join-Path $HomeRoot $Value.Substring(2) }
    $path = Full-Path $Value
    Assert-OrdinaryPath $path
    return [pscustomobject]@{Path=$path;Source=$source}
}
function Resolve-SkillDestination([string]$Harness, [string]$Scope, [string]$UserHome, [string]$ProjectPath, [string]$SkillsDirectory, [string]$DshHome) {
    if ($Harness -notin @('Codex','Claude','Cursor','Copilot','DSH','Manual')) { throw 'Please select an Agent.' }
    if ($Scope -notin @('User','Project')) { throw 'Please select an installation scope.' }
    $homeRoot = Full-Path $UserHome
    Assert-OrdinaryPath $homeRoot
    if (-not (Test-Path -LiteralPath $homeRoot -PathType Container)) { throw 'User home does not exist.' }
    $scopeRoot = $homeRoot
    $note = ''
    $resolvedDshHome = $null
    if ($Scope -eq 'Project' -and $Harness -ne 'Manual') {
        $scopeRoot = Full-Path $ProjectPath
        Assert-OrdinaryPath $scopeRoot
        if (-not (Test-Path -LiteralPath $scopeRoot -PathType Container)) { throw 'Please choose an existing project folder.' }
        if ($Harness -eq 'DSH') {
            $probe = $scopeRoot
            while ($probe) {
                if (Test-Path -LiteralPath (Join-Path $probe '.git')) { $scopeRoot = $probe; break }
                $parent = [IO.Directory]::GetParent($probe)
                if ($null -eq $parent) { break }
                $probe = $parent.FullName
            }
            $note = 'DSH 使用最近的 Git 仓库根目录；无仓库时使用所选文件夹。'
        }
    }
    if ($Harness -eq 'Manual') { $skillsRoot = Full-Path $SkillsDirectory; $note = '这里应是 Agent 已配置的 skills 根目录，不包含技能名称。' }
    elseif ($Harness -eq 'DSH' -and $Scope -eq 'User') {
        $info = Get-DshHomeInfo $DshHome $homeRoot
        $resolvedDshHome = $info.Path
        $skillsRoot = Join-Path $resolvedDshHome 'skills'
        $note = $info.Source + '。DSH 需启用文件系统技能提供器。'
    } else {
        $folder = '.agents'
        if ($Harness -eq 'Claude') { $folder = '.claude' }
        if ($Harness -eq 'DSH') { $folder = '.dsh' }
        if ($folder -eq '.agents') { $note = '共用 .agents/skills；支持此目录的其他 Agent 也可能发现它。' }
        $skillsRoot = Join-Path (Join-Path $scopeRoot $folder) 'skills'
    }
    $target = Full-Path (Join-Path $skillsRoot 'letsgal-authoring')
    Assert-OrdinaryPath $target
    return [pscustomobject]@{Target=$target;SkillsRoot=$skillsRoot;ScopeRoot=$scopeRoot;DshHome=$resolvedDshHome;Note=$note}
}
