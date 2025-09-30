#!/bin/bash
# 🚀 Clean Lambda Deployment Builder for indian-stock-market-data-fetcher

# Variables
FUNCTION_NAME="indian-stock-market-data-fetcher"
S3_BUCKET="lambda-deployments-rajkiran-998846731555-1759143167"
REGION="ap-south-1"
#LAMBDA_LAYER_ARN="arn:aws:lambda:ap-south-1:336392948345:layer:AWSSDKPandas-Python311-Arm64:17"  # Replace with your numpy/pandas layer ARN
PYTHON_DEPS="yfinance"

echo "adding the aws project profile"
export AWS_PROFILE=lambda-project

# Step 0: Clean old folders
rm -rf lambda-package lambda-deployment.zip

# Step 1: Prepare package folder
mkdir lambda-package
cp aws/lambda_function.py lambda-package/

# Step 2: Install lightweight dependencies
echo "📦 Installing minimal dependencies..."
pip install $PYTHON_DEPS -t lambda-package/ --quiet

# Step 3: Install yfinance WITHOUT pandas/numpy (layer will provide them)
echo "📦 Installing mfTool without heavy deps..."
#pip install mftool==3.0 -t lambda-package/ --quiet
#pip install httpx==0.24.1 certifi==2025.8.3 charset-normalizer==3.2.0 -t lambda-package/ --quiet
#pip install beautifulsoup4==4.12.3 -t lambda-package/ --quiet
#pip install lxml==5.3.0 -t lambda-package/ --quiet
#pip install yfinance==0.2.38 -t lambda-package/ --quiet

# Step 4: Create deployment ZIP
echo "📦 Creating ZIP..."
cd lambda-package
zip -r ../lambda-deployment.zip . -q
cd ..

## Step 5: Upload ZIP to S3
#echo "☁️  Uploading to S3..."
#aws s3 cp lambda-deployment.zip s3://$S3_BUCKET/
#
## Step 6: Update Lambda function code
#echo "🚀 Updating Lambda function..."
#aws lambda update-function-code \
#    --function-name $FUNCTION_NAME \
#    --s3-bucket $S3_BUCKET \
#    --s3-key lambda-deployment.zip \
#    --region $REGION
#
## Step 7: Attach Layer
#echo "🧩 Attaching numpy/pandas Layer..."
#aws lambda update-function-configuration \
#    --function-name $FUNCTION_NAME \
#    --layers $LAMBDA_LAYER_ARN \
#    --region $REGION
#
#echo "✅ Deployment complete! Your function is ready."
