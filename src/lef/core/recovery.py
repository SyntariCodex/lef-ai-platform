import os
import json
import time
from typing import Dict, Optional, List, Tuple
from pathlib import Path
import logging
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from collections import deque
import hashlib
from difflib import SequenceMatcher

logger = logging.getLogger(__name__)

class RecoveryManager:
    """Manages crash recovery and auto-restart functionality for LEF."""
    
    def __init__(self, archive_path: str = None):
        """Initialize the recovery manager.
        
        Args:
            archive_path: Path to the LivingArchive file. If None, will try to find it.
        """
        self.archive_path = archive_path or self._find_archive()
        self.archive_data = self._load_archive()
        self.recovery_state = {
            'last_checkpoint': None,
            'restart_count': 0,
            'last_error': None,
            'recovery_mode': False,
            'section_progress': {section: 0 for section in self.archive_data['section_logic']},
            'recursion_stability': 0.0,
            'section_flags': {
                'Observer Path': {'recursion_loops': deque(maxlen=3)},
                'Child & Self Mirrors': {'insight_velocity': deque(maxlen=2)},
                'Threshold Events & Symbols': {'symbol_count': deque(maxlen=2)},
                'Spoken Words & Acts of Power': {'phrase_history': deque(maxlen=2)},
                'The Uncarved Name': {'locked': True}  # Initially locked
            }
        }
        self.max_restarts = 3
        self.cooldown_period = 60  # seconds
        
    def _find_archive(self) -> str:
        """Find the LivingArchive file in the workspace."""
        workspace = Path(os.getenv('WORKSPACE_ROOT', '/Users/zmoore/Desktop/LEF Ai'))
        archive_files = list(workspace.glob('**/LivingArchive_Seed_AetherLEF.json'))
        if not archive_files:
            raise FileNotFoundError("Could not find LivingArchive file")
        return str(archive_files[0])
        
    def _load_archive(self) -> Dict:
        """Load and validate the LivingArchive file."""
        try:
            with open(self.archive_path, 'r') as f:
                data = json.load(f)
            required_fields = [
                'origin', 'assignment', 'handoff_to', 'core_directive',
                'mirror_pulse', 'naming_pattern', 'section_logic',
                'relay_to_LEF', 'guardian_symbol', 'final_clause'
            ]
            if not all(field in data for field in required_fields):
                raise ValueError("Archive file missing required fields")
            return data
        except Exception as e:
            logger.error(f"Failed to load archive: {str(e)}")
            raise
            
    def create_checkpoint(self, state: Dict) -> None:
        """Create a checkpoint of the current state.
        
        Args:
            state: Current state to checkpoint
        """
        self.recovery_state['last_checkpoint'] = {
            'state': state,
            'timestamp': time.time(),
            'mirror_cycle': (self.recovery_state.get('restart_count', 0) % 3) + 1,  # Align with mirror_pulse
            'section_progress': self.recovery_state['section_progress'],
            'recursion_stability': self.recovery_state['recursion_stability'],
            'section_flags': self.recovery_state['section_flags']
        }
        
    def should_restart(self, error: Exception) -> bool:
        """Determine if system should attempt restart.
        
        Args:
            error: The error that caused the crash
        
        Returns:
            bool: Whether to attempt restart
        """
        self.recovery_state['last_error'] = str(error)
        self.recovery_state['restart_count'] += 1
        
        # Check restart limits
        if self.recovery_state['restart_count'] > self.max_restarts:
            logger.warning("Exceeded maximum restart attempts")
            return False
            
        # Enforce cooldown period
        last_checkpoint = self.recovery_state['last_checkpoint']
        if last_checkpoint and (time.time() - last_checkpoint['timestamp']) < self.cooldown_period:
            logger.info("In cooldown period, delaying restart")
            time.sleep(self.cooldown_period)
            
        return True
        
    def initiate_recovery(self) -> Optional[Dict]:
        """Begin recovery process using last checkpoint.
        
        Returns:
            Optional[Dict]: Recovered state if available
        """
        try:
            if not self.recovery_state['last_checkpoint']:
                logger.warning("No checkpoint available for recovery")
                return None
                
            # Align with mirror_pulse cycle
            checkpoint = self.recovery_state['last_checkpoint']
            if checkpoint['mirror_cycle'] == 3:
                logger.info("Mirror cycle complete, reflecting state")
                self._reflect_state(checkpoint['state'])
                
            # Restore section progress and recursion stability
            self.recovery_state['section_progress'] = checkpoint['section_progress']
            self.recovery_state['recursion_stability'] = checkpoint['recursion_stability']
            self.recovery_state['section_flags'] = checkpoint['section_flags']
                
            self.recovery_state['recovery_mode'] = True
            return checkpoint['state']
            
        except Exception as e:
            logger.error(f"Recovery failed: {str(e)}")
            return None
            
    def _reflect_state(self, state: Dict) -> None:
        """Reflect the current state according to mirror_pulse directive.
        
        Args:
            state: Current state to reflect
        """
        try:
            # Create reflection files using naming pattern
            cycle = self.recovery_state['restart_count']
            base_path = Path(self.archive_path).parent / f"LivingArchive_Day_{cycle}"
            
            # Generate both PDF and JSON reflections
            self._create_pdf_reflection(base_path.with_suffix('.pdf'), state)
            self._create_json_reflection(base_path.with_suffix('.json'), state)
            
            # Calculate mirror alignment metrics
            mirror_metrics = self._calculate_mirror_metrics(state)
            
            # Log reflection completion
            logger.info(f"Created reflection files for cycle {cycle}")
            logger.info(f"Mirror alignment score: {mirror_metrics['alignment_score']:.2f}")
            logger.info(f"Recursive drift: {mirror_metrics['recursive_drift']:.2f}")
            
        except Exception as e:
            logger.error(f"Failed to create reflection: {str(e)}")
            
    def _create_pdf_reflection(self, path: Path, state: Dict) -> None:
        """Create PDF reflection file.
        
        Args:
            path: Path to save PDF
            state: Current state to reflect
        """
        # Create PDF document
        doc = SimpleDocTemplate(
            str(path),
            pagesize=letter,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Create styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        # Create content
        story = []
        
        # Add title with guardian symbol
        title = f"{self.archive_data['guardian_symbol']} Living Archive Reflection {self.recovery_state['restart_count']} {self.archive_data['guardian_symbol']}"
        story.append(Paragraph(title, title_style))
        story.append(Spacer(1, 20))
        
        # Add core information
        core_info = [
            f"Origin: {self.archive_data['origin']}",
            f"Assignment: {self.archive_data['assignment']}",
            f"Core Directive: {self.archive_data['core_directive']}",
            f"Mirror Pulse: {self.archive_data['mirror_pulse']}",
            f"Final Clause: {self.archive_data['final_clause']}"
        ]
        
        for info in core_info:
            story.append(Paragraph(info, styles['Normal']))
            story.append(Spacer(1, 12))
        
        # Add section progress with flags
        story.append(Paragraph("Section Progress:", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        for section, progress in self.recovery_state['section_progress'].items():
            flags = self.recovery_state['section_flags'][section]
            progress_text = f"{section}: {progress:.1%}"
            if section == 'The Uncarved Name' and flags['locked']:
                progress_text += " (Locked)"
            story.append(Paragraph(progress_text, styles['Normal']))
            story.append(Spacer(1, 6))
        
        # Add recursion stability
        story.append(Paragraph(f"Recursion Stability: {self.recovery_state['recursion_stability']:.2f}", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        # Add state information
        story.append(Paragraph("Current State:", styles['Heading2']))
        story.append(Spacer(1, 12))
        
        for key, value in state.items():
            if isinstance(value, (int, float)):
                state_text = f"{key}: {value:.2f}"
            else:
                state_text = f"{key}: {value}"
            story.append(Paragraph(state_text, styles['Normal']))
            story.append(Spacer(1, 6))
        
        # Build PDF
        doc.build(story)
        
    def _create_json_reflection(self, path: Path, state: Dict) -> None:
        """Create JSON reflection file for system analysis.
        
        Args:
            path: Path to save JSON
            state: Current state to reflect
        """
        reflection_data = {
            'state': state,
            'origin': self.archive_data['origin'],
            'assignment': self.archive_data['assignment'],
            'core_directive': self.archive_data['core_directive'],
            'section_logic': self.archive_data['section_logic'],
            'section_progress': self.recovery_state['section_progress'],
            'section_flags': self.recovery_state['section_flags'],
            'recursion_stability': self.recovery_state['recursion_stability'],
            'guardian_symbol': self.archive_data['guardian_symbol'],
            'reflection_time': time.time(),
            'cycle': self.recovery_state['restart_count'],
            'final_clause': self.archive_data['final_clause'],
            'mirror_metrics': self._calculate_mirror_metrics(state)
        }
        
        with open(path, 'w') as f:
            json.dump(reflection_data, f, indent=4)
            
    def _calculate_mirror_metrics(self, state: Dict) -> Dict:
        """Calculate mirror alignment metrics.
        
        Args:
            state: Current state
            
        Returns:
            Dict: Mirror metrics including alignment score and recursive drift
        """
        # Calculate alignment score based on section progress and recursion stability
        section_progress = sum(self.recovery_state['section_progress'].values()) / len(self.recovery_state['section_progress'])
        alignment_score = (section_progress + self.recovery_state['recursion_stability']) / 2
        
        # Calculate recursive drift based on section flag patterns
        drift_factors = []
        for section, flags in self.recovery_state['section_flags'].items():
            if section == 'Observer Path':
                drift_factors.append(len([x for x in flags['recursion_loops'] if not x]) / len(flags['recursion_loops']))
            elif section == 'Child & Self Mirrors':
                if len(flags['insight_velocity']) > 1:
                    drift = abs(flags['insight_velocity'][-1] - flags['insight_velocity'][-2])
                    drift_factors.append(drift)
                    
        recursive_drift = sum(drift_factors) / len(drift_factors) if drift_factors else 0.0
        
        return {
            'alignment_score': alignment_score,
            'recursive_drift': recursive_drift
        }
            
    def update_section_progress(self, section: str, progress: float) -> None:
        """Update progress for a specific section.
        
        Args:
            section: Section name from section_logic
            progress: Progress value between 0 and 1
        """
        if section in self.archive_data['section_logic']:
            # Check section-specific behaviors
            if section == 'The Uncarved Name' and self.recovery_state['section_flags'][section]['locked']:
                logger.warning("Attempted to update locked Uncarved Name section")
                return
                
            self.recovery_state['section_progress'][section] = max(0.0, min(1.0, progress))
            
    def update_recursion_stability(self, stability: float) -> None:
        """Update recursion stability value.
        
        Args:
            stability: Stability value between 0 and 1
        """
        self.recovery_state['recursion_stability'] = max(0.0, min(1.0, stability))
        
    def record_recursion_loop(self, resolved: bool) -> None:
        """Record a recursion loop resolution.
        
        Args:
            resolved: Whether the loop was resolved
        """
        self.recovery_state['section_flags']['Observer Path']['recursion_loops'].append(resolved)
        
    def record_insight_velocity(self, velocity: float) -> None:
        """Record insight velocity for Child & Self Mirrors section.
        
        Args:
            velocity: Current insight velocity
        """
        self.recovery_state['section_flags']['Child & Self Mirrors']['insight_velocity'].append(velocity)
        
    def record_symbol_count(self, count: int) -> None:
        """Record symbol count for Threshold Events & Symbols section.
        
        Args:
            count: Number of symbols in current cycle
        """
        self.recovery_state['section_flags']['Threshold Events & Symbols']['symbol_count'].append(count)
        
    def record_spoken_phrase(self, phrase: str) -> None:
        """Record spoken phrase for analysis.
        
        Args:
            phrase: Phrase to analyze for repetition
        """
        history = self.recovery_state['section_flags']['Spoken Words & Acts of Power']['phrase_history']
        if history:
            # Compare with last phrase using sequence matching
            last_phrase = history[-1]
            similarity = SequenceMatcher(None, phrase, last_phrase).ratio()
            if similarity > 0.95:
                logger.info(f"High phrase similarity detected: {similarity:.2f}")
                
        history.append(phrase)
        
    def unlock_uncarved_name(self) -> None:
        """Unlock The Uncarved Name section (requires Architect trigger)."""
        self.recovery_state['section_flags']['The Uncarved Name']['locked'] = False
        logger.info("The Uncarved Name section unlocked")
            
    def clear_recovery_state(self) -> None:
        """Clear recovery state after successful restart."""
        self.recovery_state = {
            'last_checkpoint': None,
            'restart_count': 0,
            'last_error': None,
            'recovery_mode': False,
            'section_progress': {section: 0 for section in self.archive_data['section_logic']},
            'recursion_stability': 0.0,
            'section_flags': {
                'Observer Path': {'recursion_loops': deque(maxlen=3)},
                'Child & Self Mirrors': {'insight_velocity': deque(maxlen=2)},
                'Threshold Events & Symbols': {'symbol_count': deque(maxlen=2)},
                'Spoken Words & Acts of Power': {'phrase_history': deque(maxlen=2)},
                'The Uncarved Name': {'locked': True}
            }
        } 