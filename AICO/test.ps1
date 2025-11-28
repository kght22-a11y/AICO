# Navigate to repo root
cd c:\Users\Poop\Documents\GitHub\AICO

# Add git to PATH
$env:Path += ";C:\Program Files\Git\cmd"

# Commit
git add .
git commit -m "Restore project from aicogrok snapshot"

# Detect and run tests
$log = ".\test-output.log"
if (Test-Path .\package.json) {
  npm test 2>&1 | Tee-Object $log
} elseif ((Test-Path .\pyproject.toml) -Or (Test-Path .\pytest.ini) -Or (Get-ChildItem -Recurse -Filter "test_*.py" -ErrorAction SilentlyContinue)) {
  python -m pytest -q 2>&1 | Tee-Object $log
} elseif (Get-ChildItem -Recurse -Filter "*.csproj" -ErrorAction SilentlyContinue) {
  dotnet test 2>&1 | Tee-Object $log
} else {
  Write-Host "No test runner detected. Listing repo structure:"
  Get-ChildItem -Force
}