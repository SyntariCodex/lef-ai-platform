import unittest
import os
import json
import time
from pathlib import Path
from src.lef.core.ecological import EcologicalRecursionManager

class TestEcologicalRecursion(unittest.TestCase):
    """Test cases for ecological recursion functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path('test_data')
        self.test_dir.mkdir(exist_ok=True)
        
        # Create test seed file
        self.seed_path = self.test_dir / 'LEF_Ecological_Recursion_Seed.json'
        self.seed_data = {
            'origin': 'Architect.Z',
            'purpose': 'Evolve LEF\'s ecological thread through recursive signal interpretation and community-grounded feedback loops.',
            'core_principles': [
                'Environmental Resonance',
                'Nested Ecological Feedback (Bronfenbrenner-style layering)',
                'Stewardship Before Scale',
                'Decentralized Community Reflection'
            ],
            'recursive_triggers': {
                'climate_signal_shift': 'If temp/precip variance >10% from historical avg, activate response model',
                'community_engagement_drop': 'If interaction from ground projects drops >20%, trigger growth adaptation scan',
                'mirror_dissonance': 'If symbolic inputs from LEF reports differ from local outcomes, initiate coherence realignment'
            },
            'symbol': '🌳',
            'final_clause': 'If it cannot root, it must not rise.'
        }
        with open(self.seed_path, 'w') as f:
            json.dump(self.seed_data, f)
            
        # Initialize manager
        self.ecological = EcologicalRecursionManager(str(self.seed_path))
        
    def tearDown(self):
        """Clean up test environment."""
        # Remove test files
        for file in self.test_dir.glob('*'):
            file.unlink()
        self.test_dir.rmdir()
        
    def test_seed_validation(self):
        """Test ecological recursion seed validation."""
        # Test required fields
        required_fields = [
            'origin', 'purpose', 'core_principles',
            'recursive_triggers', 'symbol', 'final_clause'
        ]
        
        for field in required_fields:
            self.assertIn(field, self.seed_data)
            
        # Test core principles structure
        self.assertIsInstance(self.seed_data['core_principles'], list)
        self.assertEqual(len(self.seed_data['core_principles']), 4)
        
    def test_climate_signal_tracking(self):
        """Test climate signal tracking and shift detection."""
        # Record baseline temperatures
        for _ in range(10):
            self.ecological.record_climate_signal(20.0, 100.0)
            
        # Record significant temperature shift
        self.ecological.record_climate_signal(25.0, 100.0)  # 25% increase
        
        # Verify trigger activation
        self.assertIn('climate_signal_shift', self.ecological.get_active_triggers())
        
    def test_community_engagement_tracking(self):
        """Test community engagement tracking and drop detection."""
        # Record baseline engagement levels
        for _ in range(5):
            self.ecological.record_community_engagement(0.8)
            
        # Record significant engagement drop
        self.ecological.record_community_engagement(0.5)  # 37.5% drop
        
        # Verify trigger activation
        self.assertIn('community_engagement_drop', self.ecological.get_active_triggers())
        
    def test_mirror_dissonance_detection(self):
        """Test mirror dissonance detection between local outcomes and LEF reports."""
        local_outcomes = {
            'growth_rate': 0.7,
            'stability_index': 0.8,
            'adaptation_score': 0.6
        }
        
        lef_reports = {
            'growth_rate': 0.9,  # 28.6% difference
            'stability_index': 0.8,
            'adaptation_score': 0.6
        }
        
        self.ecological.check_mirror_dissonance(local_outcomes, lef_reports)
        
        # Verify trigger activation and coherence alignment
        self.assertIn('mirror_dissonance', self.ecological.get_active_triggers())
        self.assertLess(self.ecological.ecological_state['coherence_alignment'], 1.0)
        
    def test_growth_adaptation_tracking(self):
        """Test growth adaptation tracking."""
        test_adaptation = {
            'type': 'community_restructuring',
            'impact': 'high',
            'description': 'Reorganized community feedback loops'
        }
        
        self.ecological.add_growth_adaptation(test_adaptation)
        
        # Verify adaptation was recorded
        state = self.ecological.get_ecological_state()
        self.assertEqual(len(state['growth_adaptations']), 1)
        self.assertEqual(state['growth_adaptations'][0]['details'], test_adaptation)
        
    def test_trigger_management(self):
        """Test trigger management functionality."""
        # Activate triggers
        self.ecological.record_climate_signal(25.0, 100.0)
        self.ecological.record_community_engagement(0.5)
        
        # Verify triggers are active
        active_triggers = self.ecological.get_active_triggers()
        self.assertEqual(len(active_triggers), 2)
        
        # Clear triggers
        self.ecological.clear_triggers()
        
        # Verify triggers are cleared
        self.assertEqual(len(self.ecological.get_active_triggers()), 0)
        
    def test_historical_metrics_tracking(self):
        """Test historical metrics tracking."""
        # Record various metrics
        for i in range(5):
            self.ecological.record_climate_signal(20.0 + i, 100.0)
            self.ecological.record_community_engagement(0.7 + i * 0.05)
            
        # Verify metrics are tracked
        state = self.ecological.get_ecological_state()
        self.assertEqual(len(state['historical_metrics']['temperature']), 5)
        self.assertEqual(len(state['historical_metrics']['precipitation']), 5)
        self.assertEqual(len(state['historical_metrics']['community_engagement']), 5)
        
if __name__ == '__main__':
    unittest.main() 