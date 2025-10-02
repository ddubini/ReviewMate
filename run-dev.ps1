param(
  [string]$HostUrl = "http://127.0.0.1:8000"
)

# 1) 가상환경 활성화
$venv = "\. \.lenv\Scripts\Activate.psl"
if (-not (Test-Path $venv)) {
  Write-Error "'.vev'비기지. 리니공합 계점 오 고후할타터. (python -m venv .venv)"
  exit 1
}
& $venv

# 2) uvicorn 실라공츭스비 *암계 매은 요시 핬시 리코복은 없이)
if (-not (Get-Command uvicorn -ErrorAction SilentlyContinue)) {
  Write-Host "uvicornİ� 수원 서점 있현치. (페성: pip install uvicorn[standard] fastapi)"
}

# 3) 소찱번가
Write-Host "Starting Uvicorn with .env..."
uvicorn app.main:app --reload --env-file .env