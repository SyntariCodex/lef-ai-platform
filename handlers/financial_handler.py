import json
import boto3
from datetime import datetime
from typing import Dict, Any, List
from decimal import Decimal

dynamodb = boto3.resource('dynamodb')
finance_table = dynamodb.Table('finances')
project_table = dynamodb.Table('projects')

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle financial operations."""
    try:
        operation = event.get('operation')
        financial_data = event.get('financial_data', {})
        
        if operation == 'record_transaction':
            return record_transaction(financial_data)
        elif operation == 'analyze_finances':
            return analyze_finances(financial_data)
        elif operation == 'generate_report':
            return generate_financial_report(financial_data)
        elif operation == 'forecast':
            return generate_financial_forecast(financial_data)
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

def record_transaction(data: Dict) -> Dict:
    """Record a financial transaction."""
    required_fields = ['transaction_id', 'type', 'amount', 'category']
    for field in required_fields:
        if field not in data:
            return {
                'statusCode': 400,
                'body': json.dumps({'error': f'Missing required field: {field}'})
            }
    
    transaction_item = {
        'transaction_id': data['transaction_id'],
        'type': data['type'],
        'amount': Decimal(str(data['amount'])),
        'category': data['category'],
        'timestamp': datetime.now().isoformat(),
        'description': data.get('description', ''),
        'project_id': data.get('project_id'),
        'status': 'completed',
        'metadata': data.get('metadata', {})
    }
    
    finance_table.put_item(Item=transaction_item)
    
    # Update project financials if associated with a project
    if data.get('project_id'):
        update_project_financials(data['project_id'], data['type'], Decimal(str(data['amount'])))
    
    return {
        'statusCode': 200,
        'body': json.dumps({
            'message': 'Transaction recorded successfully',
            'transaction_id': data['transaction_id']
        })
    }

def analyze_finances(data: Dict) -> Dict:
    """Analyze financial data and generate insights."""
    start_date = data.get('start_date', (datetime.now() - timedelta(days=30)).isoformat())
    end_date = data.get('end_date', datetime.now().isoformat())
    category = data.get('category')
    project_id = data.get('project_id')
    
    # Build filter expression
    filter_expr = 'timestamp BETWEEN :start AND :end'
    expr_values = {
        ':start': start_date,
        ':end': end_date
    }
    
    if category:
        filter_expr += ' AND category = :cat'
        expr_values[':cat'] = category
    
    if project_id:
        filter_expr += ' AND project_id = :pid'
        expr_values[':pid'] = project_id
    
    # Query transactions
    response = finance_table.scan(
        FilterExpression=filter_expr,
        ExpressionAttributeValues=expr_values
    )
    
    transactions = response.get('Items', [])
    
    # Calculate metrics
    total_revenue = sum(t['amount'] for t in transactions if t['type'] == 'revenue')
    total_expenses = sum(t['amount'] for t in transactions if t['type'] == 'expense')
    net_income = total_revenue - total_expenses
    
    # Calculate category breakdown
    category_breakdown = {}
    for t in transactions:
        cat = t['category']
        if cat not in category_breakdown:
            category_breakdown[cat] = {'revenue': 0, 'expenses': 0}
        if t['type'] == 'revenue':
            category_breakdown[cat]['revenue'] += t['amount']
        else:
            category_breakdown[cat]['expenses'] += t['amount']
    
    analysis = {
        'period': {
            'start': start_date,
            'end': end_date
        },
        'summary': {
            'total_revenue': float(total_revenue),
            'total_expenses': float(total_expenses),
            'net_income': float(net_income),
            'transaction_count': len(transactions)
        },
        'category_breakdown': {k: {
            'revenue': float(v['revenue']),
            'expenses': float(v['expenses']),
            'net': float(v['revenue'] - v['expenses'])
        } for k, v in category_breakdown.items()},
        'insights': generate_financial_insights(transactions)
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(analysis)
    }

def generate_financial_report(data: Dict) -> Dict:
    """Generate detailed financial report."""
    report_type = data.get('report_type', 'summary')
    period = data.get('period', 'monthly')
    start_date = data.get('start_date', (datetime.now() - timedelta(days=30)).isoformat())
    end_date = data.get('end_date', datetime.now().isoformat())
    
    # Get transactions for the period
    response = finance_table.scan(
        FilterExpression='timestamp BETWEEN :start AND :end',
        ExpressionAttributeValues={
            ':start': start_date,
            ':end': end_date
        }
    )
    
    transactions = response.get('Items', [])
    
    if report_type == 'summary':
        report = generate_summary_report(transactions, period)
    elif report_type == 'detailed':
        report = generate_detailed_report(transactions, period)
    elif report_type == 'project':
        report = generate_project_report(transactions, period)
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({'error': f'Invalid report type: {report_type}'})
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps(report)
    }

def generate_financial_forecast(data: Dict) -> Dict:
    """Generate financial forecasts."""
    forecast_period = data.get('period', 12)  # Default to 12 months
    confidence_level = data.get('confidence_level', 0.95)
    
    # Get historical data for modeling
    historical_data = get_historical_financial_data()
    
    # Generate forecasts
    revenue_forecast = generate_revenue_forecast(historical_data, forecast_period)
    expense_forecast = generate_expense_forecast(historical_data, forecast_period)
    cash_flow_forecast = generate_cash_flow_forecast(historical_data, forecast_period)
    
    forecast = {
        'period': forecast_period,
        'confidence_level': confidence_level,
        'revenue': {
            'forecast': revenue_forecast,
            'growth_rate': calculate_growth_rate(revenue_forecast),
            'risk_factors': identify_revenue_risks(historical_data)
        },
        'expenses': {
            'forecast': expense_forecast,
            'trend': analyze_expense_trend(expense_forecast),
            'optimization_opportunities': identify_cost_savings(historical_data)
        },
        'cash_flow': {
            'forecast': cash_flow_forecast,
            'liquidity_analysis': analyze_liquidity(cash_flow_forecast),
            'recommendations': generate_cash_flow_recommendations(cash_flow_forecast)
        }
    }
    
    return {
        'statusCode': 200,
        'body': json.dumps(forecast)
    }

def update_project_financials(project_id: str, transaction_type: str, amount: Decimal):
    """Update project financial metrics."""
    try:
        project = project_table.get_item(Key={'project_id': project_id})
        if 'Item' not in project:
            return
        
        project_data = project['Item']
        financials = project_data.get('financials', {
            'total_revenue': Decimal('0'),
            'total_expenses': Decimal('0'),
            'net_income': Decimal('0')
        })
        
        if transaction_type == 'revenue':
            financials['total_revenue'] += amount
        else:
            financials['total_expenses'] += amount
            
        financials['net_income'] = financials['total_revenue'] - financials['total_expenses']
        
        project_table.update_item(
            Key={'project_id': project_id},
            UpdateExpression='SET financials = :f',
            ExpressionAttributeValues={':f': financials}
        )
    except Exception as e:
        print(f"Error updating project financials: {str(e)}")

def generate_financial_insights(transactions: List[Dict]) -> List[str]:
    """Generate insights from financial data."""
    insights = []
    
    # Revenue insights
    revenue_trend = analyze_revenue_trend(transactions)
    if revenue_trend['growth_rate'] < 0:
        insights.append(f"Revenue declining at {abs(revenue_trend['growth_rate'])}% rate")
    elif revenue_trend['growth_rate'] > 20:
        insights.append(f"Strong revenue growth at {revenue_trend['growth_rate']}% rate")
    
    # Expense insights
    expense_analysis = analyze_expenses(transactions)
    if expense_analysis['unusual_expenses']:
        insights.append("Detected unusual expense patterns in categories: " + 
                       ", ".join(expense_analysis['unusual_expenses']))
    
    # Cash flow insights
    cash_flow = analyze_cash_flow(transactions)
    if cash_flow['status'] == 'negative':
        insights.append("Negative cash flow trend detected - review expense management")
    
    # Project profitability
    project_metrics = analyze_project_profitability(transactions)
    for project_id, metrics in project_metrics.items():
        if metrics['profit_margin'] < 0.1:
            insights.append(f"Low profit margin ({metrics['profit_margin']*100}%) for project {project_id}")
    
    return insights

def analyze_revenue_trend(transactions: List[Dict]) -> Dict:
    """Analyze revenue trends."""
    # Implementation details
    return {'growth_rate': 0.0}

def analyze_expenses(transactions: List[Dict]) -> Dict:
    """Analyze expense patterns."""
    # Implementation details
    return {'unusual_expenses': []}

def analyze_cash_flow(transactions: List[Dict]) -> Dict:
    """Analyze cash flow patterns."""
    # Implementation details
    return {'status': 'positive'}

def analyze_project_profitability(transactions: List[Dict]) -> Dict:
    """Analyze profitability by project."""
    # Implementation details
    return {} 