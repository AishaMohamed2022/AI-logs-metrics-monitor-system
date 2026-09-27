# ==============================================================================
# build_and_deploy.ps1 - Automated Build, Load, and K8s Deployment Script
# ==============================================================================

param (
    [string]$ImageTag = "latest"
)

$ErrorActionPreference = "Stop"

$ProjectRoot = Resolve-Path "$PSScriptRoot\.."
$BackendDir = "$ProjectRoot\backend"
$K8sDir = "$ProjectRoot\k8s"

Write-Host "=================================================" -ForegroundColor Cyan
Write-Host "   AIOps Platform - Build & Deploy Pipeline       " -ForegroundColor Cyan
Write-Host "=================================================" -ForegroundColor Cyan

# 1. Build Docker Image
Write-Host "`n[1/4] Building backend Docker image: aiops-backend:$ImageTag..." -ForegroundColor Yellow
docker build -t "aiops-backend:$ImageTag" -f "$BackendDir\Dockerfile" "$BackendDir"
if ($LASTEXITCODE -ne 0) {
    Write-Host "[-] Docker build failed!" -ForegroundColor Red
    exit 1
}
Write-Host "[+] Docker image aiops-backend:$ImageTag built successfully." -ForegroundColor Green

# 2. Check cluster provider and load image if required
Write-Host "`n[2/4] Checking cluster provider to make image available..." -ForegroundColor Yellow
$currentContext = (kubectl config current-context 2>$null)
Write-Host "Active Kubernetes Context: $currentContext" -ForegroundColor Cyan

if ($currentContext -eq "minikube") {
    Write-Host "Loading image into Minikube cluster..." -ForegroundColor Cyan
    minikube image load "aiops-backend:$ImageTag"
} elseif ($currentContext -like "*kind*") {
    $kindCluster = ($currentContext -split "-")[1]
    if (-not $kindCluster) { $kindCluster = "aiops-cluster" }
    Write-Host "Loading image into Kind cluster '$kindCluster'..." -ForegroundColor Cyan
    kind load docker-image "aiops-backend:$ImageTag" --name $kindCluster
} elseif ($currentContext -eq "docker-desktop") {
    Write-Host "[+] Docker Desktop shares the local engine image cache directly with Kubernetes." -ForegroundColor Green
} else {
    Write-Host "[i] Context '$currentContext' detected. Assuming image is locally accessible or using local registry." -ForegroundColor Yellow
}

# 3. Apply Kubernetes Manifests in Sequential Order
Write-Host "`n[3/4] Applying Kubernetes manifests from $K8sDir..." -ForegroundColor Yellow

$manifestFiles = @(
    "00-namespace.yaml",
    "01-configmaps.yaml",
    "02-secrets.yaml",
    "03-postgres-pvc.yaml",
    "03-postgres.yaml",
    "04-redis.yaml",
    "05-backend.yaml",
    "06-backend-service.yaml"
)

foreach ($manifest in $manifestFiles) {
    $manifestPath = Join-Path $K8sDir $manifest
    Write-Host "  -> Applying $manifest..." -ForegroundColor Cyan
    kubectl apply -f $manifestPath
}

# 4. Wait for Rollout Status
Write-Host "`n[4/4] Awaiting rollout completion in namespace 'aiops'..." -ForegroundColor Yellow

Write-Host "  -> Waiting for postgres deployment..." -ForegroundColor Cyan
kubectl rollout status deployment/postgres-deployment -n aiops --timeout=120s

Write-Host "  -> Waiting for redis deployment..." -ForegroundColor Cyan
kubectl rollout status deployment/redis-deployment -n aiops --timeout=120s

Write-Host "  -> Waiting for aiops-backend deployment..." -ForegroundColor Cyan
kubectl rollout status deployment/aiops-backend-deployment -n aiops --timeout=120s

Write-Host "`n=================================================" -ForegroundColor Green
Write-Host "   Deployment Finished! Current Cluster Resources" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Green
kubectl get all -n aiops

Write-Host "`nAccessing the application:" -ForegroundColor Cyan
Write-Host "  - Direct NodePort (if Docker Desktop): http://localhost:30080" -ForegroundColor White
Write-Host "  - Port-forward command: kubectl port-forward svc/backend-service 8000:8000 -n aiops" -ForegroundColor White
Write-Host "  - Swagger UI: http://localhost:8000/docs" -ForegroundColor White
Write-Host "  - Prometheus Metrics: http://localhost:8000/metrics" -ForegroundColor White
