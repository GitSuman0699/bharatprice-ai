# deploy_backend.ps1
# Script to package and deploy BharatPrice AI backend to AWS Lambda + API Gateway
# Handles Windows → Linux cross-compilation for pydantic_core native binaries

$ErrorActionPreference = "Stop"

# ── Refresh PATH so aws CLI is available ─────────────────────────
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
$env:PAGER = ""
$env:AWS_PAGER = ""

# ── Configuration ────────────────────────────────────────────────
$FUNCTION_NAME = "bharatprice-ai-backend"
$ROLE_NAME     = "bharatprice-ai-lambda-role"
$API_NAME      = "bharatprice-api"
$REGION        = "ap-south-1"
$ZIP_FILE      = "deployment_package.zip"
$RUNTIME       = "python3.11"

# ── Load env vars from .env for Lambda configuration ─────────────
$envVars = @{}
if (Test-Path ".env") {
    Get-Content ".env" | ForEach-Object {
        if ($_ -match "^\s*([^#][^=]+)=(.*)$") {
            $envVars[$matches[1].Trim()] = $matches[2].Trim()
        }
    }
}

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "  BharatPrice AI — Backend Deployer  " -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# ── Step 1: Package Dependencies ─────────────────────────────────
Write-Host "[1/6] Packaging dependencies..." -ForegroundColor Yellow
if (Test-Path "package") { Remove-Item -Recurse -Force "package" }
if (Test-Path "linux_wheel") { Remove-Item -Recurse -Force "linux_wheel" }
New-Item -ItemType Directory -Force -Path "package" | Out-Null

# Install all deps (Windows binaries for pure-python + native)
& "venv\Scripts\pip.exe" install -r requirements.txt -t package --quiet 2>&1 | Out-Null

# Fix: Replace pydantic_core with Linux-compatible binary
# Lambda runs on Amazon Linux — Windows .pyd files won't work
Write-Host "       Fixing pydantic_core for Linux..."
Remove-Item -Recurse -Force "package\pydantic_core" -ErrorAction SilentlyContinue
New-Item -ItemType Directory -Force -Path "linux_wheel" | Out-Null
& "venv\Scripts\pip.exe" download --dest linux_wheel --platform manylinux_2_17_x86_64 --python-version 3.11 --only-binary=:all: --no-deps pydantic_core==2.23.2 --quiet 2>&1 | Out-Null
$whl = Get-ChildItem "linux_wheel" -Filter "*.whl" | Select-Object -First 1
$zipPath = "$($whl.FullName).zip"
Copy-Item $whl.FullName $zipPath
Expand-Archive -Path $zipPath -DestinationPath "linux_wheel\extracted" -Force
Copy-Item -Recurse -Force "linux_wheel\extracted\pydantic_core" "package\"
Remove-Item -Recurse -Force "linux_wheel"

# Copy app code
Copy-Item -Recurse -Force "app" "package\"

# ── Step 2: Create ZIP ───────────────────────────────────────────
Write-Host "[2/6] Creating ZIP archive..." -ForegroundColor Yellow
if (Test-Path $ZIP_FILE) { Remove-Item -Force $ZIP_FILE }
Compress-Archive -Path "package\*" -DestinationPath $ZIP_FILE

$zipSize = [math]::Round((Get-Item $ZIP_FILE).Length / 1MB, 1)
Write-Host "       Package size: ${zipSize} MB"

# ── Step 3: IAM Role ─────────────────────────────────────────────
Write-Host "[3/6] Setting up IAM role..." -ForegroundColor Yellow
$roleArn = $null
try {
    $roleArn = aws iam get-role --role-name $ROLE_NAME --query "Role.Arn" --output text --no-cli-pager 2>$null
} catch {}

if (-not $roleArn -or $roleArn -eq "None") {
    Write-Host "       Creating IAM role..."
    $trustPolicy = '{"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"lambda.amazonaws.com"},"Action":"sts:AssumeRole"}]}'
    $trustPolicy | Out-File -Encoding ascii trust-policy.json
    aws iam create-role --role-name $ROLE_NAME --assume-role-policy-document file://trust-policy.json --no-cli-pager | Out-Null
    aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole --no-cli-pager
    Write-Host "       Waiting 10s for IAM propagation..."
    Start-Sleep -Seconds 10
    $roleArn = aws iam get-role --role-name $ROLE_NAME --query "Role.Arn" --output text --no-cli-pager
    Remove-Item -Force "trust-policy.json" -ErrorAction SilentlyContinue
} else {
    Write-Host "       IAM role already exists."
}
Write-Host "       Role ARN: $roleArn"

