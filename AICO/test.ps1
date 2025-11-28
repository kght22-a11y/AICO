$porcelain = git status --porcelain
if ($porcelain) {
  git commit -m "Restore project from aicogrok snapshot"
  Write-Host "Committed changes."
} else {
  Write-Host "No changes to commit."
}

# detect and run test runner, saving output
$log = ".\test-output.log"
if (Test-Path .\package.json) {
  $pkg = Get-Content .\package.json -Raw
  if ($pkg -match '"test"\s*:') {
    npm test 2>&1 | Tee-Object $log
  } else {
    Write-Host "package.json found but no test script. Inspect package.json." | Tee-Object $log
  }
} elseif (Test-Path .\pyproject.toml -or Test-Path .\pytest.ini -or (Get-ChildItem -Recurse -Filter "test_*.py" -ErrorAction SilentlyContinue)) {
  # prefer pytest if available
  python -m pytest -q 2>&1 | Tee-Object $log
} elseif (Get-ChildItem -Recurse -Filter "*.csproj" -ErrorAction SilentlyContinue) {
  dotnet test 2>&1 | Tee-Object $log
} else {
  Write-Host "No known test runner detected. Inspect repository." | Tee-Object $log
}

Write-Host "Test run finished. See $log"