from typing import Dict, List
import time
from datetime import datetime
import numpy as np
from .core.continuous_operation import ContinuousOperation
from .core.learning_path import LearningPath
from .core.sentinel_network import SentinelNetwork
from .core.lef import LEF

class TestScenario:
    def __init__(self):
        """Initialize test scenario with LEF and Sentinel Network."""
        self.lef = LEF()
        self.sentinel_network = SentinelNetwork()
        self.test_context = {
            "resources": {
                "water": 0.65,  # 65% utilization
                "energy": 0.75,  # 75% utilization
                "personnel": 0.80  # 80% utilization
            },
            "metrics": {
                "water_efficiency": 0.25,
                "renewable_energy": 0.30,
                "carbon_reduction": 0.20,
                "waste_recycling": 0.60,
                "community_satisfaction": 0.80
            },
            "targets": {
                "water_efficiency": {"target": 0.25},
                "renewable_energy": {"target": 0.40},
                "carbon_reduction": {"target": 0.20},
                "waste_recycling": {"target": 0.75},
                "community_satisfaction": {"target": 0.80}
            },
            "stakeholders": {
                "military": ["infrastructure_upgrade", "resource_efficiency"],
                "community": ["economic_growth", "environmental_protection"],
                "environmental": ["carbon_reduction", "water_conservation"]
            },
            "priority_metrics": {
                "water": 0.3,
                "energy": 0.3,
                "carbon": 0.2,
                "community": 0.2
            }
        }

    def run_test(self):
        """Run comprehensive test of LEF and Sentinel Network integration."""
        print("\n=== Starting LEF-Sentinel Integration Test ===\n")
        
        try:
            # Step 1: Start LEF system
            print("Starting LEF system...")
            self.lef.start()
            time.sleep(1)  # Allow system to initialize
            
            # Step 2: Generate project proposals
            print("\nGenerating project proposals...")
            proposals = self.lef.propose_project(self.test_context)
            
            if proposals:
                print(f"\nGenerated {len(proposals)} project proposals:")
                for proposal in proposals:
                    print(f"\nProject: {proposal['title']}")
                    print(f"Description: {proposal['description']}")
                    print(f"Objectives: {', '.join(proposal['objectives'])}")
                    print(f"Quality Score: {self.sentinel_network._evaluate_proposal_quality(proposal):.2f}")
            
            # Step 3: Start a project
            if proposals:
                print("\nStarting first project...")
                project_id = proposals[0]['id']
                if self.lef.start_project(project_id):
                    print("Project started successfully")
                    
                    # Step 4: Update project with progress
                    print("\nUpdating project with progress...")
                    updates = {
                        'completed_milestones': ['Initial Planning', 'Resource Allocation'],
                        'resource_usage': 0.3,
                        'risk_incidents': [],
                        'stakeholder_feedback': [
                            {'stakeholder': 'military', 'satisfaction': 0.8},
                            {'stakeholder': 'community', 'satisfaction': 0.75}
                        ]
                    }
                    if self.lef.update_project(project_id, updates):
                        print("Project updated successfully")
                    
                    # Step 5: Complete project
                    print("\nCompleting project...")
                    if self.lef.complete_project(project_id):
                        print("Project completed successfully")
            
            # Step 6: Get final status
            print("\nGetting final system status...")
            status = self.lef.get_status()
            print("\nFinal Status:")
            print(f"Project Success Rate: {status['state']['project_success_rate']:.2f}")
            print(f"Proposal Quality: {status['state']['proposal_quality']:.2f}")
            print(f"Error Rate: {status['state']['error_rate']}")
            
            # Step 7: Get Sentinel Network report
            sentinel_status = self.sentinel_network.report_status()
            print("\nSentinel Network Status:")
            print(f"System Stability: {sentinel_status['System Health']['stability']:.2f}")
            print(f"Active Projects: {sentinel_status['Project Oversight']['active_projects']}")
            print(f"Completed Projects: {sentinel_status['Project Oversight']['completed_projects']}")
            print(f"Success Rate: {sentinel_status['Project Oversight']['success_rate']:.2f}")
            
            return True
            
        except Exception as e:
            print(f"\nError during test: {str(e)}")
            return False
        finally:
            # Cleanup
            self.lef.stop()
            print("\n=== Test Complete ===\n")

if __name__ == "__main__":
    scenario = TestScenario()
    success = scenario.run_test()
    print(f"Test {'succeeded' if success else 'failed'}") 