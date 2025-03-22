import boto3
import os
import sys
import yaml
import logging
from botocore.exceptions import ClientError

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_config():
    """Load AWS configuration"""
    config_path = os.path.join(os.path.dirname(__file__), '..', 'config', 'aws_config.yaml')
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def create_model_artifacts():
    """Create and upload model artifacts to S3"""
    try:
        s3 = boto3.client('s3')
        config = load_config()
        
        # Create model directory
        os.makedirs('model', exist_ok=True)
        
        # Copy inference script
        inference_script = os.path.join(os.path.dirname(__file__), '..', 'lambda', 'inference.py')
        os.makedirs(os.path.join('model', 'code'), exist_ok=True)
        with open(inference_script, 'r') as src, open(os.path.join('model', 'code', 'inference.py'), 'w') as dst:
            dst.write(src.read())
        
        # Create requirements.txt
        with open(os.path.join('model', 'code', 'requirements.txt'), 'w') as f:
            f.write('torch>=2.1.1\ntransformers>=4.37.2\n')
        
        # Create tar.gz of the model directory
        import tarfile
        with tarfile.open('model.tar.gz', 'w:gz') as tar:
            tar.add('model', arcname='.')
        
        # Upload to S3
        bucket_name = f"{config['project_name']}-{config['environment']}-learning-environment"
        s3.upload_file(
            'model.tar.gz',
            bucket_name,
            'models/consciousness/model.tar.gz'
        )
        
        # Cleanup
        import shutil
        shutil.rmtree('model')
        os.remove('model.tar.gz')
        
        logger.info(f"Model artifacts uploaded to s3://{bucket_name}/models/consciousness/model.tar.gz")
        
    except Exception as e:
        logger.error(f"Error creating model artifacts: {e}")
        sys.exit(1)

def deploy_sagemaker_stack():
    """Deploy SageMaker CloudFormation stack"""
    try:
        cf = boto3.client('cloudformation')
        config = load_config()
        
        # Read template
        template_path = os.path.join(os.path.dirname(__file__), '..', 'cloudformation', 'sagemaker_resources.yml')
        with open(template_path, 'r') as f:
            template_body = f.read()
        
        # Create/update stack
        stack_name = f"{config['project_name']}-{config['environment']}-sagemaker"
        try:
            cf.describe_stacks(StackName=stack_name)
            logger.info(f"Updating stack {stack_name}")
            cf.update_stack(
                StackName=stack_name,
                TemplateBody=template_body,
                Parameters=[
                    {'ParameterKey': 'Environment', 'ParameterValue': config['environment']},
                    {'ParameterKey': 'ProjectName', 'ParameterValue': config['project_name']}
                ],
                Capabilities=['CAPABILITY_NAMED_IAM']
            )
        except ClientError as e:
            if 'does not exist' in str(e):
                logger.info(f"Creating stack {stack_name}")
                cf.create_stack(
                    StackName=stack_name,
                    TemplateBody=template_body,
                    Parameters=[
                        {'ParameterKey': 'Environment', 'ParameterValue': config['environment']},
                        {'ParameterKey': 'ProjectName', 'ParameterValue': config['project_name']}
                    ],
                    Capabilities=['CAPABILITY_NAMED_IAM']
                )
            else:
                raise
        
        # Wait for stack to complete
        waiter = cf.get_waiter('stack_update_complete')
        logger.info("Waiting for stack update to complete...")
        waiter.wait(StackName=stack_name)
        
        logger.info("SageMaker resources deployed successfully")
        
    except Exception as e:
        logger.error(f"Error deploying SageMaker stack: {e}")
        sys.exit(1)

def main():
    """Main deployment function"""
    logger.info("Starting SageMaker deployment")
    create_model_artifacts()
    deploy_sagemaker_stack()
    logger.info("SageMaker deployment completed")

if __name__ == '__main__':
    main() 