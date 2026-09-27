# ==============================================================================
# setup_cluster.ps1 - Local Kubernetes Cluster Bootstrap Helper
# Supports: Docker Desktop Kubernetes, Minikube, and Kind
# ==============================================================================

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "   AIOps Platform - Local Cluster Initialization  " -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# 1. Check Docker Daemon
Write-Host "`n[Step 1/3] Checking Docker Engine status..." -ForegroundColor Yellow
$dockerPing = docker info 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[-] Docker engine is NOT running!" -ForegroundColor Red
    Write-Host "    Please start Docker Desktop and ensure the engine is running, then re-run this script." -ForegroundColor White
    exit 1
} else {
    Write-Host "[+] Docker engine is running." -ForegroundColor Green
}

# 2. Check kubectl availability
Write-Host "`n[Step 2/3] Checking kubectl..." -ForegroundColor Yellow
if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
    Write-Host "[-] kubectl is not found in PATH." -ForegroundColor Red
    exit 1
} else {
    $k8sVersion = kubectl version --client -o json 2>$null | ConvertFrom-Json
    Write-Host "[+] kubectl client found: $($k8sVersion.clientVersion.gitVersion)" -ForegroundColor Green
}

# 3. Detect and configure Cluster provider
Write-Host "`n[Step 3/3] Inspecting available Kubernetes cluster providers..." -ForegroundColor Yellow

# Check current kubectl context
$currentContext = (kubectl config current-context 2>$null)
Write-Host "Current kubectl context: '$currentContext'" -ForegroundColor Cyan

if ($currentContext -eq "docker-desktop") {
    Write-Host "[+] Docker Desktop Kubernetes is currently active." -ForegroundColor Green
    Write-Host "    Testing cluster connectivity..." -ForegroundColor Cyan
    kubectl cluster-info
    if ($LASTEXITCODE -eq 0) {
        Write-Host "`n[SUCCESS] Local cluster is healthy and ready for deployment!" -ForegroundColor Green
        exit 0
    }
}

# Check if Minikube is installed
$hasMinikube = Get-Command minikube -ErrorAction SilentlyContinue
# Check if Kind is installed
$hasKind = Get-Command kind -ErrorAction SilentlyContinue

Write-Host "`nCluster Options:" -ForegroundColor White
Write-Host "  1. Docker Desktop Kubernetes (Recommended if Docker Desktop is already installed)" -ForegroundColor Gray
Write-Host "     -> Open Docker Desktop Settings -> Kubernetes -> Check 'Enable Kubernetes' -> Apply & Restart" -ForegroundColor Gray
Write-Host "  2. Minikube: Run 'minikube start --driver=docker'" -ForegroundColor Gray
Write-Host "  3. Kind: Run 'kind create cluster --name aiops-cluster'" -ForegroundColor Gray

if ($hasMinikube) {
    Write-Host "`n[i] Minikube was detected. Starting Minikube cluster with docker driver..." -ForegroundColor Cyan
    minikube start --driver=docker
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Minikube cluster started successfully!" -ForegroundColor Green
        exit 0
    }
} elseif ($hasKind) {
    Write-Host "`n[i] Kind was detected. Creating Kind cluster 'aiops-cluster'..." -ForegroundColor Cyan
    kind create cluster --name aiops-cluster
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[SUCCESS] Kind cluster created successfully!" -ForegroundColor Green
        exit 0
    }
} else {
    Write-Host "`n[!] Neither Minikube nor Kind binary found in PATH." -ForegroundColor Yellow
    Write-Host "    Recommended next steps:" -ForegroundColor White
    Write-Host "    - Option A: In Docker Desktop, go to Settings -> Kubernetes -> check 'Enable Kubernetes' -> click 'Apply & restart'." -ForegroundColor White
    Write-Host "    - Option B: Install Minikube using: winget install Kubernetes.minikube" -ForegroundColor White
    Write-Host "    - Option C: Install Kind using: winget install Kubernetes.kind" -ForegroundColor White
}
