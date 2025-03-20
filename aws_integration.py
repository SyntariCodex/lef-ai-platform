import boto3
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class AWSManager:
    """AWS infrastructure management for LEF business operations."""
    def __init__(self):
        self.ec2 = boto3.client('ec2')
        self.dynamodb = boto3.client('dynamodb')
        self.sqs = boto3.client('sqs')
        self.lambda_client = boto3.client('lambda')
        self.ecs = boto3.client('ecs')
        
        # Infrastructure Configuration
        self.config = {
            'initial_instances': 2,
            'max_instances': 10,
            'instance_type': 't3.2xlarge',
            'auto_scaling': True,
            'cost_threshold': 1000.0  # Monthly budget in USD
        }
        
        # Resource Tracking
        self.resources = {
            'instances': [],
            'databases': [],
            'queues': [],
            'functions': [],
            'containers': []
        }
        
    def initialize_infrastructure(self):
        """Set up initial AWS infrastructure."""
        try:
            # Create DynamoDB tables
            self._create_business_tables()
            
            # Set up SQS queues
            self._create_message_queues()
            
            # Initialize EC2 instances
            self._launch_initial_instances()
            
            # Deploy Lambda functions
            self._deploy_business_functions()
            
            # Configure ECS clusters
            self._setup_container_clusters()
            
            return True
        except Exception as e:
            print(f"Infrastructure initialization failed: {str(e)}")
            return False
            
    def _create_business_tables(self):
        """Create DynamoDB tables for business data."""
        tables = {
            'projects': {
                'key': 'project_id',
                'attributes': ['status', 'resources', 'timeline']
            },
            'finances': {
                'key': 'transaction_id',
                'attributes': ['type', 'amount', 'category']
            },
            'stakeholders': {
                'key': 'stakeholder_id',
                'attributes': ['type', 'status', 'relationships']
            },
            'resources': {
                'key': 'resource_id',
                'attributes': ['type', 'status', 'allocation']
            }
        }
        
        for table_name, schema in tables.items():
            self.dynamodb.create_table(
                TableName=table_name,
                KeySchema=[{'AttributeName': schema['key'], 'KeyType': 'HASH'}],
                AttributeDefinitions=[{'AttributeName': schema['key'], 'AttributeType': 'S'}],
                ProvisionedThroughput={'ReadCapacityUnits': 5, 'WriteCapacityUnits': 5}
            )
            
    def _create_message_queues(self):
        """Set up SQS queues for business operations."""
        queues = [
            'project-updates',
            'financial-transactions',
            'stakeholder-events',
            'resource-requests',
            'system-alerts'
        ]
        
        for queue in queues:
            response = self.sqs.create_queue(
                QueueName=queue,
                Attributes={
                    'VisibilityTimeout': '300',
                    'MessageRetentionPeriod': '86400'
                }
            )
            self.resources['queues'].append(response['QueueUrl'])
            
    def _launch_initial_instances(self):
        """Launch initial EC2 instances."""
        response = self.ec2.run_instances(
            ImageId='ami-0c55b159cbfafe1f0',  # Update with appropriate AMI
            InstanceType=self.config['instance_type'],
            MinCount=self.config['initial_instances'],
            MaxCount=self.config['initial_instances'],
            TagSpecifications=[{
                'ResourceType': 'instance',
                'Tags': [{'Key': 'Purpose', 'Value': 'LEF-Business-Operations'}]
            }]
        )
        
        for instance in response['Instances']:
            self.resources['instances'].append(instance['InstanceId'])
            
    def _deploy_business_functions(self):
        """Deploy Lambda functions for business operations."""
        functions = {
            'process-project': 'handlers/project_handler.py',
            'process-financial': 'handlers/financial_handler.py',
            'process-stakeholder': 'handlers/stakeholder_handler.py',
            'process-resource': 'handlers/resource_handler.py'
        }
        
        for func_name, handler_path in functions.items():
            with open(handler_path, 'rb') as f:
                self.lambda_client.create_function(
                    FunctionName=func_name,
                    Runtime='python3.9',
                    Role='arn:aws:iam::ACCOUNT_ID:role/LEF-Lambda-Role',  # Update with actual role
                    Handler=f"{handler_path.split('/')[-1].split('.')[0]}.handler",
                    Code={'ZipFile': f.read()},
                    Timeout=300,
                    MemorySize=1024
                )
                
    def _setup_container_clusters(self):
        """Set up ECS clusters for scalable operations."""
        response = self.ecs.create_cluster(
            clusterName='lef-business-cluster',
            capacityProviders=['FARGATE'],
            defaultCapacityProviderStrategy=[{
                'capacityProvider': 'FARGATE',
                'weight': 1
            }]
        )
        
        self.resources['containers'].append(response['cluster']['clusterName'])
        
    def scale_resources(self, metrics: Dict):
        """Scale AWS resources based on business metrics."""
        try:
            # Scale EC2 instances
            if metrics['cpu_utilization'] > 70:
                self._scale_instances(1)
            elif metrics['cpu_utilization'] < 30:
                self._scale_instances(-1)
                
            # Scale database capacity
            if metrics['db_usage'] > 80:
                self._scale_database_capacity(True)
            elif metrics['db_usage'] < 20:
                self._scale_database_capacity(False)
                
            # Adjust Lambda concurrency
            self._adjust_lambda_concurrency(metrics['request_rate'])
            
            return True
        except Exception as e:
            print(f"Resource scaling failed: {str(e)}")
            return False
            
    def _scale_instances(self, change: int):
        """Scale EC2 instances up or down."""
        current_count = len(self.resources['instances'])
        new_count = max(1, min(self.config['max_instances'], current_count + change))
        
        if change > 0:
            self._launch_initial_instances()
        else:
            instance_id = self.resources['instances'].pop()
            self.ec2.terminate_instances(InstanceIds=[instance_id])
            
    def _scale_database_capacity(self, increase: bool):
        """Adjust DynamoDB capacity."""
        for table in self.resources['databases']:
            current_capacity = self.dynamodb.describe_table(TableName=table)['Table']['ProvisionedThroughput']
            new_read = current_capacity['ReadCapacityUnits'] * (1.5 if increase else 0.67)
            new_write = current_capacity['WriteCapacityUnits'] * (1.5 if increase else 0.67)
            
            self.dynamodb.update_table(
                TableName=table,
                ProvisionedThroughput={
                    'ReadCapacityUnits': int(new_read),
                    'WriteCapacityUnits': int(new_write)
                }
            )
            
    def _adjust_lambda_concurrency(self, request_rate: int):
        """Adjust Lambda function concurrency limits."""
        for function in self.resources['functions']:
            new_concurrency = min(1000, max(5, int(request_rate / 10)))
            self.lambda_client.put_function_concurrency(
                FunctionName=function,
                ReservedConcurrentExecutions=new_concurrency
            )
            
    def monitor_costs(self) -> Dict:
        """Monitor and optimize AWS costs."""
        try:
            client = boto3.client('ce')
            
            response = client.get_cost_and_usage(
                TimePeriod={
                    'Start': (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d'),
                    'End': datetime.now().strftime('%Y-%m-%d')
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost']
            )
            
            current_cost = float(response['ResultsByTime'][0]['Total']['UnblendedCost']['Amount'])
            
            if current_cost > self.config['cost_threshold']:
                self._optimize_costs()
                
            return {
                'current_cost': current_cost,
                'threshold': self.config['cost_threshold'],
                'status': 'optimizing' if current_cost > self.config['cost_threshold'] else 'normal'
            }
        except Exception as e:
            print(f"Cost monitoring failed: {str(e)}")
            return None
            
    def _optimize_costs(self):
        """Implement cost optimization strategies."""
        # Scale down underutilized resources
        for instance in self.resources['instances']:
            metrics = self.ec2.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=[{'Name': 'InstanceId', 'Value': instance}],
                StartTime=datetime.now() - timedelta(hours=24),
                EndTime=datetime.now(),
                Period=3600,
                Statistics=['Average']
            )
            
            if metrics['Datapoints'][0]['Average'] < 20:
                self._scale_instances(-1)
                
        # Optimize database capacity
        for table in self.resources['databases']:
            consumed = self.dynamodb.describe_table(TableName=table)['Table']['ProvisionedThroughput']
            if consumed['ReadCapacityUnits'] > 100 and consumed['ConsumedReadCapacityUnits'] < 50:
                self._scale_database_capacity(False)
                
    def get_system_metrics(self) -> Dict:
        """Get current system metrics."""
        try:
            metrics = {
                'instances': len(self.resources['instances']),
                'databases': len(self.resources['databases']),
                'queues': len(self.resources['queues']),
                'functions': len(self.resources['functions']),
                'containers': len(self.resources['containers']),
                'costs': self.monitor_costs()
            }
            
            return metrics
        except Exception as e:
            print(f"Failed to get system metrics: {str(e)}")
            return None 