# ── Step 4: Lambda Function ──────────────────────────────────────
Write-Host "[4/6] Deploying Lambda function..." -ForegroundColor Yellow

# Write env vars to file (avoids PowerShell JSON escaping issues)
$envObj = @{
    Variables = @{
        DATA_GOV_API_KEY = if ($envVars["DATA_GOV_API_KEY"]) { $envVars["DATA_GOV_API_KEY"] } else { "" }
        API_SECRET_KEY   = if ($envVars["API_SECRET_KEY"])   { $envVars["API_SECRET_KEY"] }   else { "" }
        ALLOWED_HOSTS    = if ($envVars["ALLOWED_HOSTS"])    { $envVars["ALLOWED_HOSTS"] }    else { "*" }
        USE_LOCAL_DATA   = "true"
        USE_REAL_PRICES  = "true"
    }
}
$envObj | ConvertTo-Json -Compress | Out-File -Encoding ascii env.json

$lambdaExists = $null
try {
    $lambdaExists = aws lambda get-function --function-name $FUNCTION_NAME --region $REGION --no-cli-pager 2>$null
} catch {}

if (-not $lambdaExists) {
    Write-Host "       Creating new Lambda function..."
    aws lambda create-function `
        --function-name $FUNCTION_NAME `
        --runtime $RUNTIME `
        --role $roleArn `
        --handler app.main.handler `
        --zip-file fileb://$ZIP_FILE `
        --timeout 30 `
        --memory-size 512 `
        --region $REGION `
        --environment file://env.json `
        --no-cli-pager | Out-Null
} else {
    Write-Host "       Updating existing Lambda code..."
    aws lambda update-function-code `
        --function-name $FUNCTION_NAME `
        --zip-file fileb://$ZIP_FILE `
        --region $REGION `
        --no-cli-pager | Out-Null

    Write-Host "       Waiting for code update..."
    Start-Sleep -Seconds 5

    Write-Host "       Updating Lambda config (env vars)..."
    aws lambda update-function-configuration `
        --function-name $FUNCTION_NAME `
        --environment file://env.json `
        --region $REGION `
        --no-cli-pager | Out-Null
}

Remove-Item -Force "env.json" -ErrorAction SilentlyContinue

# ── Step 5: API Gateway (HTTP API) ───────────────────────────────
Write-Host "[5/6] Setting up API Gateway..." -ForegroundColor Yellow

$apiId = aws apigatewayv2 get-apis --query "Items[?Name=='$API_NAME'].ApiId" --output text --region $REGION --no-cli-pager 2>$null
if (-not $apiId -or $apiId -eq "None" -or $apiId.Trim() -eq "") {
    Write-Host "       Creating HTTP API..."
    $lambdaArn = aws lambda get-function --function-name $FUNCTION_NAME --query "Configuration.FunctionArn" --output text --region $REGION --no-cli-pager

    $apiResult = aws apigatewayv2 create-api --name $API_NAME --protocol-type HTTP --target $lambdaArn --region $REGION --no-cli-pager | ConvertFrom-Json
    $apiId = $apiResult.ApiId

    # Grant API Gateway permission to invoke Lambda
    $accountId = aws sts get-caller-identity --query "Account" --output text --no-cli-pager
    aws lambda add-permission `
        --function-name $FUNCTION_NAME `
        --statement-id apigateway-invoke `
        --action lambda:InvokeFunction `
        --principal apigateway.amazonaws.com `
        --source-arn "arn:aws:execute-api:${REGION}:${accountId}:${apiId}/*" `
        --region $REGION `
        --no-cli-pager | Out-Null
    Write-Host "       API created and linked to Lambda."
} else {
    Write-Host "       API Gateway already exists: $apiId"
}

$apiUrl = "https://${apiId}.execute-api.${REGION}.amazonaws.com"

# ── Step 6: Done! ────────────────────────────────────────────────
Write-Host ""
Write-Host "=====================================" -ForegroundColor Green
Write-Host "  Deployment Complete!               " -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Green
Write-Host ""
Write-Host "API URL: $apiUrl" -ForegroundColor Cyan
Write-Host ""
Write-Host "Test it:"
Write-Host "  Invoke-RestMethod $apiUrl/"
Write-Host "  Invoke-RestMethod $apiUrl/health"
Write-Host "  Invoke-RestMethod -Uri '$apiUrl/api/products' -Headers @{'X-API-Key'='YOUR_KEY'}"
Write-Host ""

# Clean up
if (Test-Path "package") { Remove-Item -Recurse -Force "package" }
