"""
AWS Environment Setup Script
Helps set up the initial AWS environment for LEF deployment
"""

import os
import sys
import yaml
import boto3
from pathlib import Path
from typing import Dict, Optional
from botocore.exceptions import ClientError

def setup_aws_environment():
    """Set up AWS environment for LEF deployment"""
    try:
        # Check for AWS credentials
        if not all([os.getenv('AWS_ACCESS_KEY_ID'), 
                   os.getenv('AWS_SECRET_ACCESS_KEY'),
                   os.getenv('AWS_REGION')]):
            print("Error: AWS credentials not found in environment variables")
            print("Please set the following environment variables:")
            print("  - AWS_ACCESS_KEY_ID")
            print("  - AWS_SECRET_ACCESS_KEY")
            print("  - AWS_REGION")
            sys.exit(1)

        # Initialize AWS session
        session = boto3.Session()
        sts = session.client('sts')
        
        # Verify credentials
        try:
            identity = sts.get_caller_identity()
            print(f"Successfully authenticated as: {identity['Arn']}")
        except ClientError as e:
            print(f"Error verifying AWS credentials: {str(e)}")
            sys.exit(1)

        # Create config directory if it doesn't exist
        config_dir = Path('aws_deploy/config')
        config_dir.mkdir(parents=True, exist_ok=True)

        # Copy template to actual config file if it doesn't exist
        template_path = config_dir / 'aws_config_template.yaml'
        config_path = config_dir / 'aws_config.yaml'
        
        if not config_path.exists():
            if template_path.exists():
                with open(template_path, 'r') as f:
                    config = yaml.safe_load(f)
                
                # Update config with current values
                config['aws_account_id'] = identity['Account']
                config['region'] = os.getenv('AWS_REGION')
                
                with open(config_path, 'w') as f:
                    yaml.dump(config, f, default_flow_style=False)
                print(f"Created AWS configuration file at: {config_path}")
            else:
                print("Error: AWS configuration template not found")
                sys.exit(1)

        # Create necessary directories
        dirs = [
            'aws_deploy/cloudformation',
            'aws_deploy/lambda',
            'aws_deploy/scripts',
            'logs'
        ]
        
        for dir_path in dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            print(f"Created directory: {dir_path}")

        print("\nAWS environment setup completed successfully!")
        print("\nNext steps:")
        print("1. Review and update aws_deploy/config/aws_config.yaml")
        print("2. Set up GitHub Actions secrets")
        print("3. Run deployment preparation script")
        
    except Exception as e:
        print(f"Error setting up AWS environment: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    setup_aws_environment() 