$dockerExe = "C:\Program Files\Docker\Docker\resources\bin\docker.exe"

if (-not (Test-Path $dockerExe)) {
    Write-Error "Docker executable not found at $dockerExe"
    exit 1
}

& $dockerExe @args
