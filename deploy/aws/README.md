# LEF AWS Deployment

This directory contains the infrastructure and deployment configuration for the LEF application on AWS.

## Prerequisites

- AWS CLI installed and configured with appropriate credentials
- Docker installed and running
- Terraform installed (version 1.0.0 or later)
- Python 3.11 or later

## Infrastructure Components

The deployment uses the following AWS services:

- Amazon ECS (Fargate) for container orchestration
- Amazon ECR for container registry
- Application Load Balancer for traffic distribution
- Amazon VPC for networking
- AWS Systems Manager Parameter Store for configuration
- CloudWatch Logs for logging

## Directory Structure

```
deploy/aws/
├── terraform/           # Terraform configuration files
│   ├── main.tf         # Main infrastructure configuration
│   ├── variables.tf    # Variable definitions
│   └── outputs.tf      # Output definitions
├── deploy.sh           # Deployment script
└── README.md          # This file
```

## Deployment Steps

1. Configure AWS credentials:
   ```bash
   aws configure
   ```

2. Make the deployment script executable:
   ```bash
   chmod +x deploy.sh
   ```

3. Run the deployment script:
   ```bash
   ./deploy.sh [environment]
   ```
   Where `[environment]` is optional and defaults to "development".

## Environment Variables

The following environment variables are used in the deployment:

- `ENVIRONMENT`: The deployment environment (development, staging, production)
- `PROJECT_NAME`: The name of the project (defaults to "lef")
- `AWS_REGION`: The AWS region to deploy to (defaults to "us-west-2")

## Infrastructure Details

### VPC Configuration
- CIDR: 10.0.0.0/16
- 3 Availability Zones
- Private and public subnets
- NAT Gateway for private subnet internet access

### ECS Configuration
- Fargate launch type
- 256 CPU units
- 512 MB memory
- Container port: 8000

### Security
- Security groups for ALB and ECS tasks
- IAM roles for ECS tasks
- Secure parameter storage in SSM

## Monitoring and Logging

- Container insights enabled on ECS cluster
- CloudWatch log group for application logs
- Health checks configured on ALB and containers

## Cleanup

To destroy the infrastructure:

```bash
cd terraform
terraform destroy
```

## Troubleshooting

1. Check CloudWatch logs:
   ```bash
   aws logs get-log-events --log-group-name /ecs/lef
   ```

2. Check ECS service status:
   ```bash
   aws ecs describe-services --cluster lef-cluster --services lef-service
   ```

3. Check ALB health:
   ```bash
   aws elbv2 describe-target-health --target-group-arn <target-group-arn>
   ```

## Support

For issues or questions, please contact the development team. 