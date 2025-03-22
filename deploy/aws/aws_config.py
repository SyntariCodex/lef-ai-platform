from typing import Dict
import os
from dataclasses import dataclass

@dataclass
class AWSConfig:
    """AWS configuration settings for LEF deployment"""
    region: str = "us-west-2"  # Default to US West (Oregon)
    
    # EC2 Configuration
    ec2_config: Dict = None
    
    # RDS Configuration
    rds_config: Dict = None
    
    # S3 Configuration
    s3_config: Dict = None
    
    def __post_init__(self):
        self.ec2_config = {
            "instance_type": "t2.micro",  # Free tier eligible
            "ami_id": "ami-0735c191cf914754d",  # Amazon Linux 2
            "key_name": "lef-key-pair",
            "security_group": "lef-security-group",
            "tags": {
                "Name": "LEF-Server",
                "Environment": "Development"
            }
        }
        
        self.rds_config = {
            "instance_class": "db.t3.micro",  # Free tier eligible
            "engine": "postgres",
            "engine_version": "13.7",
            "database_name": "lef_db",
            "master_username": "lef_admin",
            "storage_type": "gp2",
            "allocated_storage": 20
        }
        
        self.s3_config = {
            "bucket_name": "lef-storage",
            "versioning": True,
            "public_access": False,
            "encryption": True
        }
    
    def get_ec2_config(self) -> Dict:
        """Get EC2 configuration with environment-specific settings"""
        return {
            **self.ec2_config,
            "security_group_rules": [
                {
                    "IpProtocol": "tcp",
                    "FromPort": 80,
                    "ToPort": 80,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
                },
                {
                    "IpProtocol": "tcp",
                    "FromPort": 443,
                    "ToPort": 443,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}]
                },
                {
                    "IpProtocol": "tcp",
                    "FromPort": 22,
                    "ToPort": 22,
                    "IpRanges": [{"CidrIp": "0.0.0.0/0"}]  # TODO: Restrict to specific IP
                }
            ]
        }
    
    def get_rds_config(self) -> Dict:
        """Get RDS configuration with environment-specific settings"""
        return {
            **self.rds_config,
            "subnet_group": "lef-db-subnet",
            "security_group": "lef-db-security-group",
            "backup_retention_period": 7,
            "multi_az": False,  # Set to True for production
            "publicly_accessible": False
        }
    
    def get_s3_config(self) -> Dict:
        """Get S3 configuration with environment-specific settings"""
        return {
            **self.s3_config,
            "cors_rules": [
                {
                    "AllowedHeaders": ["*"],
                    "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
                    "AllowedOrigins": ["*"],  # TODO: Restrict to specific origins
                    "ExposeHeaders": ["ETag"],
                    "MaxAgeSeconds": 3000
                }
            ]
        }

    def get_cloudwatch_config(self) -> Dict:
        """Get CloudWatch configuration"""
        return {
            "log_group": "/aws/lef",
            "retention_days": 30,
            "metric_namespace": "LEF/Metrics",
            "alarms": {
                "cpu_utilization": {
                    "threshold": 80,
                    "period": 300,
                    "evaluation_periods": 2
                },
                "memory_utilization": {
                    "threshold": 80,
                    "period": 300,
                    "evaluation_periods": 2
                }
            }
        }

# Environment-specific configurations
DEV_CONFIG = AWSConfig()
# TODO: Add staging and production configs 