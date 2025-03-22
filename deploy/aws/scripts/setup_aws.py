import os
import yaml
import boto3
import logging
from typing import Dict, Any
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class AWSSetup:
    def __init__(self):
        self.config = self.load_config()
        self.verify_credentials()
        self.setup_environment()

    def load_config(self) -> Dict[str, Any]:
        """Load AWS configuration from YAML file."""
        config_path = os.path.join(os.path.dirname(__file__), '../config/aws_config.yaml')
        try:
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Error loading config: {str(e)}")
            raise

    def verify_credentials(self) -> None:
        """Verify AWS credentials are properly configured."""
        try:
            # Check for required environment variables
            required_vars = ['AWS_ACCESS_KEY_ID', 'AWS_SECRET_ACCESS_KEY', 'AWS_REGION']
            missing_vars = [var for var in required_vars if not os.getenv(var)]
            
            if missing_vars:
                raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")
            
            # Verify credentials by making a test call
            sts = boto3.client('sts')
            identity = sts.get_caller_identity()
            logger.info(f"Verified AWS credentials for account: {identity['Account']}")
            
        except Exception as e:
            logger.error(f"Error verifying AWS credentials: {str(e)}")
            raise

    def setup_environment(self) -> None:
        """Set up the AWS environment with required directories and files."""
        try:
            # Create necessary directories
            directories = [
                'cloudformation',
                'lambda',
                'scripts',
                'logs',
                'config'
            ]
            
            for directory in directories:
                os.makedirs(directory, exist_ok=True)
                logger.info(f"Created directory: {directory}")
            
            # Copy template configuration
            template_path = os.path.join(os.path.dirname(__file__), '../config/aws_config_template.yaml')
            config_path = os.path.join(os.path.dirname(__file__), '../config/aws_config.yaml')
            
            if not os.path.exists(config_path):
                with open(template_path, 'r') as src, open(config_path, 'w') as dst:
                    dst.write(src.read())
                logger.info("Created aws_config.yaml from template")
            
            # Update configuration with current AWS account
            self.update_config_with_account()
            
            logger.info("AWS environment setup completed successfully")
            
        except Exception as e:
            logger.error(f"Error setting up environment: {str(e)}")
            raise

    def update_config_with_account(self) -> None:
        """Update configuration with current AWS account information."""
        try:
            sts = boto3.client('sts')
            identity = sts.get_caller_identity()
            
            # Update account ID in config
            self.config['aws']['account_id'] = identity['Account']
            
            # Write updated config back to file
            config_path = os.path.join(os.path.dirname(__file__), '../config/aws_config.yaml')
            with open(config_path, 'w') as f:
                yaml.dump(self.config, f, default_flow_style=False)
            
            logger.info(f"Updated configuration with AWS account ID: {identity['Account']}")
            
        except Exception as e:
            logger.error(f"Error updating configuration: {str(e)}")
            raise

def main():
    """Main function to run the AWS setup."""
    try:
        setup = AWSSetup()
        logger.info("AWS setup completed successfully")
    except Exception as e:
        logger.error(f"AWS setup failed: {str(e)}")
        raise

if __name__ == '__main__':
    main() 