# Add git to PATH if needed (one-time)
$env:Path += ";C:\Program Files\Git\cmd"

# Commit
git add .
git commit -m "Restore project from aicogrok snapshot"

# Run tests (fixed syntax)
$log = ".\test-output.log"
if (Test-Path .\package.json) {
  $pkg = Get-Content .\package.json -Raw
  if ($pkg -match '"test"\s*:') {
    npm test 2>&1 | Tee-Object $log
  }
} elseif ((Test-Path .\pyproject.toml) -Or (Test-Path .\pytest.ini) -Or (Get-ChildItem -Recurse -Filter "test_*.py" -ErrorAction SilentlyContinue)) {
  python -m pytest -q 2>&1 | Tee-Object $log
} elseif (Get-ChildItem -Recurse -Filter "*.csproj" -ErrorAction SilentlyContinue) {
  dotnet test 2>&1 | Tee-Object $log
} else {
  Write-Host "No test runner detected."
}
Get-Content $log -Tail 100