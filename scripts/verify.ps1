$ErrorActionPreference = "Stop"

Write-Host "== Docker status ==" -ForegroundColor Cyan
docker compose ps

Write-Host "== Django checks ==" -ForegroundColor Cyan
docker compose exec backend python manage.py showmigrations
docker compose exec backend python manage.py makemigrations --check
docker compose exec backend python manage.py check

Write-Host "== Backend tests ==" -ForegroundColor Cyan
docker compose exec backend pytest

Write-Host "== Health endpoint ==" -ForegroundColor Cyan
try {
    $health = Invoke-RestMethod "http://localhost:8000/api/v1/health/"
    $health | ConvertTo-Json
} catch {
    Write-Error "Backend health check failed: $($_.Exception.Message)"
}

Write-Host "Verification commands completed." -ForegroundColor Green
