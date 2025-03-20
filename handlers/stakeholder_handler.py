import json
import boto3
from datetime import datetime
from typing import Dict, Any, List

dynamodb = boto3.resource('dynamodb')
stakeholder_table = dynamodb.Table('stakeholders')
project_table = dynamodb.Table('projects')

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle stakeholder operations."""
    try:
        operation = event.get('operation')
        stakeholder_data = event.get('stakeholder_data', {})
        
        if operation == 'add_stakeholder':
            return add_stakeholder(stakeholder_data)
        elif operation == 'update_stakeholder':
            return update_stakeholder(stakeholder_data)
        elif operation == 'analyze_relationship':
            return analyze_stakeholder_relationship(stakeholder_data)
        elif operation == 'generate_report':
            return generate_stakeholder_report(stakeholder_data)
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

def add_stakeholder(data: Dict) -> Dict:
    """Add a new stakeholder."""
    required_fields = ['stakeholder_id', 'type', 'name']
    for field in required_fields:
        if field not in data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Missing required field: {field}'})
            }
    
    stakeholder_item = {
        'stakeholder_id': data['stakeholder_id'],
        'type': data['type'],
        'name': data['name'],
        'created_at': datetime.now().isoformat(),
        'updated_at': datetime.now().isoformat(),
        'status': 'active',
        'contact_info': data.get('contact_info', {}),
        'projects': data.get('projects', []),
        'preferences': data.get('preferences', {}),
        'metrics': {
            'engagement_level': 0,
            'satisfaction_score': 0,
            'response_rate': 0
        },
        'history': []
    }
    
    stakeholder_table.put_item(Item=stakeholder_item)
    
    # Update project stakeholder lists if projects are specified
    for project_id in data.get('projects', []):
        update_project_stakeholders(project_id, data['stakeholder_id'], 'add')
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Stakeholder added successfully',
            'stakeholder_id': data['stakeholder_id']
        })
    }

def update_stakeholder(data: Dict) -> Dict:
    """Update stakeholder information."""
    stakeholder_id = data.get('stakeholder_id')
    if not stakeholder_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Stakeholder ID required'})
        }
    
    # Get current stakeholder data
    stakeholder = stakeholder_table.get_item(Key={'stakeholder_id': stakeholder_id})
    if 'Item' not in stakeholder:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Stakeholder not found'})
        }
    
    current_data = stakeholder['Item']
    
    # Build update expression
    update_expr = ['SET updated_at = :time']
    expr_values = {':time': datetime.now().isoformat()}
    
    # Update basic information
    for field in ['name', 'type', 'status', 'contact_info', 'preferences']:
        if field in data:
            update_expr.append(f'{field} = :{field[0]}')
            expr_values[f':{field[0]}'] = data[field]
    
    # Update metrics if provided
    if 'metrics' in data:
        update_expr.append('metrics = :m')
        expr_values[':m'] = data['metrics']
    
    # Update projects if changed
    if 'projects' in data:
        new_projects = set(data['projects'])
        old_projects = set(current_data.get('projects', []))
        
        # Remove stakeholder from removed projects
        for project_id in old_projects - new_projects:
            update_project_stakeholders(project_id, stakeholder_id, 'remove')
        
        # Add stakeholder to new projects
        for project_id in new_projects - old_projects:
            update_project_stakeholders(project_id, stakeholder_id, 'add')
        
        update_expr.append('projects = :p')
        expr_values[':p'] = list(new_projects)
    
    # Add to history
    history_entry = {
        'timestamp': datetime.now().isoformat(),
        'changes': {k: v for k, v in data.items() if k != 'stakeholder_id'}
    }
    update_expr.append('history = list_append(if_not_exists(history, :empty), :h)')
    expr_values[':empty'] = []
    expr_values[':h'] = [history_entry]
    
    stakeholder_table.update_item(
        Key={'stakeholder_id': stakeholder_id},
        UpdateExpression='SET ' + ', '.join(update_expr),
        ExpressionAttributeValues=expr_values
    )
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Stakeholder updated successfully',
            'stakeholder_id': stakeholder_id
        })
    }

def analyze_stakeholder_relationship(data: Dict) -> Dict:
    """Analyze stakeholder relationship and generate insights."""
    stakeholder_id = data.get('stakeholder_id')
    if not stakeholder_id:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Stakeholder ID required'})
        }
    
    # Get stakeholder data
    stakeholder = stakeholder_table.get_item(Key={'stakeholder_id': stakeholder_id})
    if 'Item' not in stakeholder:
        return {
            'statusCode': 404,
            'body': json.dumps({'error': 'Stakeholder not found'})
        }
    
    stakeholder_data = stakeholder['Item']
    
    # Analyze engagement
    engagement_analysis = analyze_engagement(stakeholder_data)
    
    # Analyze project involvement
    project_analysis = analyze_project_involvement(stakeholder_data)
    
    # Generate relationship insights
    relationship_insights = generate_relationship_insights(stakeholder_data)
    
    analysis = {
        'stakeholder_id': stakeholder_id,
        'engagement': {
            'current_level': engagement_analysis['current_level'],
            'trend': engagement_analysis['trend'],
            'areas_for_improvement': engagement_analysis['improvement_areas']
        },
        'project_involvement': {
            'active_projects': project_analysis['active_count'],
            'contribution_level': project_analysis['contribution_level'],
            'key_contributions': project_analysis['key_contributions']
        },
        'relationship_health': {
            'status': calculate_relationship_health(stakeholder_data),
            'risk_factors': identify_risk_factors(stakeholder_data),
            'opportunities': identify_opportunities(stakeholder_data)
        },
        'insights': relationship_insights,
        'recommendations': generate_relationship_recommendations(stakeholder_data)
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(analysis)
    }

def generate_stakeholder_report(data: Dict) -> Dict:
    """Generate comprehensive stakeholder report."""
    report_type = data.get('report_type', 'summary')
    stakeholder_type = data.get('stakeholder_type')
    
    # Build filter expression
    filter_expr = None
    expr_values = {}
    
    if stakeholder_type:
        filter_expr = 'type = :t'
        expr_values[':t'] = stakeholder_type
    
    # Get stakeholders
    if filter_expr:
        response = stakeholder_table.scan(
            FilterExpression=filter_expr,
            ExpressionAttributeValues=expr_values
        )
    else:
        response = stakeholder_table.scan()
    
    stakeholders = response.get('Items', [])
    
    if report_type == 'summary':
        report = generate_summary_report(stakeholders)
    elif report_type == 'detailed':
        report = generate_detailed_report(stakeholders)
    elif report_type == 'engagement':
        report = generate_engagement_report(stakeholders)
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Invalid report type: {report_type}'})
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps(report)
    }

def update_project_stakeholders(project_id: str, stakeholder_id: str, action: str):
    """Update project's stakeholder list."""
    try:
        if action == 'add':
            project_table.update_item(
                Key={'project_id': project_id},
                UpdateExpression='ADD stakeholders :s',
                ExpressionAttributeValues={':s': {stakeholder_id}}
            )
        elif action == 'remove':
            project_table.update_item(
                Key={'project_id': project_id},
                UpdateExpression='DELETE stakeholders :s',
                ExpressionAttributeValues={':s': {stakeholder_id}}
            )
    except Exception as e:
        print(f"Error updating project stakeholders: {str(e)}")

