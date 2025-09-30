#!/bin/bash

# Streamlined AWS Lambda Setup - No Scheduler, API-only approach
# This creates a Lambda function that your main app can call via AWS SDK

echo "🚀 Setting up AWS Lambda for Indian Market Data (No Scheduler)"
echo "=============================================================="

# Check AWS Profile
if [ -z "$AWS_PROFILE" ]; then
    echo "⚠️  AWS_PROFILE not set. Please run: export AWS_PROFILE=lambda-project"
    exit 1
fi

echo "✅ Using AWS Profile: $AWS_PROFILE"

# Variables - No S3 needed since you'll handle storage in your main app
REGION="ap-south-1"
FUNCTION_NAME="indian-stock-market-data-fetcher"
ROLE_NAME="IndianStockMarketDataFetcherRole"

ACCOUNT_ID=$(aws sts get-caller-identity --query 'Account' --output text)
echo "✅ Account ID: $ACCOUNT_ID"

echo "📊 Configuration:"
echo "  Function: $FUNCTION_NAME"
echo "  Region: $REGION (Mumbai - for Indian market access)"
echo "  No S3 bucket (data returned directly to mera paisa app)"
echo "  No EventBridge scheduler - we will use Ofelia Scheduler"
echo ""

echo "⚡ Creating minimal IAM role for Lambda..."
# Create trust policy
cat > trust-policy.json << EOF
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Principal": {"Service": "lambda.amazonaws.com"},
            "Action": "sts:AssumeRole"
        }
    ]
}
EOF

# Create role
aws iam create-role \
    --role-name $ROLE_NAME \
    --assume-role-policy-document file://trust-policy.json

# Only attach basic execution role (no S3 needed)
aws iam attach-role-policy \
    --role-name $ROLE_NAME \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

echo "✅ IAM role created (CloudWatch logs only)"

# Wait for role propagation
echo "⏳ Waiting for IAM role to propagate..."
sleep 10

echo "📦 Creating deployment package..."
mkdir -p ../lambda-package
cp ../aws/lambda_function.py lambda-package/
cp requirements.txt lambda-package/

cd lambda-package
echo "📦 Installing dependencies..."
pip install -r requirements.txt -t . --quiet --no-warn-script-location

# Create deployment ZIP
zip -r ../lambda-deployment.zip . -q
cd ..

# Get role ARN
ROLE_ARN=$(aws iam get-role --role-name $ROLE_NAME --query 'Role.Arn' --output text)

echo "🚀 Creating Lambda function (API-only, no scheduler)..."
aws lambda create-function \
    --function-name $FUNCTION_NAME \
    --runtime python3.9 \
    --role $ROLE_ARN \
    --handler lambda_function.lambda_handler \
    --zip-file fileb://lambda-deployment.zip \
    --timeout 300 \
    --memory-size 512 \
    --region $REGION \
    --description "Indian market data fetcher - returns data directly to our mera paisa app"

# Test the function
echo "🧪 Testing Lambda function..."
cat > test-payload.json << 'EOF'
{
    "investments": {
        "mutual_funds": ["120716", "119551"],
        "stocks": ["RELIANCE", "TCS"],
        "indices": ["^NSEI"]
    }
}
EOF

aws lambda invoke \
    --function-name $FUNCTION_NAME \
    --payload file://test-payload.json \
    --region $REGION \
    response.json

# Show results
echo ""
echo "🎉 Deployment Complete!"
echo "======================="
echo "✅ Lambda Function: $FUNCTION_NAME"
echo "✅ Region: $REGION"
echo "✅ No S3 bucket (data returned directly)"
echo "✅ No scheduler (use your Ofelia setup)"

echo ""
echo "📋 Test Result:"
if [ -f response.json ]; then
    cat response.json | jq '.' 2>/dev/null || cat response.json
fi

# Create .env file for your integration
#cat > .env << EOF
## AWS Lambda Configuration
#AWS_REGION=$REGION
#AWS_PROFILE=$AWS_PROFILE
#LAMBDA_FUNCTION_NAME=$FUNCTION_NAME
#
## No S3 bucket - data returned directly
## Use this function ARN in your Python app:
#LAMBDA_FUNCTION_ARN=arn:aws:lambda:$REGION:$ACCOUNT_ID:function:$FUNCTION_NAME
#EOF
#
#echo ""
#echo "✅ Configuration saved to .env"

# Cleanup
rm trust-policy.json lambda-deployment.zip test-payload.json
rm -rf lambda-package
rm -f response.json

echo ""
echo "🔗 Integration Details:"
echo "Function ARN: arn:aws:lambda:$REGION:$ACCOUNT_ID:function:$FUNCTION_NAME"
echo "Region: $REGION"
echo "Function Name: $FUNCTION_NAME"
echo ""
echo "🚀 Ready to integrate with your main Python app!"
echo "Use the Python integration code provided separately."
