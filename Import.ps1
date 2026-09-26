# Native Windows importer; all mutations are delegated to the verified CLI backend.
[CmdletBinding()]
param(
    [ValidateSet('Install','Check','Uninstall')][string]$InitialAction = 'Install',
    [ValidateSet('Codex','Claude','Cursor','Copilot','DSH','Manual')][string]$Harness,
    [ValidateSet('User','Project')][string]$Scope,
    [string]$UserHome = [Environment]::GetFolderPath('UserProfile'),
    [string]$ProjectPath,
    [string]$DshHome,
    [string]$SkillsDirectory,
    [Parameter(DontShow=$true)][switch]$PrepareOnly
)
$ErrorActionPreference = 'Stop'
Add-Type -AssemblyName PresentationFramework
Add-Type -AssemblyName System.Windows.Forms
. (Join-Path $PSScriptRoot 'Import.Paths.ps1')
. (Join-Path $PSScriptRoot 'Risk.Notice.ps1')
$script:job = $null
$script:destination = $null
$script:lastAction = $null
$script:loading = $true
$script:ui = @{}
$script:prompt = ''

function Quote-PS([string]$Value) { return "'" + $Value.Replace("'", "''") + "'" }
function Get-SelectedAgent { return [string]$script:ui.AgentBox.SelectedItem.Tag }
function Get-SelectedScope { if ($script:ui.ScopeBox.SelectedIndex -eq 1) { return 'Project' }; return 'User' }
function Show-ImportResult([string]$Title, [string]$Body, [bool]$Success) {
    $script:ui.ResultPanel.Visibility = 'Visible'
    $script:ui.ResultPanel.Background = if ($Success) { '#EAF4EF' } else { '#FFF2DE' }
    $script:ui.ResultTitle.Text = $Title
    $script:ui.ResultBody.Text = $Body
}
function Update-Destination {
    if ($script:loading -or $script:job) { return }
    $agent = Get-SelectedAgent
    $scopeName = Get-SelectedScope
    $script:ui.DshPanel.Visibility = if ($agent -eq 'DSH' -and $scopeName -eq 'User') { 'Visible' } else { 'Collapsed' }
    $script:ui.ProjectPanel.Visibility = if ($scopeName -eq 'Project' -and $agent -ne 'Manual') { 'Visible' } else { 'Collapsed' }
    $script:ui.ManualPanel.Visibility = if ($agent -eq 'Manual') { 'Visible' } else { 'Collapsed' }
    $script:ui.ScopeBox.IsEnabled = $agent -ne 'Manual'
    $displayName = [string]$script:ui.AgentBox.SelectedItem.Content
    $script:ui.ImportButton.Content = switch ($InitialAction) { 'Check' { '检查安装' }; 'Uninstall' { '卸载并保留特调' }; default { '导入到 ' + $displayName } }
    $script:ui.BackupButton.Visibility = 'Collapsed'
    $script:ui.CopyButton.Visibility = 'Collapsed'
    $script:ui.ResultPanel.Visibility = 'Collapsed'
    try {
        $area = Resolve-UserArea $UserHome
        $script:ui.ProfileText.Text = '个人偏好：' + $area.Profile
        $script:ui.PluginsText.Text = '插件 Skill：' + $area.Plugins
        $script:destination = Resolve-SkillDestination $agent $scopeName $UserHome $script:ui.ProjectBox.Text $script:ui.ManualBox.Text $script:ui.DshBox.Text
        $script:ui.DestinationText.Text = $script:destination.Target
        $script:ui.PathNote.Text = $script:destination.Note
        $script:ui.ImportButton.IsEnabled = $true
        $script:ui.CheckButton.IsEnabled = $true
        $script:ui.RemoveButton.IsEnabled = $true
    } catch {
        $script:destination = $null
        $script:ui.DestinationText.Text = '请先选择正确的文件夹。'
        $script:ui.PathNote.Text = $_.Exception.Message
        $script:ui.ImportButton.IsEnabled = $false
        $script:ui.CheckButton.IsEnabled = $false
        $script:ui.RemoveButton.IsEnabled = $false
    }
}
function Select-Folder($TextBox, [string]$Description) {
    $dialog = New-Object System.Windows.Forms.FolderBrowserDialog
    $dialog.Description = $Description
    if (Test-Path -LiteralPath $TextBox.Text -PathType Container) { $dialog.SelectedPath = $TextBox.Text }
    try { if ($dialog.ShowDialog() -eq [System.Windows.Forms.DialogResult]::OK) { $TextBox.Text = $dialog.SelectedPath } }
    finally { $dialog.Dispose() }
}
function Start-ImportAction([string]$Action, [bool]$Replace = $false) {
    if ($script:job -or -not $script:destination) { return }
    if ($Action -eq 'Uninstall') {
        $answer = [Windows.MessageBox]::Show($script:window, "将此技能移到备份目录，个人特调与作品文件保留。`n`n$($script:destination.Target)", '卸载技能', 'YesNo', 'Question')
        if ($answer -ne 'Yes') { return }
    }
    if ($Replace) {
        $answer = [Windows.MessageBox]::Show($script:window, '原技能中的修改将完整保存在备份中。建议先把个人改动迁到 user.md。确认先备份再继续？', '保留原文后继续', 'YesNo', 'Question')
        if ($answer -ne 'Yes') { return }
    }
    $script:lastAction = $Action
    $arguments = @{
        Action=$Action;Harness=(Get-SelectedAgent);Scope=(Get-SelectedScope);UserHome=$UserHome;
        ProjectPath=$script:ui.ProjectBox.Text;DshHome=$script:ui.DshBox.Text;SkillsDirectory=$script:ui.ManualBox.Text
    }
    $command = '[Console]::OutputEncoding = New-Object System.Text.UTF8Encoding($false); & ' + (Quote-PS (Join-Path $PSScriptRoot 'Install.ps1'))
    foreach ($key in $arguments.Keys) { if ($arguments[$key]) { $command += ' -' + $key + ' ' + (Quote-PS $arguments[$key]) } }
    $command += ' -NonInteractive'
    if ($Replace) { $command += ' -ReplaceModified' }
    $encoded = [Convert]::ToBase64String([Text.Encoding]::Unicode.GetBytes($command))
    $start = New-Object Diagnostics.ProcessStartInfo
    $executable = if ($PSVersionTable.PSEdition -eq 'Core') { 'pwsh.exe' } else { 'powershell.exe' }
    $start.FileName = Join-Path $PSHOME $executable
    $start.Arguments = '-NoLogo -NoProfile -NonInteractive -ExecutionPolicy Bypass -EncodedCommand ' + $encoded
    $start.UseShellExecute = $false
    $start.CreateNoWindow = $true
    $start.WindowStyle = [Diagnostics.ProcessWindowStyle]::Hidden
    $start.RedirectStandardOutput = $true
    $start.RedirectStandardError = $true
    $start.StandardOutputEncoding = New-Object Text.UTF8Encoding($false)
    $start.StandardErrorEncoding = New-Object Text.UTF8Encoding($false)
    $process = New-Object Diagnostics.Process
    $process.StartInfo = $start
    try {
        [void]$process.Start()
        $script:job = @{Process=$process;Out=$process.StandardOutput.ReadToEndAsync();Err=$process.StandardError.ReadToEndAsync();Target=$script:destination.Target;Action=$Action}
        $script:ui.SettingsPanel.IsEnabled = $false
        foreach ($name in @('ImportButton','CheckButton','RemoveButton','BackupButton')) { $script:ui[$name].IsEnabled = $false }
        $script:ui.CopyButton.Visibility = 'Collapsed'
        $script:ui.BackupButton.Visibility = 'Collapsed'
        $script:ui.Progress.Visibility = 'Visible'
        Show-ImportResult '正在处理，请稍候…' '正在校验文件并保留已有配置。' $true
        $script:timer.Start()
    } catch {
        $process.Dispose()
        Show-ImportResult '未能启动导入' $_.Exception.Message $false
    }
}
function Complete-ImportAction {
    if (-not $script:job -or -not $script:job.Process.HasExited -or -not $script:job.Out.IsCompleted -or -not $script:job.Err.IsCompleted) { return }
    $script:timer.Stop()
    $job = $script:job
    $script:job = $null
    $stdout = $job.Out.Result
    $stderr = $job.Err.Result
    $exitCode = $job.Process.ExitCode
    $job.Process.Dispose()
    $script:ui.SettingsPanel.IsEnabled = $true
    foreach ($name in @('ImportButton','CheckButton','RemoveButton','BackupButton')) { $script:ui[$name].IsEnabled = $true }
    $script:ui.Progress.Visibility = 'Collapsed'
    $script:ui.LogBox.Text = ($stdout + "`r`n" + $stderr).Trim()
    $result = $null
    foreach ($line in ($stdout -split "`r?`n")) {
        if ($line.TrimStart().StartsWith('{')) { try { $result = $line | ConvertFrom-Json } catch {} }
    }
    if ($result -and $result.action -eq 'error' -and $result.requires_backup) {
        Show-ImportResult '发现已有改动，已保留原文件' '此目录的技能被改过，或不是由本包安装。可以先将特调迁到 user.md，再选择“备份后继续”。' $false
        $script:ui.BackupButton.Visibility = 'Visible'
    } elseif ($exitCode -eq 0 -and $result -and $result.action -in @('installed','already_current','check')) {
        $title = switch ($result.action) { 'installed' { '导入完成' }; 'already_current' { '已经是此包版本' }; 'check' { '安装文件校验通过' } }
        $body = '下一步：打开 Agent 的新会话，粘贴验证提示词。此结果确认文件已就位；AI 是否加载，需要在 Agent 中核对。'
        if ($result.PSObject.Properties['backup'] -and $result.backup) { $body += "`n旧技能完整备份：" + $result.backup }
        Show-ImportResult $title $body $true
        $script:prompt = "使用 letsgal-authoring。只读检查：核对实际读取的技能路径是否为 $($job.Target)；读取个人偏好 $($result.profile) 和工程 LETSGAL.md（不存在就明确说不存在）；插件 Skill 位于 $($result.plugins)，只按当前项目的插件 ID 和实际版本定位相关资料，不默认全部启用。定位当前工程与章节，说明写 JSON 前要查哪一页官方规范。不要修改文件或启动引擎。"
        $script:ui.CopyButton.Visibility = 'Visible'
        $script:ui.CopyButton.Content = '复制验证提示词'
    } elseif ($exitCode -eq 0 -and $result -and $result.action -eq 'uninstalled_to_backup') {
        Show-ImportResult '技能已移到备份' ("个人偏好与插件 Skill 均保留。备份位置：`n" + $result.backup) $true
    } elseif ($result -and $result.action -eq 'check') {
        Show-ImportResult '此位置尚未安装，或文件已有变化' '检查没有修改任何文件。可使用导入入口安装；已有改动会先受到保护。详细信息见下方。' $false
    } else {
        $message = if ($result -and $result.action -eq 'error') { $result.message } else { '请展开“详细信息”查看原因；也可按 README 手动导入。' }
        Show-ImportResult '操作未完成' $message $false
    }
    if ($result -and $result.PSObject.Properties['completion_warnings'] -and $result.completion_warnings) {
        $script:ui.ResultTitle.Text += '（有提示）'
        $script:ui.ResultPanel.Background = '#FFF2DE'
        $script:ui.ResultBody.Text += "`n" + ($result.completion_warnings -join "`n")
    }
    $script:window.UpdateLayout()
    $script:ui.ResultPanel.BringIntoView()
}

