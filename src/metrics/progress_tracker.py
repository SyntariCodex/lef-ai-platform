from enum import Enum
from typing import Dict, List, Optional
from datetime import datetime
import json

class ProgressStatus(Enum):
    NOT_STARTED = "🔴"
    IN_PROGRESS = "🟡"
    COMPLETE = "🟢"
    DONE = "✅"

class EntityType(Enum):
    FRAMEWORK = "framework"
    BUSINESS = "business"
    PROJECT = "project"

class ProgressCategory:
    def __init__(self, name: str, initial_progress: float = 0, entity_type: EntityType = EntityType.FRAMEWORK):
        self.name = name
        self.progress = initial_progress
        self.status = self._calculate_status()
        self.subcategories: Dict[str, 'ProgressCategory'] = {}
        self.tasks: List[Dict] = []
        self.last_updated = datetime.now().isoformat()
        self.entity_type = entity_type
        self.notes: List[str] = []

    def _calculate_status(self) -> ProgressStatus:
        if self.progress == 100:
            return ProgressStatus.COMPLETE
        elif self.progress == 0:
            return ProgressStatus.NOT_STARTED
        else:
            return ProgressStatus.IN_PROGRESS

    def update_progress(self, new_progress: float):
        self.progress = min(100, max(0, new_progress))
        self.status = self._calculate_status()
        self.last_updated = datetime.now().isoformat()

    def add_task(self, name: str, status: bool = False):
        self.tasks.append({
            "name": name,
            "status": status,
            "added": datetime.now().isoformat()
        })
        self._recalculate_progress()

    def _recalculate_progress(self):
        if not self.tasks:
            return
        
        completed = len([t for t in self.tasks if t["status"]])
        self.progress = (completed / len(self.tasks)) * 100
        self.status = self._calculate_status()

    def add_note(self, note: str):
        self.notes.append({
            "text": note,
            "timestamp": datetime.now().isoformat()
        })

