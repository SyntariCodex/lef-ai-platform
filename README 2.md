# LEF Deployment

This repository contains the infrastructure and deployment code for the LEF project.

## Prerequisites

- Python 3.9+
- AWS CLI
- Git LFS
- GitHub account with repository access

## Setup

1. Clone the repository:
```bash
git clone https://github.com/zmoore/lef-deployment.git
cd lef-deployment
```

2. Install dependencies:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

3. Configure AWS credentials:
```bash
python aws_deploy/configure_aws.py
```

4. Set up GitHub Actions:
   - Go to your repository settings
   - Navigate to Secrets and Variables > Actions
   - Add a new secret `AWS_ROLE_ARN` with your AWS role ARN

## Infrastructure

The infrastructure is defined using AWS CloudFormation and includes:
- DynamoDB table for data storage
- S3 bucket for file storage
- Lambda function for processing
- CloudWatch for monitoring and logging
- IAM roles and policies

## Deployment

The project uses GitHub Actions for automated deployment. The workflow:
1. Triggers on push to main branch or manual dispatch
2. Supports multiple environments (dev/staging/prod)
3. Deploys infrastructure using CloudFormation
4. Updates Lambda function code
5. Verifies deployment

To deploy manually:
1. Go to Actions tab in GitHub
2. Select "AWS Deployment" workflow
3. Click "Run workflow"
4. Choose environment and trigger deployment

## Monitoring

- CloudWatch Logs: `/aws/lambda/lef-{environment}-processor`
- CloudWatch Metrics: Custom metrics in `LEF` namespace
- CloudWatch Dashboard: `lef-{environment}-dashboard`

## Backup and Recovery

Automated backups are configured for:
- DynamoDB: Point-in-time recovery
- S3: Versioning enabled
- Lambda: Code versions maintained

## Security

- All resources use encryption at rest
- S3 bucket blocks public access
- IAM roles follow principle of least privilege
- GitHub Actions uses OIDC for secure authentication

## Contributing

1. Create a new branch
2. Make changes
3. Submit a pull request
4. Ensure CI checks pass

## License

This project is proprietary and confidential. 