try {
    $notice = Get-RiskNotice
    $UserHome = Full-Path $UserHome
    Assert-OrdinaryPath $UserHome
    $statePath = Join-Path $UserHome '.letsgal-authoring/installer-state.json'
    $saved = Read-InstallerChoices $statePath
    if ($saved) {
        if (-not $Harness) { $Harness = $saved.Harness }
        if (-not $Scope) { $Scope = $saved.Scope }
        if (-not $ProjectPath) { $ProjectPath = $saved.ProjectPath }
        if (-not $SkillsDirectory) { $SkillsDirectory = $saved.SkillsDirectory }
        if (-not $DshHome -and $saved.PSObject.Properties['DshHome']) { $DshHome = $saved.DshHome }
    }
    if (-not $Harness) { $Harness = 'Codex' }
    if (-not $Scope) { $Scope = 'User' }
    try { $dshInfo = Get-DshHomeInfo $DshHome $UserHome }
    catch {
        # A stale DSH location must not prevent users of another Agent from opening the UI.
        $rawDshHome = $DshHome
        if (-not $rawDshHome) { $rawDshHome = [Environment]::GetEnvironmentVariable('DSH_HOME') }
        if (-not $rawDshHome) { $rawDshHome = Join-Path $UserHome '.dsh' }
        $dshInfo = [pscustomobject]@{Path=$rawDshHome;Source='原 DSH 路径不可用；使用 DSH 时请重新选择'}
    }
    [xml]$xaml = [IO.File]::ReadAllText((Join-Path $PSScriptRoot 'Import.xaml'))
    $reader = New-Object Xml.XmlNodeReader($xaml)
    try { $script:window = [Windows.Markup.XamlReader]::Load($reader) } finally { $reader.Close() }
    $script:window.Height = [Math]::Min(805, [Windows.SystemParameters]::WorkArea.Height - 32)
    foreach ($node in $xaml.SelectNodes('//*[@Name]')) { $script:ui[$node.Name] = $script:window.FindName($node.Name) }
    $script:ui.RiskSummary.Text = $notice.Summary
    $script:ui.RiskLegal.Text = $notice.Legal
    $script:ui.RiskDetails.Text = $notice.Text
    $choices = @(@('Codex','Codex'),@('Claude','Claude Code'),@('Cursor','Cursor'),@('Copilot','GitHub Copilot'),@('DSH','DSH'),@('Manual','其他 Agent'))
    foreach ($choice in $choices) {
        $item = New-Object Windows.Controls.ComboBoxItem
        $item.Tag = $choice[0]; $item.Content = $choice[1]
        [void]$script:ui.AgentBox.Items.Add($item)
        if ($choice[0] -eq $Harness) { $script:ui.AgentBox.SelectedItem = $item }
    }
    if ($script:ui.AgentBox.SelectedIndex -lt 0) { $script:ui.AgentBox.SelectedIndex = 0 }
    [void]$script:ui.ScopeBox.Items.Add('个人 · 所有项目')
    [void]$script:ui.ScopeBox.Items.Add('项目 · 仅此工程')
    $script:ui.ScopeBox.SelectedIndex = if ($Scope -eq 'Project') { 1 } else { 0 }
    $script:ui.ProjectBox.Text = $ProjectPath
    $script:ui.DshBox.Text = $dshInfo.Path
    $script:ui.DshHint.Text = $dshInfo.Source + '。选 DSH 的数据目录，不是程序安装目录。'
    $script:ui.ManualBox.Text = $SkillsDirectory
    $script:timer = New-Object Windows.Threading.DispatcherTimer
    $script:timer.Interval = [TimeSpan]::FromMilliseconds(180)
    $script:timer.Add_Tick({ try { Complete-ImportAction } catch { $script:timer.Stop(); Show-ImportResult '结果显示失败' $_.Exception.Message $false } })
    $script:ui.AgentBox.Add_SelectionChanged({ Update-Destination })
    $script:ui.ScopeBox.Add_SelectionChanged({ Update-Destination })
    foreach ($name in @('ProjectBox','DshBox','ManualBox')) { $script:ui[$name].Add_TextChanged({ Update-Destination }) }
    $script:ui.ProjectBrowse.Add_Click({ Select-Folder $script:ui.ProjectBox '选择要使用技能的项目文件夹' })
    $script:ui.DshBrowse.Add_Click({ Select-Folder $script:ui.DshBox '选择 DSH 数据文件夹（例如 .dsh）' })
    $script:ui.ManualBrowse.Add_Click({ Select-Folder $script:ui.ManualBox '选择 Agent 已配置的 skills 根目录' })
    $script:ui.ImportButton.Add_Click({ Start-ImportAction $InitialAction })
    $script:ui.CheckButton.Add_Click({ Start-ImportAction 'Check' })
    $script:ui.RemoveButton.Add_Click({ Start-ImportAction 'Uninstall' })
    $script:ui.BackupButton.Add_Click({ Start-ImportAction $script:lastAction $true })
    $script:ui.CopyButton.Add_Click({ try { [Windows.Clipboard]::SetText($script:prompt); $script:ui.CopyButton.Content = '已复制，去 Agent 粘贴' } catch { Show-ImportResult '剪贴板暂不可用' '请使用 README 中的验证提示词。' $false } })
    $script:window.Add_Closing({ param($sender,$eventArgs) if ($script:job) { $eventArgs.Cancel = $true; $script:ui.Footer.Text = '正在处理，请等待完成后关闭，以便保留操作结果。' } })
    $script:loading = $false
    Update-Destination
    if (-not $PrepareOnly) { [void]$script:window.ShowDialog() }
} catch {
    [void][Windows.MessageBox]::Show(('导入界面未能启动：' + $_.Exception.Message + "`n可按 README 使用命令行或手动导入。"), 'LetsGal 技能导入', 'OK', 'Error')
    exit 1
}
