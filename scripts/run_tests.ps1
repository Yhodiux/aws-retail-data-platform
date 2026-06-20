$ErrorActionPreference = "Stop"

$projectRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$sparkImage = "apache/spark:3.5.4"

docker image inspect $sparkImage *> $null
if ($LASTEXITCODE -ne 0) {
    docker pull $sparkImage
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to pull Docker image $sparkImage"
    }
}

docker run --rm `
    --volume "${projectRoot}:/workspace" `
    --workdir /workspace `
    --env PYTHONPATH=/opt/spark/python:/opt/spark/python/lib/py4j-0.10.9.7-src.zip:/workspace/scripts `
    --env PYTHONDONTWRITEBYTECODE=1 `
    --env PYTHONWARNINGS=ignore::ResourceWarning `
    --env SPARK_LOCAL_IP=127.0.0.1 `
    $sparkImage `
    bash -lc "python3 -m unittest discover -s tests -v"

if ($LASTEXITCODE -ne 0) {
    throw "PySpark tests failed with exit code $LASTEXITCODE"
}