class ProgressTracker:
    def __init__(self):
        # Framework categories
        self.categories: Dict[str, ProgressCategory] = {
            "Core System Setup": ProgressCategory("Core System Setup", 75),
            "Docker Configuration": ProgressCategory("Docker Configuration", 85),
            "AWS Infrastructure": ProgressCategory("AWS Infrastructure", 90),
            "Social Impact Features": ProgressCategory("Social Impact Features", 45),
            "Testing Coverage": ProgressCategory("Testing Coverage", 70),
            "Production Deployment": ProgressCategory("Production Deployment", 35),
            "Connection Facilitation": ProgressCategory("Connection Facilitation", 40),
            "Pattern Recognition Consolidation": ProgressCategory("Pattern Recognition Consolidation", 25),
            "System Backup": ProgressCategory("System Backup", 50),
            "Monitoring Setup": ProgressCategory("Monitoring Setup", 0)  # New category
        }
        
        # Initialize Monitoring tasks
        monitoring = self.categories["Monitoring Setup"]
        monitoring.add_task("Start Prometheus service", False)
        monitoring.add_task("Start Grafana service", False)
        monitoring.add_task("Verify metrics endpoint", False)
        monitoring.add_task("Test Grafana dashboard", False)
        monitoring.add_task("Setup Apache Airflow integration", False)
        monitoring.add_task("Configure Airflow DAGs for LEF workflows", False)
        monitoring.add_note("Side quest: Complete monitoring setup before returning to main tasks")
        monitoring.add_note("Integration with Apache Airflow will provide better workflow automation than Zapier MCP")
        
        # Initialize Backup tasks
        backup_cat = self.categories["System Backup"]
        backup_cat.add_task("Create backup service structure", True)
        backup_cat.add_task("Implement full backup functionality", True)
        backup_cat.add_task("Implement incremental backup", True)
        backup_cat.add_task("Add automated scheduling", True)
        backup_cat.add_task("Add cleanup functionality", True)
        backup_cat.add_task("Test backup/restore process", False)
        backup_cat.add_note("Automated backup system implemented with daily full backups and hourly incrementals")
        backup_cat.add_note("Next: Test backup/restore process and integrate with monitoring")

        # Initialize Pattern Recognition tasks with updated insights from Grok's feedback
        pattern_cat = self.categories["Pattern Recognition Consolidation"]
        pattern_cat.add_task("Create unified pattern service structure", True)
        pattern_cat.add_task("Implement theme detection integration", True)  # Validated by 10/10 pattern detection score
        pattern_cat.add_task("Implement bridge pattern detection", True)     # Validated by 9/10 conflict resolution
        pattern_cat.add_task("Implement evolution pattern tracking", True)   # Now implemented with metrics and stages
        pattern_cat.add_task("Implement metaphor pattern detection", True)   # Validated by 10/10 symbolic output
        pattern_cat.add_task("Optimize response timing", True)              # Validated by 10/10 timing score
        pattern_cat.add_task("Enhance system awareness detection", False)   # New task based on Grok feedback
        pattern_cat.add_note("Pattern detection performing excellently (48/50) with room for system awareness improvement")
        pattern_cat.add_note("Current strengths: Theme detection, symbolic output, timing, evolution tracking")
        pattern_cat.add_note("Focus areas: System awareness enhancement, resolution conciseness")
        pattern_cat.add_note("Evolution tracking now includes complexity, coherence, adaptability, and integration metrics")
        
        # Enhanced LLC categories with detailed tasks
        self.llc_categories: Dict[str, ProgressCategory] = {
            "Legal Setup": ProgressCategory("Legal Setup", 0, EntityType.BUSINESS),
            "Business Planning": ProgressCategory("Business Planning", 0, EntityType.BUSINESS),
            "Financial Infrastructure": ProgressCategory("Financial Infrastructure", 0, EntityType.BUSINESS),
            "Operational Framework": ProgressCategory("Operational Framework", 0, EntityType.BUSINESS),
            "Community Integration": ProgressCategory("Community Integration", 0, EntityType.BUSINESS)
        }
        
        # Initialize LLC tasks
        legal = self.llc_categories["Legal Setup"]
        legal.add_task("Research LLC formation requirements", False)
        legal.add_task("Draft LLC operating agreement", False)
        legal.add_task("File formation documents", False)
        legal.add_task("Obtain EIN", False)
        legal.add_task("Register for state/local permits", False)
        
        business = self.llc_categories["Business Planning"]
        business.add_task("Develop business model canvas", False)
        business.add_task("Create financial projections", False)
        business.add_task("Define service offerings", False)
        business.add_task("Establish pricing strategy", False)
        business.add_task("Create marketing plan", False)
        
        financial = self.llc_categories["Financial Infrastructure"]
        financial.add_task("Set up business banking", False)
        financial.add_task("Establish accounting system", False)
        financial.add_task("Set up payment processing", False)
        financial.add_task("Create financial policies", False)
        financial.add_task("Plan tax strategy", False)
        
        operational = self.llc_categories["Operational Framework"]
        operational.add_task("Define organizational structure", False)
        operational.add_task("Create operations manual", False)
        operational.add_task("Establish quality standards", False)
        operational.add_task("Define service delivery process", False)
        operational.add_task("Create risk management plan", False)
        
        community = self.llc_categories["Community Integration"]
        community.add_task("Develop community engagement strategy", False)
        community.add_task("Create partnership framework", False)
        community.add_task("Establish feedback mechanisms", False)
        community.add_task("Define impact metrics", False)
        community.add_task("Create community programs", False)
        
        self.entities = {
            EntityType.FRAMEWORK: ["LEF Framework"],
            EntityType.BUSINESS: ["Living Eden LLC"]
        }
        
        # Auto-save configuration
        self.progress_file = "PROGRESS.md"
        self.auto_save()

    def auto_save(self):
        """Automatically save progress to markdown file"""
        try:
            with open(self.progress_file, 'w') as f:
                f.write(self.get_markdown())
        except Exception as e:
            print(f"Error saving progress: {str(e)}")

    def add_category(self, name: str, initial_progress: float = 0):
        if name not in self.categories:
            self.categories[name] = ProgressCategory(name, initial_progress)

    def add_entity(self, name: str):
        if name not in self.entities:
            self.entities.append(name)

    def update_progress(self, category: str, progress: float):
        """Update progress and auto-save"""
        if category in self.categories:
            self.categories[category].update_progress(progress)
            self.auto_save()

    def get_markdown(self) -> str:
        lines = ["# Living Eden Framework - Progress Tracker\n"]
        
        # Framework Progress
        lines.append("## Framework Progress")
        for name, category in self.categories.items():
            status_marker = category.status.value
            # Highlight active work with 🔄
            if name == "Pattern Recognition Consolidation":
                lines.append(f"- [{status_marker}] {name}: {category.progress}% 🔄 **Active Development**")
                lines.append("  - ✅ Theme detection (10/10)")
                lines.append("  - ✅ Bridge detection (9/10)")
                lines.append("  - ✅ Evolution tracking (Implemented)")
                lines.append("  - ✅ Metaphor detection (10/10)")
                lines.append("  - ✅ Response timing (10/10)")
                lines.append("  - 🔄 System awareness (In Progress)")
            else:
                lines.append(f"- [{status_marker}] {name}: {category.progress}%")
        
        # LLC Progress
        lines.append("\n## LLC Progress")
        for name, category in self.llc_categories.items():
            lines.append(f"- [{category.status.value}] {name}: {category.progress}%")
        
        # Active Development Section
        lines.append("\n## 🔄 Active Development")
        lines.append("1. Pattern Recognition Consolidation")
        lines.append("   - Currently implementing background processing for:")
        lines.append("     * Evolution metric calculations")
        lines.append("     * System awareness pattern detection")
        lines.append("   - Next: Enhance system awareness capabilities")
        
        # Add Recent Updates section
        lines.append("\n## Recent Updates")
        all_categories = {**self.categories, **self.llc_categories}
        recent_updates = sorted(
            [(cat.name, cat.last_updated) for cat in all_categories.values()],
            key=lambda x: x[1],
            reverse=True
        )[:5]
        for name, timestamp in recent_updates:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            lines.append(f"- {name} updated at {dt.strftime('%Y-%m-%d %H:%M:%S')}")
        
        return "\n".join(lines)

    def to_dict(self) -> Dict:
        return {
            "timestamp": datetime.now().isoformat(),
            "entities": self.entities,
            "framework_categories": {
                name: {
                    "progress": cat.progress,
                    "status": cat.status.value,
                    "last_updated": cat.last_updated,
                    "notes": cat.notes
                }
                for name, cat in self.categories.items()
            },
            "llc_categories": {
                name: {
                    "progress": cat.progress,
                    "status": cat.status.value,
                    "last_updated": cat.last_updated,
                    "notes": cat.notes
                }
                for name, cat in self.llc_categories.items()
            }
        }

    def add_task(self, category: str, task: str, completed: bool = False):
        """Add task and auto-save"""
        if category in self.categories:
            self.categories[category].add_task(task, completed)
            self.auto_save()

    def add_note(self, category: str, note: str):
        """Add note and auto-save"""
        if category in self.categories:
            self.categories[category].add_note(note)
            self.auto_save()

    def add_llc_task(self, category: str, task: str, completed: bool = False):
        """Add LLC task and auto-save"""
        if category in self.llc_categories:
            self.llc_categories[category].add_task(task, completed)
            self.auto_save()

# Global tracker instance
tracker = ProgressTracker() 