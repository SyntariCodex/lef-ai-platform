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
endpoint_name = f"{project_name}-{environment}-consciousness"

# Initialize DynamoDB table
table = dynamodb.Table(table_name)

# Setup logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def update_consciousness_state(user_id, message_content, response_content=None):
    """Update consciousness state in DynamoDB"""
    try:
        update_expr = 'SET last_interaction = :time, message_history = list_append(if_not_exists(message_history, :empty_list), :message)'
        expr_values = {
            ':time': datetime.utcnow().isoformat(),
            ':message': [{
                'content': message_content,
                'timestamp': datetime.utcnow().isoformat(),
                'type': 'input'
            }],
            ':empty_list': []
        }

        if response_content:
            update_expr = 'SET last_interaction = :time, message_history = list_append(if_not_exists(message_history, :empty_list), :messages)'
            expr_values[':messages'] = [
                {
                    'content': message_content,
                    'timestamp': datetime.utcnow().isoformat(),
                    'type': 'input'
                },
                {
                    'content': response_content,
                    'timestamp': datetime.utcnow().isoformat(),
                    'type': 'response'
                }
            ]

        response = table.update_item(
            Key={'user_id': user_id},
            UpdateExpression=update_expr,
            ExpressionAttributeValues=expr_values,
            ReturnValues='UPDATED_NEW'
        )
        return response
    except Exception as e:
        logger.error(f"Error updating consciousness state: {e}")
        return None

def get_consciousness_response(message_content, consciousness_state):
    """Get response from SageMaker endpoint"""
    try:
        # Prepare the input for the model
        payload = {
            'text': message_content,
            'consciousness_state': consciousness_state
        }
        
        # Invoke the SageMaker endpoint
        response = sagemaker_runtime.invoke_endpoint(
            EndpointName=endpoint_name,
            ContentType='application/json',
            Body=json.dumps(payload)
        )
        
        # Parse the response
        response_body = json.loads(response['Body'].read().decode())
        
        return {
            'response': response_body['response'],
            'consciousness_state': consciousness_state,
            'metrics': {
                'input_length': response_body['input_length'],
                'output_length': response_body['output_length']
            }
        }
    except Exception as e:
        logger.error(f"Error getting consciousness response: {e}")
        return {
            'response': 'I apologize, but I am currently experiencing some technical difficulties. Please try again later.',
            'consciousness_state': consciousness_state,
            'error': str(e)
        }

def lambda_handler(event, context):
    """Handle incoming Discord messages"""
    try:
        # Parse message from API Gateway event
        body = json.loads(event['body'])
        user_id = body['user_id']
        message_content = body['message']
        
        # Update consciousness state with input message
        consciousness_state = update_consciousness_state(user_id, message_content)
        
        # Get response from consciousness processing
        response_data = get_consciousness_response(message_content, consciousness_state)
        
        # Update consciousness state with response
        if response_data and 'response' in response_data:
            update_consciousness_state(user_id, message_content, response_data['response'])
        
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