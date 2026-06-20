$ErrorActionPreference = "Stop"

$builder = Join-Path $PSScriptRoot "build_common_zip.py"

python $builder
if ($LASTEXITCODE -ne 0) {
    throw "Unable to build libs/common.zip"
}
