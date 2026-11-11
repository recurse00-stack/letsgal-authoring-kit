# Shared local notice; records delivery metadata, never presumed consent.
function Get-RiskNotice {
    $path = Join-Path $PSScriptRoot 'RISK-NOTICE.md'
    Assert-OptionalFile $path
    $bytes = [IO.File]::ReadAllBytes($path)
    $content = [Text.Encoding]::UTF8.GetString($bytes)
    if ($content -notmatch '(?m)^说明版本：([0-9.\-]+)\r?$') { throw 'Risk notice is missing its version; use a complete distribution.' }
    $version = $Matches[1]
    $algorithm = [Security.Cryptography.SHA256]::Create()
    try { $sha256 = ([BitConverter]::ToString($algorithm.ComputeHash($bytes))).Replace('-','').ToLowerInvariant() }
    finally { $algorithm.Dispose() }
    return [pscustomobject]@{
        Version=$version; Path=$path; Text=$content
        Summary='先备份作品并设置 Agent 可写范围；安装器备份 Skill，作品和个人资料需另行备份。'
        Legal='本项目采用 MIT 许可证；许可与责任条款见随包 LICENSE。'
        Sha256=$sha256
    }
}
