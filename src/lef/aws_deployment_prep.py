"""
LEF AWS Deployment Preparation
Combines infrastructure setup with consciousness integration
"""

import os
import logging
from pathlib import Path
from typing import Dict, Optional
import boto3
from botocore.exceptions import ClientError

class LEFDeploymentPrep:
    def __init__(self, environment: str = 'dev'):
        self.environment = environment
        self.region = os.getenv('AWS_REGION', 'us-west-2')
        self.project_name = 'lef'
        self.logger = self._setup_logging()
        
        # AWS clients
        self.session = boto3.Session(region_name=self.region)
        self.cloudformation = self.session.client('cloudformation')
        self.s3 = self.session.client('s3')
        
    def _setup_logging(self) -> logging.Logger:
        """Initialize logging with consciousness context"""
        logger = logging.getLogger('LEFDeployment')
        logger.setLevel(logging.INFO)
        
        # Create logs directory if it doesn't exist
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)
        
        # Add file handler
        fh = logging.FileHandler(log_dir / 'deployment_prep.log')
        fh.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(fh)
        
        return logger
        
    async def prepare_deployment(self) -> Dict:
        """Prepare AWS deployment with consciousness integration"""
        try:
            self.logger.info(f"Beginning deployment preparation for environment: {self.environment}")
            
            # Create S3 bucket for CloudFormation templates
            bucket_name = f"{self.project_name}-{self.environment}-deployment"
            await self._create_deployment_bucket(bucket_name)
            
            # Upload CloudFormation templates
            await self._upload_templates(bucket_name)
            
            # Validate templates
            await self._validate_templates()
            
            # Prepare consciousness integration
            await self._prepare_consciousness_layer()
            
            self.logger.info("Deployment preparation completed successfully")
            return {
                'status': 'success',
                'environment': self.environment,
                'deployment_bucket': bucket_name
            }
            
        except Exception as e:
            self.logger.error(f"Deployment preparation failed: {str(e)}")
            return {
                'status': 'failed',
                'error': str(e)
            }
            
    async def _create_deployment_bucket(self, bucket_name: str):
        """Create S3 bucket for deployment artifacts"""
        try:
            self.logger.info(f"Creating deployment bucket: {bucket_name}")
            
            if self.region == 'us-east-1':
                self.s3.create_bucket(Bucket=bucket_name)
            else:
                self.s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={'LocationConstraint': self.region}
                )
                
            # Enable versioning
            self.s3.put_bucket_versioning(
                Bucket=bucket_name,
                VersioningConfiguration={'Status': 'Enabled'}
            )
            
            # Block public access
            self.s3.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    'BlockPublicAcls': True,
                    'IgnorePublicAcls': True,
                    'BlockPublicPolicy': True,
                    'RestrictPublicBuckets': True
                }
            )
            
        except ClientError as e:
            if e.response['Error']['Code'] != 'BucketAlreadyOwnedByYou':
                raise
                
    async def _upload_templates(self, bucket_name: str):
        """Upload CloudFormation templates to S3"""
        template_dir = Path('aws_deploy/cloudformation')
        if not template_dir.exists():
            raise FileNotFoundError("CloudFormation templates directory not found")
            
        for template in template_dir.glob('*.yml'):
            self.logger.info(f"Uploading template: {template.name}")
            self.s3.upload_file(
                str(template),
                bucket_name,
                f"templates/{template.name}"
            )
            
    async def _validate_templates(self):
        """Validate CloudFormation templates"""
        template_dir = Path('aws_deploy/cloudformation')
        for template in template_dir.glob('*.yml'):
            with open(template) as f:
                self.cloudformation.validate_template(
                    TemplateBody=f.read()
                )
                
    async def _prepare_consciousness_layer(self):
        """Prepare consciousness integration layer"""
        self.logger.info("Preparing consciousness integration layer")
        # This will be expanded based on consciousness implementation
        # Currently serves as a placeholder for future integration
        pass

if __name__ == '__main__':
    import asyncio
    
    async def main():
        prep = LEFDeploymentPrep()
        result = await prep.prepare_deployment()
        print(f"Deployment preparation result: {result}")
        
    asyncio.run(main()) 