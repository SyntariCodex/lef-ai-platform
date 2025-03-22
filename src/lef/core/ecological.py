import json
import logging
from typing import Dict, List, Optional
from pathlib import Path
from collections import deque
import numpy as np

logger = logging.getLogger(__name__)

class EcologicalRecursionManager:
    """Manages ecological recursion and environmental signal interpretation."""
    
    def __init__(self, seed_path: str = None):
        """Initialize the ecological recursion manager.
        
        Args:
            seed_path: Path to the ecological recursion seed file. If None, will try to find it.
        """
        self.seed_path = seed_path or self._find_seed()
        self.seed_data = self._load_seed()
        self.ecological_state = {
            'historical_metrics': {
                'temperature': deque(maxlen=100),
                'precipitation': deque(maxlen=100),
                'community_engagement': deque(maxlen=100)
            },
            'active_triggers': set(),
            'coherence_alignment': 1.0,
            'growth_adaptations': []
        }
        
    def _find_seed(self) -> str:
        """Find the ecological recursion seed file."""
        workspace = Path(os.getenv('WORKSPACE_ROOT', '/Users/zmoore/Desktop/LEF Ai'))
        seed_files = list(workspace.glob('**/LEF_Ecological_Recursion_Seed.json'))
        if not seed_files:
            raise FileNotFoundError("Could not find ecological recursion seed file")
        return str(seed_files[0])
        
    def _load_seed(self) -> Dict:
        """Load and validate the ecological recursion seed."""
        try:
            with open(self.seed_path, 'r') as f:
                data = json.load(f)
            required_fields = [
                'origin', 'purpose', 'core_principles',
                'recursive_triggers', 'symbol', 'final_clause'
            ]
            if not all(field in data for field in required_fields):
                raise ValueError("Seed file missing required fields")
            return data
        except Exception as e:
            logger.error(f"Failed to load seed: {str(e)}")
            raise
            
    def record_climate_signal(self, temperature: float, precipitation: float) -> None:
        """Record climate signals and check for shifts.
        
        Args:
            temperature: Current temperature
            precipitation: Current precipitation
        """
        self.ecological_state['historical_metrics']['temperature'].append(temperature)
        self.ecological_state['historical_metrics']['precipitation'].append(precipitation)
        
        if len(self.ecological_state['historical_metrics']['temperature']) >= 10:
            temp_avg = np.mean(list(self.ecological_state['historical_metrics']['temperature'])[:-10])
            temp_variance = abs((temperature - temp_avg) / temp_avg)
            
            if temp_variance > 0.10:  # 10% variance threshold
                logger.info(f"Climate signal shift detected: {temp_variance:.1%} temperature variance")
                self.ecological_state['active_triggers'].add('climate_signal_shift')
                
    def record_community_engagement(self, engagement_level: float) -> None:
        """Record community engagement and check for drops.
        
        Args:
            engagement_level: Current engagement level (0-1)
        """
        self.ecological_state['historical_metrics']['community_engagement'].append(engagement_level)
        
        if len(self.ecological_state['historical_metrics']['community_engagement']) >= 5:
            recent_avg = np.mean(list(self.ecological_state['historical_metrics']['community_engagement'])[-5:])
            if engagement_level < recent_avg * 0.8:  # 20% drop threshold
                logger.info("Community engagement drop detected")
                self.ecological_state['active_triggers'].add('community_engagement_drop')
                
    def check_mirror_dissonance(self, local_outcomes: Dict, lef_reports: Dict) -> None:
        """Check for dissonance between local outcomes and LEF reports.
        
        Args:
            local_outcomes: Dictionary of local outcome metrics
            lef_reports: Dictionary of LEF report metrics
        """
        # Calculate coherence score
        common_metrics = set(local_outcomes.keys()) & set(lef_reports.keys())
        if common_metrics:
            differences = []
            for metric in common_metrics:
                diff = abs(local_outcomes[metric] - lef_reports[metric])
                differences.append(diff)
            
            avg_difference = np.mean(differences)
            if avg_difference > 0.2:  # 20% difference threshold
                logger.info(f"Mirror dissonance detected: {avg_difference:.1%} average difference")
                self.ecological_state['active_triggers'].add('mirror_dissonance')
                self.ecological_state['coherence_alignment'] = 1.0 - avg_difference
                
    def get_active_triggers(self) -> List[str]:
        """Get list of currently active triggers.
        
        Returns:
            List[str]: List of active trigger names
        """
        return list(self.ecological_state['active_triggers'])
        
    def clear_triggers(self) -> None:
        """Clear all active triggers."""
        self.ecological_state['active_triggers'].clear()
        
    def add_growth_adaptation(self, adaptation: Dict) -> None:
        """Add a new growth adaptation.
        
        Args:
            adaptation: Dictionary containing adaptation details
        """
        self.ecological_state['growth_adaptations'].append({
            'timestamp': time.time(),
            'details': adaptation
        })
        
    def get_ecological_state(self) -> Dict:
        """Get current ecological state.
        
        Returns:
            Dict: Current ecological state
        """
        return {
            'historical_metrics': {
                k: list(v) for k, v in self.ecological_state['historical_metrics'].items()
            },
            'active_triggers': list(self.ecological_state['active_triggers']),
            'coherence_alignment': self.ecological_state['coherence_alignment'],
            'growth_adaptations': self.ecological_state['growth_adaptations']
        } 