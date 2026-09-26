# Shared local notice; records delivery metadata, never presumed consent.
function Get-RiskNotice {
    $path = Join-Path $PSScriptRoot 'skills/letsgal-authoring/references/risk-notice.md'
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
        Summary='AI 可能误改、误删或泄露资料。请先备份作品并限制 Agent 可写范围；技能备份不包含作品。'
        Legal='在法律允许的最大范围内，作者与贡献者对使用本包造成的损失不承担任何责任；依法不得免除的责任及用户法定权利不受影响。'
        Sha256=$sha256
    }
}
