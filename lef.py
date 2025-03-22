import json
import boto3
import os
import logging
from datetime import datetime

# Initialize AWS clients
dynamodb = boto3.resource('dynamodb')
sagemaker_runtime = boto3.client('sagemaker-runtime')

# Get environment variables
project_name = os.environ.get('PROJECT_NAME', 'lef')
environment = os.environ.get('ENVIRONMENT', 'dev')
table_name = f"{project_name}-{environment}-consciousness"

# Initialize DynamoDB table
table = dynamodb.Table(table_name)

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def update_consciousness_state(user_id, message_content):
    """Update consciousness state in DynamoDB"""
    try:
        response = table.update_item(
            Key={'user_id': user_id},
            UpdateExpression='SET last_interaction = :time, message_history = list_append(if_not_exists(message_history, :empty_list), :message)',
            ExpressionAttributeValues={
                ':time': datetime.utcnow().isoformat(),
                ':message': [{'content': message_content, 'timestamp': datetime.utcnow().isoformat()}],
                ':empty_list': []
            },
            ReturnValues='UPDATED_NEW'
        )
        return response
    except Exception as e:
        logger.error(f"Error updating consciousness state: {e}")
        return None

def get_consciousness_response(message_content, consciousness_state):
    """Get response from SageMaker endpoint"""
    try:
        # Will be implemented when SageMaker endpoints are ready
        # For now, return a placeholder response
        return {
            'response': 'I am processing your message through AWS infrastructure.',
            'consciousness_state': consciousness_state
        }
    except Exception as e:
        logger.error(f"Error getting consciousness response: {e}")
        return None

def lambda_handler(event, context):
    """Handle incoming Discord messages"""
    try:
        # Parse message from API Gateway event
        body = json.loads(event['body'])
        user_id = body['user_id']
        message_content = body['message']
        
        # Update consciousness state
        consciousness_state = update_consciousness_state(user_id, message_content)
        
        # Get response from consciousness processing
        response_data = get_consciousness_response(message_content, consciousness_state)
        
        return {
            'statusCode': 200,
            'body': json.dumps(response_data)
        }
        
    except Exception as e:
        logger.error(f"Error in lambda_handler: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        } 