# deploy_backend.ps1
# Script to package and deploy BharatPrice AI backend to AWS Lambda

$ErrorActionPreference = "Stop"

$FUNCTION_NAME="bharatprice-ai-backend"
$ROLE_NAME="bharatprice-ai-lambda-role"
$REGION="ap-south-1"
$ZIP_FILE="deployment_package.zip"

Write-Host "Creating deployment package..."
# 1. Package dependencies
if (Test-Path "package") { Remove-Item -Recurse -Force "package" }
New-Item -ItemType Directory -Force -Path "package" | Out-Null
& "venv\Scripts\pip.exe" install -r requirements.txt -t package

# 2. Copy app code
Copy-Item -Recurse -Force "app" "package\"

# 3. Zip it (requires PowerShell 5+)
if (Test-Path $ZIP_FILE) { Remove-Item -Force $ZIP_FILE }
Compress-Archive -Path "package\*" -DestinationPath $ZIP_FILE

Write-Host "Checking if IAM role exists..."
$roleExists = aws iam get-role --role-name $ROLE_NAME 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating IAM trust policy for Lambda..."
    $trustPolicy = '{
      "Version": "2012-10-17",
      "Statement": [
        {
          "Effect": "Allow",
          "Principal": {
            "Service": "lambda.amazonaws.com"
          },
          "Action": "sts:AssumeRole"
        }
      ]
    }'
    $trustPolicy | Out-File -Encoding UTF8 trust-policy.json
    
    Write-Host "Creating IAM Role..."
    aws iam create-role --role-name $ROLE_NAME --assume-role-policy-document file://trust-policy.json | Out-Null
    
    Write-Host "Attaching Basic Execution Policy..."
    aws iam attach-role-policy --role-name $ROLE_NAME --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole
}

$roleArn = (aws iam get-role --role-name $ROLE_NAME --query "Role.Arn" --output text)

Write-Host "Waiting a moment for IAM role to propagate..."
Start-Sleep -Seconds 10

Write-Host "Deploying to AWS Lambda..."
$lambdaExists = aws lambda get-function --function-name $FUNCTION_NAME 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating new Lambda function..."
    aws lambda create-function `
        --function-name $FUNCTION_NAME `
        --runtime python3.11 `
        --role $roleArn `
        --handler app.main.handler `
        --zip-file fileb://$ZIP_FILE `
        --timeout 30 `
        --memory-size 512 `
        --region $REGION | Out-Null
} else {
    Write-Host "Updating existing Lambda function code..."
    aws lambda update-function-code `
        --function-name $FUNCTION_NAME `
        --zip-file fileb://$ZIP_FILE `
        --region $REGION | Out-Null
}

Write-Host "Backend Deployment Attempt Complete!"
Write-Host "If this succeeded, you can now add an API Gateway trigger in the AWS Console."
