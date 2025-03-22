# LEF AWS Deployment

This directory contains the AWS deployment configuration and scripts for the Learning and Evolution Framework (LEF) project.

## Prerequisites

- AWS CLI installed and configured
- Python 3.8 or later
- AWS account with appropriate permissions
- AWS credentials configured

## Directory Structure

```
aws_deploy/
├── cloudformation/           # CloudFormation templates
│   └── ecological_awareness.yml
├── lambda/                  # Lambda function code
│   └── ecological_awareness.py
├── scripts/                 # Deployment scripts
│   └── deploy_ecological_awareness.py
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   ```bash
   export AWS_ACCESS_KEY_ID=your_access_key
   export AWS_SECRET_ACCESS_KEY=your_secret_key
   export AWS_REGION=us-west-2
   export ENVIRONMENT=dev  # or staging, prod
   ```

## Deployment

The deployment process creates the following AWS resources:

### Ecological Awareness Layer

- **Microsystem Layer**: DynamoDB table for direct interactions
- **Mesosystem Layer**: SQS queue for community connections
- **Exosystem Layer**: S3 bucket for external influences
- **Macrosystem Layer**: DynamoDB table for cultural patterns
- **Chronosystem Layer**: Kinesis stream for temporal evolution
- **Community Impact**: DynamoDB table for metrics
- **Ripple Effect**: SQS queue for tracking
- **Cultural Translation**: DynamoDB table for mappings
- **Mentorship**: DynamoDB table for development tracking
- **Ecological Mapping**: S3 bucket for system mapping
- **Recursive Feedback**: SQS queue for system feedback

### Lambda Function

The `ecological_awareness.py` Lambda function processes events from various layers and updates the corresponding resources.

## Deployment Process

1. Create Lambda ZIP file:
   ```bash
   python scripts/deploy_ecological_awareness.py
   ```

2. The script will:
   - Create a Lambda role with necessary permissions
   - Upload Lambda code to S3
   - Deploy CloudFormation stack with all resources

## Monitoring

- CloudWatch Logs: Lambda function logs
- CloudWatch Metrics: Resource utilization and performance
- X-Ray: Request tracing and analysis

## Security

- IAM roles with least privilege
- KMS encryption for sensitive data
- VPC security groups and NACLs
- CloudWatch alarms for security events

## Backup and Recovery

- DynamoDB point-in-time recovery
- S3 versioning and lifecycle policies
- Cross-region backup configuration

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests and linting
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 