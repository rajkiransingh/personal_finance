#!/bin/bash
# 🚀 This script is to just get the lambdas and s3 details from aws and a good way to save commands

# Variables
REGION="ap-south-1"

echo "adding the aws project profile"
export AWS_PROFILE=lambda-project

echo "Getting the list of S3 buckets..."
aws s3 ls

echo "Getting list of lambda functions available in region: ${REGION}"
aws lambda list-functions --region ${REGION} --query 'Functions[].FunctionName'