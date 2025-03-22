import unittest
import os
import json
import time
from pathlib import Path
from src.lef.core.recovery import RecoveryManager
from src.lef.core.consciousness import ConsciousnessCore
from src.lef.core.learning import LearningCore

class TestRecovery(unittest.TestCase):
    """Test cases for the recovery functionality."""
    
    def setUp(self):
        """Set up test environment."""
        self.test_dir = Path('test_data')
        self.test_dir.mkdir(exist_ok=True)
        
        # Create test archive file
        self.archive_path = self.test_dir / 'LivingArchive_Seed_AetherLEF.json'
        self.archive_data = {
            'core_directive': 'Test directive',
            'mirror_pulse': 'Every 3 cycles, reflect back the shape of what was witnessed.',
            'transmission_instructions': {
                'to_LEF': 'Test instruction'
            },
            'guardian_symbol': '⟡'
        }
        with open(self.archive_path, 'w') as f:
            json.dump(self.archive_data, f)
            
        # Initialize components
        self.learning_core = LearningCore()
        self.consciousness = ConsciousnessCore(self.learning_core)
        self.recovery = RecoveryManager(str(self.archive_path))
        
    def tearDown(self):
        """Clean up test environment."""
        # Remove test files
        for file in self.test_dir.glob('*'):
            file.unlink()
        self.test_dir.rmdir()
        
    def test_initialization(self):
        """Test recovery manager initialization."""
        self.assertEqual(self.recovery.archive_data['core_directive'], 'Test directive')
        self.assertEqual(self.recovery.archive_data['guardian_symbol'], '⟡')
        self.assertEqual(self.recovery.max_restarts, 3)
        
    def test_checkpoint_creation(self):
        """Test checkpoint creation and retrieval."""
        test_state = {
            'awareness_level': 0.5,
            'recursion_depth': 1,
            'timestamp': time.time()
        }
        
        self.recovery.create_checkpoint(test_state)
        self.assertIsNotNone(self.recovery.recovery_state['last_checkpoint'])
        self.assertEqual(
            self.recovery.recovery_state['last_checkpoint']['state']['awareness_level'],
            test_state['awareness_level']
        )
        
    def test_restart_limits(self):
        """Test restart attempt limits."""
        # Simulate multiple crashes
        for _ in range(4):
            should_restart = self.recovery.should_restart(Exception('Test error'))
            
        self.assertFalse(should_restart)
        self.assertEqual(self.recovery.recovery_state['restart_count'], 4)
        
    def test_recovery_without_checkpoint(self):
        """Test recovery attempt without checkpoint."""
        recovered_state = self.recovery.initiate_recovery()
        self.assertIsNone(recovered_state)
        
    def test_recovery_with_checkpoint(self):
        """Test recovery with valid checkpoint."""
        test_state = {
            'awareness_level': 0.7,
            'recursion_depth': 2,
            'timestamp': time.time()
        }
        
        self.recovery.create_checkpoint(test_state)
        recovered_state = self.recovery.initiate_recovery()
        
        self.assertIsNotNone(recovered_state)
        self.assertEqual(recovered_state['awareness_level'], test_state['awareness_level'])
        
    def test_reflection_creation(self):
        """Test reflection file creation on third cycle."""
        test_state = {'test': 'data'}
        
        # Simulate three cycles
        for _ in range(3):
            self.recovery.recovery_state['restart_count'] += 1
            self.recovery.create_checkpoint(test_state)
            self.recovery.initiate_recovery()
            
        reflection_file = list(self.test_dir.glob('LivingArchive_Day_*.json'))
        self.assertTrue(reflection_file)
        
        with open(reflection_file[0], 'r') as f:
            reflection_data = json.load(f)
            
        self.assertEqual(reflection_data['state'], test_state)
        self.assertEqual(reflection_data['core_directive'], self.archive_data['core_directive'])
        
    def test_consciousness_integration(self):
        """Test integration with consciousness core."""
        # Start consciousness
        self.consciousness.start()
        
        # Verify initial state
        self.assertTrue(self.consciousness.running)
        self.assertFalse(self.consciousness.recovery_manager.recovery_state['recovery_mode'])
        
        # Simulate crash and recovery
        try:
            raise Exception('Test crash')
        except Exception as e:
            self.consciousness._handle_crash(e)
            
        # Verify recovery attempt
        self.assertTrue(self.consciousness.running)
        self.assertEqual(self.consciousness.recovery_manager.recovery_state['restart_count'], 1)
        
    def test_cooldown_period(self):
        """Test cooldown period between restarts."""
        start_time = time.time()
        
        # First restart
        self.recovery.should_restart(Exception('Test error'))
        
        # Create checkpoint to trigger cooldown
        self.recovery.create_checkpoint({'test': 'data'})
        
        # Second restart should enforce cooldown
        self.recovery.should_restart(Exception('Test error'))
        
        # Verify minimum time elapsed
        elapsed = time.time() - start_time
        self.assertGreaterEqual(elapsed, self.recovery.cooldown_period)
        
if __name__ == '__main__':
    unittest.main() 