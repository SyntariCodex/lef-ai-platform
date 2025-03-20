import json
import boto3
from datetime import datetime
from typing import Dict, Any

dynamodb = boto3.resource('dynamodb')
project_table = dynamodb.Table('projects')
resource_table = dynamodb.Table('resources')

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle project-related operations."""
    try:
        operation = event.get('operation')
        project_data = event.get('project_data', {})
        
        if operation == 'create':
            return create_project(project_data)
        elif operation == 'update':
            return update_project(project_data)
        elif operation == 'complete':
            return complete_project(project_data)
        elif operation == 'analyze':
            return analyze_project(project_data)
        else:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Invalid operation: {operation}'})
            }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

def create_project(data: Dict) -> Dict:
    """Create a new project."""
    project_id = data.get('project_id')
    if not project_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Project ID required'})
        }
        
    project_item = {
        'project_id': project_id,
        'status': 'initializing',
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'resources': data.get('resources', {}),
        'timeline': data.get('timeline', {}),
        'metrics': {
            'progress': 0,
            'efficiency': 0,
            'quality': 0
        }
    }
    
    project_table.put_item(Item=project_item)
    
    # Allocate initial resources
    if 'resources' in data:
        for resource_id, allocation in data['resources'].items():
            resource_table.update_item(
                Key={'resource_id': resource_id},
                UpdateExpression='SET allocation = :a',
                ExpressionAttributeValues={':a': allocation}
            )
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Project created successfully',
            'project_id': project_id
        })
    }

def update_project(data: Dict) -> Dict:
    """Update project status and metrics."""
    project_id = data.get('project_id')
    if not project_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Project ID required'})
        }
        
    update_expr = ['SET updated_at = :time']
    expr_values = {':time': datetime.now().isoformat()}
    
    # Update status if provided
    if 'status' in data:
        update_expr.append('status = :s')
        expr_values[':s'] = data['status']
    
    # Update resources if provided
    if 'resources' in data:
        update_expr.append('resources = :r')
        expr_values[':r'] = data['resources']
        
        # Update resource allocations
        for resource_id, allocation in data['resources'].items():
            resource_table.update_item(
                Key={'resource_id': resource_id},
                UpdateExpression='SET allocation = :a',
                ExpressionAttributeValues={':a': allocation}
            )
    
    # Update timeline if provided
    if 'timeline' in data:
        update_expr.append('timeline = :t')
        expr_values[':t'] = data['timeline']
    
    # Update metrics if provided
    if 'metrics' in data:
        update_expr.append('metrics = :m')
        expr_values[':m'] = data['metrics']
    
    project_table.update_item(
        Key={'project_id': project_id},
        UpdateExpression='SET ' + ', '.join(update_expr),
        ExpressionAttributeValues=expr_values
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Project updated successfully',
            'project_id': project_id
        })
    }

def complete_project(data: Dict) -> Dict:
    """Mark project as complete and release resources."""
    project_id = data.get('project_id')
    if not project_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Project ID required'})
        }
    
    # Get current project data
    project = project_table.get_item(Key={'project_id': project_id})
    if 'Item' not in project:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Project not found'})
        }
    
    # Release resources
    for resource_id in project['Item'].get('resources', {}):
        resource_table.update_item(
            Key={'resource_id': resource_id},
            UpdateExpression='SET allocation = :a',
            ExpressionAttributeValues={':a': 0}
        )
    
    # Update project status
    project_table.update_item(
        Key={'project_id': project_id},
        UpdateExpression='SET status = :s, completed_at = :t, updated_at = :u',
        ExpressionAttributeValues={
            ':s': 'completed',
            ':t': datetime.now().isoformat(),
            ':u': datetime.now().isoformat()
        }
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Project completed successfully',
            'project_id': project_id
        })
    }

def analyze_project(data: Dict) -> Dict:
    """Analyze project performance and metrics."""
    project_id = data.get('project_id')
    if not project_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Project ID required'})
        }
    
    # Get project data
    project = project_table.get_item(Key={'project_id': project_id})
    if 'Item' not in project:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Project not found'})
        }
    
    project_data = project['Item']
    
    # Calculate metrics
    timeline = project_data.get('timeline', {})
    resources = project_data.get('resources', {})
    metrics = project_data.get('metrics', {})
    
    analysis = {
        'project_id': project_id,
        'status': project_data.get('status'),
        'duration': _calculate_duration(timeline),
        'resource_efficiency': _calculate_resource_efficiency(resources),
        'progress_rate': _calculate_progress_rate(metrics),
        'quality_score': metrics.get('quality', 0),
        'recommendations': _generate_recommendations(project_data)
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(analysis)
    }

def _calculate_duration(timeline: Dict) -> float:
    """Calculate project duration in days."""
    if not timeline.get('start') or not timeline.get('end'):
        return 0
        
    start = datetime.fromisoformat(timeline['start'])
    end = datetime.fromisoformat(timeline['end'])
    return (end - start).days

def _calculate_resource_efficiency(resources: Dict) -> float:
    """Calculate resource utilization efficiency."""
    if not resources:
        return 0
        
    total_allocation = sum(r.get('allocation', 0) for r in resources.values())
    return min(1.0, total_allocation / len(resources))

def _calculate_progress_rate(metrics: Dict) -> float:
    """Calculate project progress rate."""
    return metrics.get('progress', 0) / 100.0

def _generate_recommendations(project_data: Dict) -> List[str]:
    """Generate project improvement recommendations."""
    recommendations = []
    
    # Resource utilization recommendations
    resource_efficiency = _calculate_resource_efficiency(project_data.get('resources', {}))
    if resource_efficiency < 0.7:
        recommendations.append("Consider optimizing resource allocation")
    
    # Progress recommendations
    progress = project_data.get('metrics', {}).get('progress', 0)
    if progress < 50:
        recommendations.append("Review project timeline and milestones")
    
    # Quality recommendations
    quality = project_data.get('metrics', {}).get('quality', 0)
    if quality < 80:
        recommendations.append("Implement additional quality control measures")
    
    return recommendations 