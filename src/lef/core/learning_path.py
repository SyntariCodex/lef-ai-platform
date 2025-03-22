from typing import Dict, List, Optional
import numpy as np
from datetime import datetime

class LearningPath:
    def __init__(self):
        self.path_segments = {
            'visible': [],
            'hidden': [],
            'completed': []
        }
        # Enhanced objectives with future potential
        self.objectives = {
            'technical': {
                'aws': {
                    'current': ['EC2', 'S3', 'Lambda'],
                    'future_potential': 0.85,  # High potential
                    'prerequisites': ['networking', 'security'],
                    'growth_path': ['ECS', 'EKS', 'Serverless'],
                    'impact_areas': ['scalability', 'cost_efficiency', 'reliability']
                },
                'blockchain': {
                    'current': ['Smart Contracts', 'Token Economics'],
                    'future_potential': 0.92,  # Very high potential
                    'prerequisites': ['cryptography', 'distributed systems'],
                    'growth_path': ['DeFi', 'NFTs', 'DAO Governance'],
                    'impact_areas': ['transparency', 'automation', 'decentralization']
                }
            },
            'business': {
                'project_management': {
                    'current': ['Agile', 'Scrum', 'Kanban'],
                    'future_potential': 0.78,
                    'prerequisites': ['communication', 'leadership'],
                    'growth_path': ['SAFe', 'Lean', 'DevOps'],
                    'impact_areas': ['efficiency', 'team_collaboration', 'delivery_speed']
                },
                'financial_operations': {
                    'current': ['Budgeting', 'Forecasting', 'Analysis'],
                    'future_potential': 0.82,
                    'prerequisites': ['accounting', 'analytics'],
                    'growth_path': ['AI_Finance', 'Blockchain_Finance', 'Sustainable_Finance'],
                    'impact_areas': ['cost_control', 'growth', 'sustainability']
                }
            }
        }
        
        self.learning_state = {
            'current_skills': {},
            'completed_paths': [],
            'active_learning': [],
            'future_potentials': {}
        }
        
    def _calculate_potential_score(self, current_skills: Dict[str, float], 
                                prerequisites: List[str], 
                                base_potential: float) -> float:
        """Calculate future potential score based on prerequisites and current skills"""
        if not prerequisites:
            return base_potential
            
        prerequisite_scores = [
            current_skills.get(prereq, 0.0) 
            for prereq in prerequisites
        ]
        
        # Weighted average of prerequisite scores
        prereq_score = np.mean(prerequisite_scores) if prerequisite_scores else 0.0
        
        # Combine with base potential
        return 0.7 * base_potential + 0.3 * prereq_score
        
    def _get_relevant_objectives(self, trainee_state: Dict) -> List[Dict]:
        """Get objectives with future potential consideration"""
        current_skills = trainee_state.get('skills', {})
        future_potentials = []
        
        for domain, skills in self.objectives.items():
            for skill, details in skills.items():
                # Calculate future potential score
                potential_score = self._calculate_potential_score(
                    current_skills,
                    details['prerequisites'],
                    details['future_potential']
                )
                
                # Calculate impact score
                impact_score = self._calculate_impact_score(
                    details['impact_areas'],
                    trainee_state.get('needs', {})
                )
                
                future_potentials.append({
                    'skill': skill,
                    'domain': domain,
                    'potential': potential_score,
                    'impact': impact_score,
                    'path': details['growth_path'],
                    'prerequisites': details['prerequisites'],
                    'impact_areas': details['impact_areas']
                })
        
        # Sort by combined potential and impact
        return sorted(
            future_potentials,
            key=lambda x: 0.6 * x['potential'] + 0.4 * x['impact'],
            reverse=True
        )
        
    def _calculate_impact_score(self, impact_areas: List[str], 
                              current_needs: Dict[str, float]) -> float:
        """Calculate impact score based on current needs"""
        if not impact_areas or not current_needs:
            return 0.5  # Neutral impact
            
        impact_scores = [
            current_needs.get(area, 0.5)  # Default to neutral if area not found
            for area in impact_areas
        ]
        
        return np.mean(impact_scores)
        
    def update_learning_state(self, new_skills: Dict[str, float], 
                            completed_paths: List[str]):
        """Update the learning state with new skills and completed paths"""
        self.learning_state['current_skills'].update(new_skills)
        self.learning_state['completed_paths'].extend(completed_paths)
        
        # Update future potentials
        self.learning_state['future_potentials'] = {
            skill: self._calculate_potential_score(
                self.learning_state['current_skills'],
                self.objectives[domain][skill]['prerequisites'],
                self.objectives[domain][skill]['future_potential']
            )
            for domain, skills in self.objectives.items()
            for skill in skills
        }
        
    def get_next_learning_objectives(self, trainee_state: Dict) -> List[Dict]:
        """Get the next set of learning objectives based on current state"""
        relevant_objectives = self._get_relevant_objectives(trainee_state)
        
        # Filter out completed paths
        available_objectives = [
            obj for obj in relevant_objectives
            if obj['skill'] not in self.learning_state['completed_paths']
        ]
        
        # Return top 3 most relevant objectives
        return available_objectives[:3]
        
    def get_learning_progress(self) -> Dict:
        """Get current learning progress metrics"""
        total_skills = sum(len(skills) for skills in self.objectives.values())
        completed_skills = len(self.learning_state['completed_paths'])
        
        return {
            'completion_rate': completed_skills / total_skills if total_skills > 0 else 0,
            'active_learning': len(self.learning_state['active_learning']),
            'future_potentials': self.learning_state['future_potentials'],
            'last_update': datetime.now().isoformat()
        } 