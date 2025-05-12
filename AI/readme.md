https://coursera.org/share/a3ba86b75ae3d63064d87073fcb112e6



if (!(Test-Path $PROFILE)) {
    New-Item -Type File -Path $PROFILE -Force
}
notepad $PROFILE


# 自动将 Terraform 所在目录添加到 PATH（在你的情况下是 C:\abc\usr）
$env:Path += ";C:\abc\usr"


