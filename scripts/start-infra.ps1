# Start local infrastructure (MongoDB, Redis, Ollama)
param(
    [switch]$PullModel
)

Set-Location (Join-Path $PSScriptRoot "..")

Write-Host "Starting infrastructure services..." -ForegroundColor Cyan
docker compose -f docker-compose.infra.yml up -d

if ($PullModel) {
    Write-Host "Pulling Ollama model llama3.2..." -ForegroundColor Cyan
    docker compose -f docker-compose.infra.yml exec ollama ollama pull llama3.2
}

Write-Host ""
Write-Host "Infrastructure ready:" -ForegroundColor Green
Write-Host "  MongoDB  -> localhost:27017"
Write-Host "  Redis    -> localhost:6379"
Write-Host "  Ollama   -> localhost:11434"
Write-Host ""
Write-Host "Next steps (see docs/LOCAL_DEV.md):" -ForegroundColor Yellow
Write-Host "  Terminal 1: cd backend; uvicorn app.main:app --reload --port 8000"
Write-Host "  Terminal 2: cd backend; celery -A app.workers.celery worker --queues=resume,scraping,matching --pool=solo"
Write-Host "  Terminal 3: cd backend; celery -A app.workers.celery beat"
Write-Host "  Terminal 4: npm run dev"
