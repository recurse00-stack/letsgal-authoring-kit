# Optional offline-workbench integration. The Skill installer itself needs no Python.
function Update-LocalWorkbench([string]$BundleRoot, [string]$UserArea) {
    $python = Get-Command python -ErrorAction SilentlyContinue
    if (-not $python) {
        $message = '主 Skill 已安装；自动整合 Wiki 需要 Python 3.10+。仍可打开发行包 MANUAL.html，安装 Python 后重运行安装器即可接入已有附属包。'
        $completionWarnings.Add($message); Write-Warning $message
        return
    }
    $runtime = Join-Path $BundleRoot 'maintenance/workbench_runtime.py'
    try {
        $output = & $python.Source -B -X utf8 $runtime setup --source $BundleRoot --user-area $UserArea 2>&1
        $code = $LASTEXITCODE
    } catch {
        $output = @($_.Exception.Message)
        $code = 1
    }
    if ($code -ne 0) {
        $message = '主 Skill 已安装，工作台更新未完成；保留现有资料。详情：' + ($output -join ' ')
        $completionWarnings.Add($message); Write-Warning $message
    } else {
        Write-Host ('本机总 Wiki：' + (Join-Path $UserArea 'workbench/MANUAL.html'))
    }
}
