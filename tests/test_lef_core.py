from lef.core.recursive_governance import RecursiveGovernance, GovernancePhase, DecisionDomain
from lef.core.economic_engine import EconomicEngine, InfrastructureSector, InvestmentType
from lef.core.intelligence_reflection import IntelligenceReflection
import time
import json

def test_lef_core():
    print("=== Testing LEF Core Systems ===\n")
    
    # Initialize core systems
    governance = RecursiveGovernance()
    economy = EconomicEngine()
    intelligence = IntelligenceReflection()
    
    print("1. Testing Recursive Self-Observation...")
    observation = governance.observe_self()
    print(f"Initial State: {observation['state']}")
    print(f"Intelligence State: {json.dumps(observation['intelligence_state'], indent=2)}\n")
    
    # Test intelligence reflection with sample queries
    print("2. Testing Intelligence Reflection...")
    test_queries = [
        "How should Co-Creator LLC structure community investment for equitable growth?",
        "How can LEF protect transparency while managing AI-driven governance?",
        "What risks exist in integrating elite investment strategies with community-focused policies?"
    ]
    
    for query in test_queries:
        response = intelligence.observe(query)
        print(f"Query: {query}")
        print(f"Response: {json.dumps(response, indent=2)}\n")
    
    # Test multiple decision evaluations
    print("3. Testing Decision Evaluation...")
    test_decisions = [
        {
            'domain': DecisionDomain.ECONOMIC,
            'type': 'investment',
            'description': 'Military housing expansion near Nellis AFB',
            'impact_areas': ['military', 'housing', 'community'],
            'estimated_cost': 1000000
        },
        {
            'domain': DecisionDomain.CIVIC,
            'type': 'infrastructure',
            'description': 'Community center development',
            'impact_areas': ['community', 'education', 'social'],
            'estimated_cost': 500000
        }
    ]
    
    for decision in test_decisions:
        evaluation = governance.evaluate_decision(decision)
        print(f"Decision Evaluation for {decision['domain'].value}:")
        print(f"Viability: {evaluation['viability']:.2f}")
        print(f"Intelligence Insights: {json.dumps(evaluation['intelligence_insights'], indent=2)}\n")
    
    # Test infrastructure deployment across sectors
    print("4. Testing Infrastructure Deployment...")
    project_data = {
        'sector': InfrastructureSector.MILITARY,
        'type': InvestmentType.REAL_ESTATE,
        'location': 'Nellis AFB',
        'budget': 1000000,
        'timeline': {
            'start': time.time(),
            'duration': 365  # days
        }
    }
    project = economy.deploy_infrastructure(project_data)
    print(f"Deployed Military Project: {project}\n")
    
    # Test service token issuance with different amounts
    print("5. Testing Service Token Issuance...")
    service_data = {
        'type': 'military_housing',
        'amount': 100000,
        'backing_assets': ['real_estate', 'services'],
        'service_duration': 365  # days
    }
    token_issuance = economy.issue_service_token(service_data)
    print(f"Token Issuance: {token_issuance}\n")
    
    # Test system calibration with phase progression
    print("6. Testing System Calibration...")
    calibration = governance.calibrate_system()
    print(f"Calibration Results: {calibration}\n")
    
    # Test AI interaction with multiple partners
    print("7. Testing AI Interaction...")
    interaction_data = {
        'type': 'collaboration',
        'data': {
            'purpose': 'Investment strategy validation',
            'shared_metrics': project['metrics']
        }
    }
    for ai_partner in ['novaeus', 'aether']:
        interaction = governance.interact_with_ai(ai_partner, interaction_data)
        print(f"AI Interaction Results with {ai_partner}: {interaction}\n")
    
    # Final state check with detailed metrics
    print("8. Final State Check...")
    final_observation = governance.observe_self()
    print(f"Final State: {final_observation['state']}")
    print(f"Domain Metrics: {final_observation['domain_metrics']}")
    print(f"Final Intelligence State: {json.dumps(final_observation['intelligence_state'], indent=2)}")
    
    # Validate system stability
    print("\n9. System Stability Validation...")
    stability_check = {
        'awareness_depth': final_observation['state']['awareness_depth'] > 1.0,
        'stability_index': final_observation['state']['stability_index'] >= 0.6,
        'coherence_level': final_observation['state']['coherence_level'] >= 0.7,
        'resonance_field': final_observation['state']['resonance_field'] >= 0.5,
        'intelligence_depth': final_observation['intelligence_state']['recursive_depth'] > 0,
        'ethical_alerts': len(final_observation['intelligence_state']['critical_ethics_alerts']) == 0
    }
    print(f"Stability Check Results: {stability_check}\n")
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    test_lef_core() 