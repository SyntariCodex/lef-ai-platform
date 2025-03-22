#!/bin/bash

# Exit on error
set -e

# Configuration
PROJECT_NAME="lef"
ENVIRONMENT=${1:-development}
AWS_REGION="us-west-2"
TERRAFORM_DIR="terraform"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Starting deployment to ${ENVIRONMENT} environment...${NC}"

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}Error: AWS credentials not configured${NC}"
    exit 1
fi

# Build and push Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t ${PROJECT_NAME}:latest .

# Get ECR repository URL
ECR_REPO=$(aws ecr describe-repositories --repository-names ${PROJECT_NAME}-repo --query 'repositories[0].repositoryUri' --output text)

# Authenticate Docker to ECR
aws ecr get-login-password --region ${AWS_REGION} | docker login --username AWS --password-stdin ${ECR_REPO}

# Tag and push image
docker tag ${PROJECT_NAME}:latest ${ECR_REPO}:latest
docker push ${ECR_REPO}:latest

# Initialize Terraform
echo -e "${YELLOW}Initializing Terraform...${NC}"
cd ${TERRAFORM_DIR}
terraform init

# Apply Terraform configuration
echo -e "${YELLOW}Applying Terraform configuration...${NC}"
terraform apply \
    -var="environment=${ENVIRONMENT}" \
    -var="project_name=${PROJECT_NAME}" \
    -var="aws_region=${AWS_REGION}" \
    -auto-approve

# Get deployment outputs
echo -e "${YELLOW}Getting deployment outputs...${NC}"
ALB_DNS=$(terraform output -raw alb_dns_name)
ECS_SERVICE=$(terraform output -raw ecs_service_name)
ECS_CLUSTER=$(terraform output -raw ecs_cluster_name)

echo -e "${GREEN}Deployment completed successfully!${NC}"
echo -e "Application URL: http://${ALB_DNS}"
echo -e "ECS Service: ${ECS_SERVICE}"
echo -e "ECS Cluster: ${ECS_CLUSTER}"

# Wait for service to stabilize
echo -e "${YELLOW}Waiting for service to stabilize...${NC}"
aws ecs wait services-stable \
    --cluster ${ECS_CLUSTER} \
    --services ${ECS_SERVICE} \
    --region ${AWS_REGION}

echo -e "${GREEN}Service is now stable and ready to accept traffic!${NC}" 