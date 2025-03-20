import json
import boto3
from datetime import datetime
from typing import Dict, Any, List
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
resource_table = dynamodb.Table('resources')
project_table = dynamodb.Table('projects')

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle resource operations."""
    try:
        operation = event.get('operation')
        resource_data = event.get('resource_data', {})
        
        if operation == 'add_resource':
            return add_resource(resource_data)
        elif operation == 'update_resource':
            return update_resource(resource_data)
        elif operation == 'allocate_resource':
            return allocate_resource(resource_data)
        elif operation == 'analyze_utilization':
            return analyze_resource_utilization(resource_data)
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

def add_resource(data: Dict) -> Dict:
    """Add a new resource."""
    required_fields = ['resource_id', 'type', 'capacity']
    for field in required_fields:
        if field not in data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Missing required field: {field}'})
            }
    
    resource_item = {
        'resource_id': data['resource_id'],
        'type': data['type'],
        'capacity': Decimal(str(data['capacity'])),
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'status': 'available',
        'allocation': Decimal('0'),
        'projects': [],
        'metrics': {
            'utilization_rate': Decimal('0'),
            'efficiency_score': Decimal('0'),
            'availability': Decimal('100')
        },
        'maintenance_schedule': data.get('maintenance_schedule', {}),
        'specifications': data.get('specifications', {}),
        'cost_center': data.get('cost_center'),
        'history': []
    }
    
    resource_table.put_item(Item=resource_item)
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Resource added successfully',
            'resource_id': data['resource_id']
        })
    }

def update_resource(data: Dict) -> Dict:
    """Update resource information."""
    resource_id = data.get('resource_id')
    if not resource_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Resource ID required'})
        }
    
    # Get current resource data
    resource = resource_table.get_item(Key={'resource_id': resource_id})
    if 'Item' not in resource:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Resource not found'})
        }
    
    current_data = resource['Item']
    
    # Build update expression
    update_expr = ['SET updated_at = :time']
    expr_values = {':time': datetime.now().isoformat()}
    
    # Update basic information
    for field in ['type', 'capacity', 'status', 'specifications', 'maintenance_schedule']:
        if field in data:
            update_expr.append(f'{field} = :{field[0]}')
            expr_values[f':{field[0]}'] = data[field]
    
    # Update metrics if provided
    if 'metrics' in data:
        update_expr.append('metrics = :m')
        expr_values[':m'] = data['metrics']
    
    # Add to history
    history_entry = {
        'timestamp': datetime.now().isoformat(),
        'changes': {k: v for k, v in data.items() if k != 'resource_id'}
    }
    update_expr.append('history = list_append(if_not_exists(history, :empty), :h)')
    expr_values[':empty'] = []
    expr_values[':h'] = [history_entry]
    
    resource_table.update_item(
        Key={'resource_id': resource_id},
        UpdateExpression='SET ' + ', '.join(update_expr),
        ExpressionAttributeValues=expr_values
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Resource updated successfully',
            'resource_id': resource_id
        })
    }

def allocate_resource(data: Dict) -> Dict:
    """Allocate resource to a project."""
    resource_id = data.get('resource_id')
    project_id = data.get('project_id')
    allocation_amount = data.get('allocation')
    
    if not all([resource_id, project_id, allocation_amount]):
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Missing required fields'})
        }
    
    # Get resource data
    resource = resource_table.get_item(Key={'resource_id': resource_id})
    if 'Item' not in resource:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Resource not found'})
        }
    
    resource_data = resource['Item']
    
    # Check capacity
    current_allocation = Decimal(str(resource_data.get('allocation', 0)))
    new_allocation = current_allocation + Decimal(str(allocation_amount))
    if new_allocation > resource_data['capacity']:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Insufficient capacity'})
        }
    
    # Update resource allocation
    resource_table.update_item(
        Key={'resource_id': resource_id},
        UpdateExpression='SET allocation = :a, updated_at = :t, projects = list_append(if_not_exists(projects, :empty), :p)',
        ExpressionAttributeValues={
            ':a': new_allocation,
            ':t': datetime.now().isoformat(),
            ':empty': [],
            ':p': [project_id]
        }
    )
    
    # Update project resource allocation
    try:
        project_table.update_item(
            Key={'project_id': project_id},
            UpdateExpression='SET resources.#rid = :a',
            ExpressionAttributeNames={'#rid': resource_id},
            ExpressionAttributeValues={':a': allocation_amount}
        )
    except Exception as e:
        # Rollback resource allocation if project update fails
        resource_table.update_item(
            Key={'resource_id': resource_id},
            UpdateExpression='SET allocation = :a',
            ExpressionAttributeValues={':a': current_allocation}
        )
        return {
            'statusCode': 500,
            'body': json.dumps({'error': f'Failed to update project: {str(e)}'})
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Resource allocated successfully',
            'resource_id': resource_id,
            'project_id': project_id,
            'allocation': float(new_allocation)
        })
    }

def analyze_resource_utilization(data: Dict) -> Dict:
    """Analyze resource utilization and generate insights."""
    resource_id = data.get('resource_id')
    if not resource_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Resource ID required'})
        }
    
    # Get resource data
    resource = resource_table.get_item(Key={'resource_id': resource_id})
    if 'Item' not in resource:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Resource not found'})
        }
    
    resource_data = resource['Item']
    
    # Calculate utilization metrics
    utilization_metrics = calculate_utilization_metrics(resource_data)
    
    # Generate efficiency insights
    efficiency_insights = generate_efficiency_insights(resource_data)
    
    # Analyze allocation patterns
    allocation_analysis = analyze_allocation_patterns(resource_data)
    
    # Generate optimization recommendations
    recommendations = generate_optimization_recommendations(resource_data)
    
    analysis = {
        'resource_id': resource_id,
        'utilization': {
            'current_rate': float(utilization_metrics['current_rate']),
            'average_rate': float(utilization_metrics['average_rate']),
            'peak_rate': float(utilization_metrics['peak_rate'])
        },
        'efficiency': {
            'score': float(resource_data['metrics']['efficiency_score']),
            'insights': efficiency_insights
        },
        'allocation': {
            'pattern': allocation_analysis['pattern'],
            'stability': allocation_analysis['stability'],
            'bottlenecks': allocation_analysis['bottlenecks']
        },
        'recommendations': recommendations
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(analysis)
    }

def calculate_utilization_metrics(resource_data: Dict) -> Dict:
    """Calculate resource utilization metrics."""
    current_rate = (resource_data['allocation'] / resource_data['capacity']) * 100
    
    # Calculate average and peak rates from history
    history = resource_data.get('history', [])
    if history:
        allocation_history = [
            entry.get('changes', {}).get('allocation', 0)
            for entry in history
        ]
        average_rate = sum(allocation_history) / len(allocation_history)
        peak_rate = max(allocation_history)
    else:
        average_rate = current_rate
        peak_rate = current_rate
    
    return {
        'current_rate': current_rate,
        'average_rate': average_rate,
        'peak_rate': peak_rate
    }

def generate_efficiency_insights(resource_data: Dict) -> List[str]:
    """Generate insights about resource efficiency."""
    insights = []
    metrics = resource_data.get('metrics', {})
    
    # Utilization insights
    utilization = metrics.get('utilization_rate', 0)
    if utilization < 30:
        insights.append("Resource is significantly underutilized")
    elif utilization > 80:
        insights.append("Resource is approaching capacity limits")
    
    # Efficiency insights
    efficiency = metrics.get('efficiency_score', 0)
    if efficiency < 0.6:
        insights.append("Efficiency improvements needed")
    elif efficiency > 0.9:
        insights.append("Resource is operating at optimal efficiency")
    
    # Availability insights
    availability = metrics.get('availability', 100)
    if availability < 90:
        insights.append("Resource availability is below target")
    
    return insights

def analyze_allocation_patterns(resource_data: Dict) -> Dict:
    """Analyze resource allocation patterns."""
    history = resource_data.get('history', [])
    
    # Determine allocation pattern
    if not history:
        pattern = 'stable'
    else:
        changes = [
            entry.get('changes', {}).get('allocation', 0)
            for entry in history[-5:]  # Look at last 5 changes
        ]
        if all(c > 0 for c in changes):
            pattern = 'increasing'
        elif all(c < 0 for c in changes):
            pattern = 'decreasing'
        else:
            pattern = 'fluctuating'
    
    # Calculate stability
    stability = calculate_allocation_stability(history)
    
    # Identify bottlenecks
    bottlenecks = identify_allocation_bottlenecks(resource_data)
    
    return {
        'pattern': pattern,
        'stability': stability,
        'bottlenecks': bottlenecks
    }

def calculate_allocation_stability(history: List[Dict]) -> str:
    """Calculate stability of resource allocation."""
    if not history:
        return 'stable'
    
    # Calculate variance in allocation changes
    changes = [
        abs(entry.get('changes', {}).get('allocation', 0))
        for entry in history
    ]
    
    average_change = sum(changes) / len(changes)
    if average_change < 0.1:
        return 'very_stable'
    elif average_change < 0.3:
        return 'stable'
    elif average_change < 0.5:
        return 'moderate'
    else:
        return 'volatile'

def identify_allocation_bottlenecks(resource_data: Dict) -> List[str]:
    """Identify bottlenecks in resource allocation."""
    bottlenecks = []
    
    # Capacity bottlenecks
    if resource_data['allocation'] > resource_data['capacity'] * 0.9:
        bottlenecks.append('capacity_limit')
    
    # Project allocation bottlenecks
    if len(resource_data.get('projects', [])) > 5:
        bottlenecks.append('project_overallocation')
    
    # Maintenance bottlenecks
    if resource_data.get('maintenance_schedule'):
        bottlenecks.append('maintenance_constraints')
    
    return bottlenecks

def generate_optimization_recommendations(resource_data: Dict) -> List[str]:
    """Generate recommendations for resource optimization."""
    recommendations = []
    
    # Utilization recommendations
    utilization = resource_data['metrics']['utilization_rate']
    if utilization < 50:
        recommendations.append("Consider reallocating resource to other projects")
    elif utilization > 80:
        recommendations.append("Plan for capacity expansion")
    
    # Efficiency recommendations
    efficiency = resource_data['metrics']['efficiency_score']
    if efficiency < 0.7:
        recommendations.append("Implement efficiency improvement measures")
    
    # Allocation recommendations
    if len(resource_data.get('projects', [])) > 3:
        recommendations.append("Review project allocation distribution")
    
    return recommendations 