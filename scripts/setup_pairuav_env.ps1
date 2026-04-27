param(
    [string]$EnvName = "uavm_pairuav",
    [string]$PythonVersion = "3.10"
)

$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent $PSScriptRoot
$CondaHook = ((& conda shell.powershell hook) | Out-String)
Invoke-Expression $CondaHook

Write-Host "Creating conda environment $EnvName with Python $PythonVersion..."
if (-not (conda env list | Select-String -Pattern "^\s*$EnvName\s")) {
    conda create -n $EnvName -y python=$PythonVersion
} else {
    Write-Host "Environment $EnvName already exists. Reusing it."
}
conda activate $EnvName

Write-Host "Installing PyTorch with CUDA 12.8 wheels..."
python -m pip install --upgrade pip
python -m pip install torch==2.7.1 torchvision==0.22.1 torchaudio==2.7.1 --index-url https://download.pytorch.org/whl/cu128

Write-Host "Installing minimal PairUAV dependencies..."
python -m pip install -r (Join-Path $RepoRoot "requirements-pairuav-min.txt")

Write-Host "Downloading the DINO-ResNet pretrained backbone..."
$ModelDir = Join-Path $RepoRoot "models\dino_resnet"
New-Item -ItemType Directory -Force -Path $ModelDir | Out-Null
hf download Ramos-Ramos/dino-resnet-50 --local-dir $ModelDir

Write-Host "Checking CUDA visibility from PyTorch..."
python -c "import torch; print({'torch': torch.__version__, 'cuda': torch.version.cuda, 'cuda_available': torch.cuda.is_available(), 'device_count': torch.cuda.device_count(), 'device_name': torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu'})"

Write-Host "Environment setup finished."