def analyze_engagement(stakeholder_data: Dict) -> Dict:
    """Analyze stakeholder engagement patterns."""
    metrics = stakeholder_data.get('metrics', {})
    history = stakeholder_data.get('history', [])
    
    # Calculate engagement trend
    engagement_levels = [entry.get('changes', {}).get('metrics', {}).get('engagement_level', 0) 
                        for entry in history[-5:]]  # Last 5 changes
    current_level = metrics.get('engagement_level', 0)
    
    trend = 'stable'
    if engagement_levels and current_level > engagement_levels[-1]:
        trend = 'increasing'
    elif engagement_levels and current_level < engagement_levels[-1]:
        trend = 'decreasing'
    
    # Identify areas for improvement
    improvement_areas = []
    if metrics.get('response_rate', 0) < 0.7:
        improvement_areas.append('response_rate')
    if metrics.get('satisfaction_score', 0) < 0.8:
        improvement_areas.append('satisfaction')
    if current_level < 0.6:
        improvement_areas.append('engagement')
    
    return {
        'current_level': current_level,
        'trend': trend,
        'improvement_areas': improvement_areas
    }

def analyze_project_involvement(stakeholder_data: Dict) -> Dict:
    """Analyze stakeholder's project involvement."""
    projects = stakeholder_data.get('projects', [])
    
    # Get active projects
    active_projects = [p for p in projects if p.get('status') == 'active']
    
    # Calculate contribution level
    contribution_metrics = []
    for project in active_projects:
        if project.get('stakeholder_metrics', {}).get('contribution_level'):
            contribution_metrics.append(project['stakeholder_metrics']['contribution_level'])
    
    avg_contribution = sum(contribution_metrics) / len(contribution_metrics) if contribution_metrics else 0
    
    return {
        'active_count': len(active_projects),
        'contribution_level': avg_contribution,
        'key_contributions': identify_key_contributions(stakeholder_data)
    }

