from typing import Dict, List, Optional
import time
import boto3
from botocore.exceptions import ClientError
from lef.core.business import BusinessCore

class AWSHandler:
    def __init__(self, business_core: BusinessCore):
        self.business_core = business_core
        self.last_update = time.time()
        self.update_interval = 300  # Update every 5 minutes
        
        # Initialize AWS clients
        self.ec2 = boto3.client('ec2')
        self.s3 = boto3.client('s3')
        self.rds = boto3.client('rds')
        self.cloudwatch = boto3.client('cloudwatch')
        
        # Track AWS resources
        self.aws_resources = {
            'ec2_instances': {},
            'rds_instances': {},
            's3_buckets': {},
            'metrics': {}
        }
        
    def update(self):
        current_time = time.time()
        if current_time - self.last_update >= self.update_interval:
            self._update_resource_status()
            self._monitor_performance()
            self._optimize_costs()
            self._manage_scaling()
            self.last_update = current_time
            
    def _update_resource_status(self):
        """Update status of all AWS resources."""
        try:
            # Update EC2 instances
            response = self.ec2.describe_instances()
            for reservation in response['Reservations']:
                for instance in reservation['Instances']:
                    self.aws_resources['ec2_instances'][instance['InstanceId']] = {
                        'state': instance['State']['Name'],
                        'type': instance['InstanceType'],
                        'launch_time': instance['LaunchTime']
                    }
                    
            # Update RDS instances
            response = self.rds.describe_db_instances()
            for instance in response['DBInstances']:
                self.aws_resources['rds_instances'][instance['DBInstanceIdentifier']] = {
                    'status': instance['DBInstanceStatus'],
                    'class': instance['DBInstanceClass'],
                    'engine': instance['Engine']
                }
                
            # Update S3 buckets
            response = self.s3.list_buckets()
            for bucket in response['Buckets']:
                self.aws_resources['s3_buckets'][bucket['Name']] = {
                    'creation_date': bucket['CreationDate']
                }
                
        except ClientError as e:
            print(f"Error updating AWS resource status: {str(e)}")
            
    def _monitor_performance(self):
        """Monitor performance metrics for AWS resources."""
        try:
            for instance_id in self.aws_resources['ec2_instances']:
                # Get CPU utilization
                response = self.cloudwatch.get_metric_statistics(
                    Namespace='AWS/EC2',
                    MetricName='CPUUtilization',
                    Dimensions=[{'Name': 'InstanceId', 'Value': instance_id}],
                    StartTime=time.time() - 3600,
                    EndTime=time.time(),
                    Period=300,
                    Statistics=['Average']
                )
                
                if response['Datapoints']:
                    self.aws_resources['metrics'][instance_id] = {
                        'cpu_utilization': response['Datapoints'][-1]['Average']
                    }
                    
            for db_instance in self.aws_resources['rds_instances']:
                # Get database connections
                response = self.cloudwatch.get_metric_statistics(
                    Namespace='AWS/RDS',
                    MetricName='DatabaseConnections',
                    Dimensions=[{'Name': 'DBInstanceIdentifier', 'Value': db_instance}],
                    StartTime=time.time() - 3600,
                    EndTime=time.time(),
                    Period=300,
                    Statistics=['Average']
                )
                
                if response['Datapoints']:
                    self.aws_resources['metrics'][db_instance] = {
                        'db_connections': response['Datapoints'][-1]['Average']
                    }
                    
        except ClientError as e:
            print(f"Error monitoring AWS performance: {str(e)}")
            
    def _optimize_costs(self):
        """Optimize AWS resource costs."""
        try:
            # Check EC2 instance utilization
            for instance_id, metrics in self.aws_resources['metrics'].items():
                if instance_id in self.aws_resources['ec2_instances']:
                    if metrics.get('cpu_utilization', 0) < 20:  # Less than 20% CPU utilization
                        self._recommend_instance_downgrade(instance_id)
                        
            # Check RDS instance utilization
            for db_instance, metrics in self.aws_resources['metrics'].items():
                if db_instance in self.aws_resources['rds_instances']:
                    if metrics.get('db_connections', 0) < 10:  # Less than 10 connections
                        self._recommend_rds_downgrade(db_instance)
                        
        except ClientError as e:
            print(f"Error optimizing AWS costs: {str(e)}")
            
    def _manage_scaling(self):
        """Manage auto-scaling of AWS resources."""
        try:
            # Scale EC2 instances
            for instance_id, metrics in self.aws_resources['metrics'].items():
                if instance_id in self.aws_resources['ec2_instances']:
                    if metrics.get('cpu_utilization', 0) > 80:  # Over 80% CPU utilization
                        self._scale_up_ec2(instance_id)
                        
            # Scale RDS instances
            for db_instance, metrics in self.aws_resources['metrics'].items():
                if db_instance in self.aws_resources['rds_instances']:
                    if metrics.get('db_connections', 0) > 100:  # Over 100 connections
                        self._scale_up_rds(db_instance)
                        
        except ClientError as e:
            print(f"Error managing AWS scaling: {str(e)}")
            
    def _recommend_instance_downgrade(self, instance_id: str):
        """Recommend EC2 instance type downgrade."""
        instance_type = self.aws_resources['ec2_instances'][instance_id]['type']
        
        # Add recommendation to business core
        self.business_core.update_resource(f"ec2_{instance_id}", {
            'status': 'optimization_recommended',
            'recommendation': f"Consider downgrading {instance_id} from {instance_type}"
        })
        
    def _recommend_rds_downgrade(self, db_instance: str):
        """Recommend RDS instance class downgrade."""
        instance_class = self.aws_resources['rds_instances'][db_instance]['class']
        
        # Add recommendation to business core
        self.business_core.update_resource(f"rds_{db_instance}", {
            'status': 'optimization_recommended',
            'recommendation': f"Consider downgrading {db_instance} from {instance_class}"
        })
        
    def _scale_up_ec2(self, instance_id: str):
        """Scale up EC2 instance."""
        try:
            instance_type = self.aws_resources['ec2_instances'][instance_id]['type']
            
            # Stop the instance
            self.ec2.stop_instances(InstanceIds=[instance_id])
            
            # Wait for the instance to stop
            waiter = self.ec2.get_waiter('instance_stopped')
            waiter.wait(InstanceIds=[instance_id])
            
            # Modify instance type
            new_type = self._get_next_instance_type(instance_type)
            self.ec2.modify_instance_attribute(
                InstanceId=instance_id,
                InstanceType={'Value': new_type}
            )
            
            # Start the instance
            self.ec2.start_instances(InstanceIds=[instance_id])
            
        except ClientError as e:
            print(f"Error scaling up EC2 instance: {str(e)}")
            
    def _scale_up_rds(self, db_instance: str):
        """Scale up RDS instance."""
        try:
            instance_class = self.aws_resources['rds_instances'][db_instance]['class']
            
            # Modify instance class
            new_class = self._get_next_db_class(instance_class)
            self.rds.modify_db_instance(
                DBInstanceIdentifier=db_instance,
                DBInstanceClass=new_class,
                ApplyImmediately=True
            )
            
        except ClientError as e:
            print(f"Error scaling up RDS instance: {str(e)}")
            
    def _get_next_instance_type(self, current_type: str) -> str:
        """Get next larger EC2 instance type."""
        # Simple mapping of instance types to their next size up
        instance_upgrades = {
            't2.micro': 't2.small',
            't2.small': 't2.medium',
            't2.medium': 't2.large',
            't2.large': 't2.xlarge',
            't2.xlarge': 't2.2xlarge'
        }
        return instance_upgrades.get(current_type, current_type)
        
    def _get_next_db_class(self, current_class: str) -> str:
        """Get next larger RDS instance class."""
        # Simple mapping of DB instance classes to their next size up
        db_upgrades = {
            'db.t2.micro': 'db.t2.small',
            'db.t2.small': 'db.t2.medium',
            'db.t2.medium': 'db.t2.large',
            'db.t2.large': 'db.t2.xlarge',
            'db.t2.xlarge': 'db.t2.2xlarge'
        }
        return db_upgrades.get(current_class, current_class) 