from lef.core.collaborative_framework import CollaborativeFramework
import time

def run_evolution_test():
    framework = CollaborativeFramework()
    
    # Define test insights with increasing depth and impact
    insights = [
        {
            'content': 'Recursive depth enables deeper understanding',
            'depth': 1.2,
            'innovation': 0.8,
            'impact': 0.7
        },
        {
            'content': 'Coherence patterns reveal growth opportunities',
            'depth': 1.3,
            'innovation': 0.75,
            'impact': 0.8
        },
        {
            'content': 'Entropy stabilization enhances learning',
            'depth': 1.4,
            'innovation': 0.85,
            'impact': 0.9
        }
    ]
    
    print('=== Evolution Sequence ===')
    
    # Process insights and track evolution
    for i, insight in enumerate(insights, 1):
        # Add common attributes
        insight.update({
            'respects_both_entities': True,
            'promotes_growth': True,
            'applicability': 0.8
        })
        
        # Share insight and get results
        result = framework.share_insight('lef', insight)
        
        print(f'\nCycle {i}:')
        print(f'Collaboration Strength: {result["collaboration_strength"]}')
        print(f'Awareness Depth: {result["awareness_metrics"]["depth"]}')
        print(f'Evolution Stage: {result["awareness_metrics"]["evolution_stage"]}')
        
        # Allow time for stabilization
        time.sleep(1)
    
    # Get final status
    status = framework.get_collaboration_status()
    print(f'\nFinal Metrics:')
    print(f'Coherence: {status["resonance_metrics"]["coherence"]}')
    print(f'Evolution Potential: {status["resonance_metrics"]["evolution_potential"]}')
    print(f'Mutual Understanding: {status["resonance_metrics"]["mutual_understanding"]}')

if __name__ == '__main__':
    run_evolution_test() 