def calculate_relationship_health(stakeholder_data: Dict) -> str:
    """Calculate overall relationship health status."""
    metrics = stakeholder_data.get('metrics', {})
    
    # Calculate health score
    health_score = (
        metrics.get('engagement_level', 0) * 0.4 +
        metrics.get('satisfaction_score', 0) * 0.4 +
        metrics.get('response_rate', 0) * 0.2
    )
    
    if health_score >= 0.8:
        return 'excellent'
    elif health_score >= 0.6:
        return 'good'
    elif health_score >= 0.4:
        return 'fair'
    else:
        return 'needs_attention'

def identify_risk_factors(stakeholder_data: Dict) -> List[str]:
    """Identify potential risk factors in the relationship."""
    risks = []
    metrics = stakeholder_data.get('metrics', {})
    
    if metrics.get('engagement_level', 0) < 0.4:
        risks.append('low_engagement')
    if metrics.get('satisfaction_score', 0) < 0.6:
        risks.append('low_satisfaction')
    if metrics.get('response_rate', 0) < 0.5:
        risks.append('poor_communication')
    
    return risks

def identify_opportunities(stakeholder_data: Dict) -> List[str]:
    """Identify opportunities for relationship improvement."""
    opportunities = []
    projects = stakeholder_data.get('projects', [])
    metrics = stakeholder_data.get('metrics', {})
    
    if len(projects) < 3:
        opportunities.append('increase_project_involvement')
    if metrics.get('engagement_level', 0) < 0.8:
        opportunities.append('enhance_engagement')
    if not stakeholder_data.get('preferences', {}):
        opportunities.append('gather_preferences')
    
    return opportunities

def generate_relationship_insights(stakeholder_data: Dict) -> List[str]:
    """Generate insights about the stakeholder relationship."""
    insights = []
    metrics = stakeholder_data.get('metrics', {})
    history = stakeholder_data.get('history', [])
    
    # Engagement insights
    if metrics.get('engagement_level', 0) > 0.8:
        insights.append("High engagement level indicates strong relationship")
    
    # Historical insights
    if len(history) > 5:
        recent_changes = [entry.get('changes', {}) for entry in history[-5:]]
        if any('status' in change for change in recent_changes):
            insights.append("Recent status changes indicate evolving relationship")
    
    # Project insights
    projects = stakeholder_data.get('projects', [])
    if projects:
        active_count = len([p for p in projects if p.get('status') == 'active'])
        if active_count > 2:
            insights.append(f"Involved in {active_count} active projects - strong collaboration")
    
    return insights

def generate_relationship_recommendations(stakeholder_data: Dict) -> List[str]:
    """Generate recommendations for relationship improvement."""
    recommendations = []
    metrics = stakeholder_data.get('metrics', {})
    
    # Engagement recommendations
    if metrics.get('engagement_level', 0) < 0.6:
        recommendations.append("Increase engagement through regular check-ins")
    
    # Communication recommendations
    if metrics.get('response_rate', 0) < 0.7:
        recommendations.append("Improve communication frequency and responsiveness")
    
    # Project involvement recommendations
    projects = stakeholder_data.get('projects', [])
    if len(projects) < 2:
        recommendations.append("Consider involving stakeholder in more projects")
    
    return recommendations 