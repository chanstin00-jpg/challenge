param(
    [string]$UniversityZip = "",
    [switch]$KeepArchives
)

$ErrorActionPreference = "Stop"

$PairUavRoot = $PSScriptRoot

if (-not $UniversityZip) {
    $UniversityZip = Join-Path $PairUavRoot "University-Release.zip"
}

if (-not (Test-Path -LiteralPath $UniversityZip)) {
    throw "University-Release.zip not found. Put it at $PairUavRoot or pass -UniversityZip <path>."
}

$ExtractRoot = Join-Path $PairUavRoot "University-Release"
if (Test-Path -LiteralPath $ExtractRoot) {
    Remove-Item -LiteralPath $ExtractRoot -Recurse -Force
}

Write-Host "Extracting University-Release.zip ..."
Expand-Archive -LiteralPath $UniversityZip -DestinationPath $PairUavRoot -Force

$TrainTourDir = Join-Path $PairUavRoot "train_tour"
New-Item -ItemType Directory -Force -Path $TrainTourDir | Out-Null

$DroneTrainDir = Join-Path $ExtractRoot "train\drone"
if (-not (Test-Path -LiteralPath $DroneTrainDir)) {
    throw "Expected drone training directory not found: $DroneTrainDir"
}

Write-Host "Copying University-1652 drone training images into train_tour ..."
Copy-Item -Path (Join-Path $DroneTrainDir "*") -Destination $TrainTourDir -Recurse -Force

Write-Host "Downloading PairUAV train/test JSON and test images from Hugging Face ..."
hf download --repo-type dataset YaxuanLi/UAVM_2026_test --local-dir $PairUavRoot

Write-Host "Extracting PairUAV archives ..."
tar -xf (Join-Path $PairUavRoot "train.tar") -C $PairUavRoot
tar -xf (Join-Path $PairUavRoot "test.tar") -C $PairUavRoot
tar -xf (Join-Path $PairUavRoot "test_tour.tar") -C $PairUavRoot

if (-not $KeepArchives) {
    Write-Host "Cleaning temporary archives ..."
    Remove-Item -LiteralPath (Join-Path $PairUavRoot "train.tar") -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath (Join-Path $PairUavRoot "test.tar") -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath (Join-Path $PairUavRoot "test_tour.tar") -Force -ErrorAction SilentlyContinue
    Remove-Item -LiteralPath $ExtractRoot -Recurse -Force -ErrorAction SilentlyContinue
}

Write-Host "PairUAV data preparation finished."
