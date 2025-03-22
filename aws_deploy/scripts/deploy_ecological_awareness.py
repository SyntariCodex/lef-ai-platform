import boto3
import logging
import os
import json
from typing import Dict, Any
from botocore.exceptions import ClientError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EcologicalAwarenessDeployment:
    def __init__(self, environment: str = 'dev'):
        self.environment = environment
        self.project_name = 'lef'
        self.region = os.getenv('AWS_REGION', 'us-east-1')
        
        # Initialize AWS clients
        self.cloudformation = boto3.client('cloudformation')
        self.lambda_client = boto3.client('lambda')
        self.iam = boto3.client('iam')
        self.s3 = boto3.client('s3')
        self.cloudwatch = boto3.client('cloudwatch')
        self.xray = boto3.client('xray')
        self.sts = boto3.client('sts')
        
        # Set up paths
        self.template_path = os.path.join(os.path.dirname(__file__), '../cloudformation/ecological_awareness.yml')
        self.lambda_path = os.path.join(os.path.dirname(__file__), '../lambda/ecological_awareness.py')
        self.zip_path = os.path.join(os.path.dirname(__file__), '../lambda/ecological_awareness.zip')

    def get_account_id(self) -> str:
        """Get the AWS account ID."""
        try:
            return self.sts.get_caller_identity()["Account"]
        except Exception as e:
            logger.error(f"Error getting account ID: {str(e)}")
            raise

    def create_lambda_zip(self) -> None:
        """Create a ZIP file containing the Lambda function code."""
        try:
            import zipfile
            with zipfile.ZipFile(self.zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.write(self.lambda_path, 'ecological_awareness.py')
            logger.info(f"Created Lambda ZIP file at {self.zip_path}")
        except Exception as e:
            logger.error(f"Error creating Lambda ZIP file: {str(e)}")
            raise

    def create_lambda_role(self) -> str:
        """Create IAM role for the Lambda function."""
        try:
            role_name = f"{self.project_name}-{self.environment}-ecological-role"
            
            try:
                # Try to get existing role
                response = self.iam.get_role(RoleName=role_name)
                logger.info(f"Role {role_name} already exists")
                return response['Role']['Arn']
            except self.iam.exceptions.NoSuchEntityException:
                # Role doesn't exist, create it
                trust_policy = {
                    "Version": "2012-10-17",
                    "Statement": [
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "Service": "lambda.amazonaws.com"
                            },
                            "Action": "sts:AssumeRole"
                        }
                    ]
                }
                
                # Create role
                response = self.iam.create_role(
                    RoleName=role_name,
                    AssumeRolePolicyDocument=json.dumps(trust_policy)
                )
                
                # Attach required policies
                required_policies = [
                    'arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole',
                    'arn:aws:iam::aws:policy/AWSXRayDaemonWriteAccess',
                    'arn:aws:iam::aws:policy/CloudWatchLogsFullAccess',
                    'arn:aws:iam::aws:policy/CloudWatchFullAccess',
                    'arn:aws:iam::aws:policy/AmazonDynamoDBFullAccess',
                    'arn:aws:iam::aws:policy/AmazonSQSFullAccess',
                    'arn:aws:iam::aws:policy/AmazonS3FullAccess',
                    'arn:aws:iam::aws:policy/AmazonKinesisFullAccess'
                ]
                
                for policy_arn in required_policies:
                    self.iam.attach_role_policy(
                        RoleName=role_name,
                        PolicyArn=policy_arn
                    )
                
                logger.info(f"Created Lambda role: {role_name}")
                return response['Role']['Arn']
                
        except Exception as e:
            logger.error(f"Error creating Lambda role: {str(e)}")
            raise

    def setup_cloudwatch_namespace(self) -> None:
        """Set up CloudWatch namespace for cognitive development metrics."""
        try:
            namespace = 'LEF/CognitiveDevelopment'
            
            # Create custom namespace
            self.cloudwatch.put_metric_data(
                Namespace=namespace,
                MetricData=[{
                    'MetricName': 'Setup',
                    'Value': 1,
                    'Unit': 'None'
                }]
            )
            
            logger.info(f"Set up CloudWatch namespace: {namespace}")
        except Exception as e:
            logger.error(f"Error setting up CloudWatch namespace: {str(e)}")
            raise

    def setup_xray_sampling(self) -> None:
        """Set up X-Ray sampling rules for cognitive development tracking."""
        try:
            rule_name = f"{self.project_name}-{self.environment}-cognitive-sampling"
            
            # Create sampling rule
            self.xray.create_sampling_rule(
                SamplingRule={
                    'RuleName': rule_name,
                    'ResourceARN': '*',
                    'Priority': 1,
                    'FixedRate': 0.1,
                    'ReservoirSize': 1,
                    'Host': '*',
                    'HTTPMethod': '*',
                    'URLPath': '*',
                    'ServiceName': '*',
                    'ServiceType': '*',
                    'Version': 1,
                    'Attributes': {
                        'Layer': 'CognitiveDevelopment'
                    }
                }
            )
            
            logger.info(f"Set up X-Ray sampling rule: {rule_name}")
        except Exception as e:
            logger.error(f"Error setting up X-Ray sampling: {str(e)}")
            # Continue deployment even if X-Ray setup fails
            logger.warning("Continuing deployment despite X-Ray setup failure")

    def upload_lambda_code(self) -> str:
        """Upload Lambda function code to S3."""
        try:
            bucket_name = f"{self.project_name}-{self.environment}-deployment"
            
            # Create bucket if it doesn't exist
            try:
                if self.region == 'us-east-1':
                    self.s3.create_bucket(Bucket=bucket_name)
                else:
                    self.s3.create_bucket(
                        Bucket=bucket_name,
                        CreateBucketConfiguration={'LocationConstraint': self.region}
                    )
            except ClientError as e:
                if e.response['Error']['Code'] != 'BucketAlreadyExists':
                    raise
            
            # Upload Lambda ZIP file
            key = f"lambda/ecological_awareness_{self.environment}.zip"
            self.s3.upload_file(self.zip_path, bucket_name, key)
            
            logger.info(f"Uploaded Lambda code to s3://{bucket_name}/{key}")
            return f"s3://{bucket_name}/{key}"
            
        except Exception as e:
            logger.error(f"Error uploading Lambda code: {str(e)}")
            raise

    def deploy_cloudformation_stack(self, lambda_code_url: str, role_arn: str) -> None:
        """Deploy the CloudFormation stack."""
        try:
            stack_name = f"{self.project_name}-{self.environment}-ecological"
            
            # Read template file
            with open(self.template_path, 'r') as f:
                template_body = f.read()
            
            # Define stack parameters
            parameters = [
                {
                    'ParameterKey': 'Environment',
                    'ParameterValue': self.environment
                },
                {
                    'ParameterKey': 'ProjectName',
                    'ParameterValue': self.project_name
                }
            ]
            
            # Create or update stack
            try:
                self.cloudformation.create_stack(
                    StackName=stack_name,
                    TemplateBody=template_body,
                    Parameters=parameters,
                    Capabilities=['CAPABILITY_IAM']
                )
                logger.info(f"Created CloudFormation stack: {stack_name}")
            except ClientError as e:
                if e.response['Error']['Code'] == 'AlreadyExistsException':
                    self.cloudformation.update_stack(
                        StackName=stack_name,
                        TemplateBody=template_body,
                        Parameters=parameters,
                        Capabilities=['CAPABILITY_IAM']
                    )
                    logger.info(f"Updated CloudFormation stack: {stack_name}")
                else:
                    raise
            
            # Wait for stack creation/update
            waiter = self.cloudformation.get_waiter('stack_create_complete')
            waiter.wait(StackName=stack_name)
            
        except Exception as e:
            logger.error(f"Error deploying CloudFormation stack: {str(e)}")
            raise

    def deploy(self) -> None:
        """Deploy the ecological awareness infrastructure."""
        try:
            logger.info("Starting ecological awareness deployment...")
            
            # Create Lambda ZIP file
            self.create_lambda_zip()
            
            # Create Lambda role
            role_arn = self.create_lambda_role()
            
            # Set up CloudWatch namespace
            self.setup_cloudwatch_namespace()
            
            # Set up X-Ray sampling
            self.setup_xray_sampling()
            
            # Upload Lambda code
            lambda_code_url = self.upload_lambda_code()
            
            # Deploy CloudFormation stack
            self.deploy_cloudformation_stack(lambda_code_url, role_arn)
            
            logger.info("Ecological awareness deployment completed successfully")
            
        except Exception as e:
            logger.error(f"Deployment failed: {str(e)}")
            raise

def main():
    """Main function to run the deployment."""
    try:
        environment = os.getenv('ENVIRONMENT', 'dev')
        deployment = EcologicalAwarenessDeployment(environment)
        deployment.deploy()
    except Exception as e:
        logger.error(f"Deployment failed: {str(e)}")
        raise

if __name__ == '__main__':
    main() 