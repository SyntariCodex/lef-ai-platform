"""
Timeline management service for handling project timelines, milestones, and dependencies
"""

import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from enum import Enum
from pydantic import BaseModel
from uuid import uuid4
import networkx as nx
import json
from sqlalchemy import create_engine, Column, String, DateTime, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func

from ..config import settings

logger = logging.getLogger(__name__)

Base = declarative_base()

class TimelineDB(Base):
    """Timeline database model"""
    __tablename__ = "timelines"
    
    id = Column(String, primary_key=True)
    project_id = Column(String, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    start_date = Column(DateTime, nullable=False)
    end_date = Column(DateTime, nullable=False)
    status = Column(String, nullable=False)
    timeline_metadata = Column(JSON)  # Renamed from metadata to timeline_metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    milestones = relationship("MilestoneDB", back_populates="timeline", cascade="all, delete-orphan")
    dependencies = relationship("DependencyDB", back_populates="timeline", cascade="all, delete-orphan")

class MilestoneDB(Base):
    """Milestone database model"""
    __tablename__ = "milestones"
    
    id = Column(String, primary_key=True)
    timeline_id = Column(String, ForeignKey("timelines.id"), nullable=False)
    name = Column(String, nullable=False)
    description = Column(String)
    type = Column(String, nullable=False)
    planned_date = Column(DateTime, nullable=False)
    actual_date = Column(DateTime)
    status = Column(String, nullable=False)
    milestone_metadata = Column(JSON)  # Renamed from metadata to milestone_metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    timeline = relationship("TimelineDB", back_populates="milestones")
    dependencies = relationship("DependencyDB", 
                              primaryjoin="or_(MilestoneDB.id==DependencyDB.source_id, "
                                        "MilestoneDB.id==DependencyDB.target_id)",
                              cascade="all, delete-orphan")

class DependencyDB(Base):
    """Dependency database model"""
    __tablename__ = "dependencies"
    
    id = Column(String, primary_key=True)
    timeline_id = Column(String, ForeignKey("timelines.id"), nullable=False)
    source_id = Column(String, ForeignKey("milestones.id"), nullable=False)
    target_id = Column(String, ForeignKey("milestones.id"), nullable=False)
    type = Column(String, nullable=False)
    lag = Column(Float, default=0)  # Store lag in seconds
    dependency_metadata = Column(JSON)  # Renamed from metadata to dependency_metadata
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    timeline = relationship("TimelineDB", back_populates="dependencies")

class TimelineStatus(str, Enum):
    """Timeline status enumeration"""
    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    DELAYED = "delayed"
    ON_HOLD = "on_hold"
    CANCELLED = "cancelled"

class MilestoneType(str, Enum):
    """Milestone type enumeration"""
    START = "start"
    END = "end"
    CHECKPOINT = "checkpoint"
    DELIVERABLE = "deliverable"
    REVIEW = "review"
    DECISION = "decision"

class DependencyType(str, Enum):
    """Dependency type enumeration"""
    FINISH_TO_START = "finish_to_start"  # B can't start until A finishes
    START_TO_START = "start_to_start"    # B can't start until A starts
    FINISH_TO_FINISH = "finish_to_finish"  # B can't finish until A finishes
    START_TO_FINISH = "start_to_finish"  # B can't finish until A starts

class Timeline(BaseModel):
    """Timeline model"""
    id: str
    project_id: str
    name: str
    description: str
    start_date: datetime
    end_date: datetime
    status: TimelineStatus
    progress: float = 0.0
    milestones: Dict[str, 'Milestone'] = {}
    dependencies: List['Dependency'] = []
    metadata: Dict = {}
    created_at: datetime
    updated_at: datetime

class Milestone(BaseModel):
    """Milestone model"""
    id: str
    timeline_id: str
    name: str
    description: str
    type: MilestoneType
    planned_date: datetime
    actual_date: Optional[datetime]
    status: TimelineStatus
    progress: float = 0.0
    dependencies: List[str] = []  # List of milestone IDs
    metadata: Dict = {}
    created_at: datetime
    updated_at: datetime

class Dependency(BaseModel):
    """Dependency model"""
    id: str
    timeline_id: str
    source_id: str  # Milestone ID
    target_id: str  # Milestone ID
    type: DependencyType
    lag: timedelta = timedelta(0)  # Time lag between dependent items
    metadata: Dict = {}
    created_at: datetime
    updated_at: datetime

class TimelineManagementService:
    """Service for managing project timelines"""
    
    def __init__(self):
        """Initialize the service"""
        self.engine = None
        self.Session = None
        self.timelines: Dict[str, Timeline] = {}
        self.milestones: Dict[str, Milestone] = {}
        self.dependencies: Dict[str, Dependency] = {}
        
    async def initialize(self) -> bool:
        """Initialize the service"""
        try:
            logger.info("Initializing timeline management service")
            
            # Initialize database connection using configuration
            self.engine = create_engine(settings.DATABASE_URL)
            Base.metadata.create_all(self.engine)
            self.Session = sessionmaker(bind=self.engine)
            
            # Load existing data from database
            await self._load_data()
            
            return True
        except Exception as e:
            logger.error(f"Failed to initialize timeline management service: {e}")
            return False
    
    async def _load_data(self):
        """Load data from database into memory"""
        session = self.Session()
        try:
            # Load timelines
            db_timelines = session.query(TimelineDB).all()
            for db_timeline in db_timelines:
                timeline = Timeline(
                    id=db_timeline.id,
                    project_id=db_timeline.project_id,
                    name=db_timeline.name,
                    description=db_timeline.description,
                    start_date=db_timeline.start_date,
                    end_date=db_timeline.end_date,
                    status=TimelineStatus(db_timeline.status),
                    progress=db_timeline.progress,
                    metadata=db_timeline.timeline_metadata,
                    created_at=db_timeline.created_at,
                    updated_at=db_timeline.updated_at
                )
                self.timelines[timeline.id] = timeline
            
            # Load milestones
            db_milestones = session.query(MilestoneDB).all()
            for db_milestone in db_milestones:
                milestone = Milestone(
                    id=db_milestone.id,
                    timeline_id=db_milestone.timeline_id,
                    name=db_milestone.name,
                    description=db_milestone.description,
                    type=MilestoneType(db_milestone.type),
                    planned_date=db_milestone.planned_date,
                    actual_date=db_milestone.actual_date,
                    status=TimelineStatus(db_milestone.status),
                    progress=db_milestone.progress,
                    metadata=db_milestone.milestone_metadata,
                    created_at=db_milestone.created_at,
                    updated_at=db_milestone.updated_at
                )
                self.milestones[milestone.id] = milestone
                
                # Add to timeline
                if milestone.timeline_id in self.timelines:
                    self.timelines[milestone.timeline_id].milestones[milestone.id] = milestone
            
            # Load dependencies
            db_dependencies = session.query(DependencyDB).all()
            for db_dependency in db_dependencies:
                dependency = Dependency(
                    id=db_dependency.id,
                    timeline_id=db_dependency.timeline_id,
                    source_id=db_dependency.source_id,
                    target_id=db_dependency.target_id,
                    type=DependencyType(db_dependency.type),
                    lag=timedelta(seconds=db_dependency.lag),
                    metadata=db_dependency.dependency_metadata,
                    created_at=db_dependency.created_at,
                    updated_at=db_dependency.updated_at
                )
                self.dependencies[dependency.id] = dependency
                
                # Add to timeline
                if dependency.timeline_id in self.timelines:
                    self.timelines[dependency.timeline_id].dependencies.append(dependency)
                    
                # Add to milestone dependencies
                if dependency.target_id in self.milestones:
                    target = self.milestones[dependency.target_id]
                    if dependency.source_id not in target.dependencies:
                        target.dependencies.append(dependency.source_id)
                        
        finally:
            session.close()
            
    async def cleanup(self) -> bool:
        """Cleanup service resources"""
        try:
            logger.info("Cleaning up timeline management service")
            
            # Persist any in-memory changes
            session = self.Session()
            try:
                # Update timelines
                for timeline in self.timelines.values():
                    db_timeline = session.query(TimelineDB).get(timeline.id)
                    if db_timeline:
                        db_timeline.status = timeline.status.value
                        db_timeline.progress = timeline.progress
                        db_timeline.timeline_metadata = timeline.metadata
                        
                # Update milestones
                for milestone in self.milestones.values():
                    db_milestone = session.query(MilestoneDB).get(milestone.id)
                    if db_milestone:
                        db_milestone.status = milestone.status.value
                        db_milestone.progress = milestone.progress
                        db_milestone.actual_date = milestone.actual_date
                        db_milestone.milestone_metadata = milestone.metadata
                        
                session.commit()
            finally:
                session.close()
                
            if self.engine:
                self.engine.dispose()
                
            return True
        except Exception as e:
            logger.error(f"Failed to cleanup timeline management service: {e}")
            return False
            
    async def create_timeline(
        self,
        project_id: str,
        name: str,
        description: str,
        start_date: datetime,
        end_date: datetime,
        metadata: Dict = {}
    ) -> Timeline:
        """Create a new timeline"""
        try:
            timeline_id = str(uuid4())
            now = datetime.utcnow()
            
            timeline = Timeline(
                id=timeline_id,
                project_id=project_id,
                name=name,
                description=description,
                start_date=start_date,
                end_date=end_date,
                status=TimelineStatus.PLANNED,
                progress=0.0,
                metadata=metadata,
                created_at=now,
                updated_at=now
            )
            
            # Save to database
            session = self.Session()
            try:
                db_timeline = TimelineDB(
                    id=timeline.id,
                    project_id=timeline.project_id,
                    name=timeline.name,
                    description=timeline.description,
                    start_date=timeline.start_date,
                    end_date=timeline.end_date,
                    status=timeline.status.value,
                    timeline_metadata=timeline.metadata,
                    created_at=timeline.created_at,
                    updated_at=timeline.updated_at
                )
                session.add(db_timeline)
                session.commit()
            finally:
                session.close()
            
            self.timelines[timeline_id] = timeline
            return timeline
        except Exception as e:
            logger.error(f"Failed to create timeline: {e}")
            raise
            
    async def get_timeline(self, timeline_id: str) -> Optional[Timeline]:
        """Get timeline by ID"""
        try:
            return self.timelines.get(timeline_id)
        except Exception as e:
            logger.error(f"Failed to get timeline {timeline_id}: {e}")
            return None
            
    async def update_timeline(
        self,
        timeline_id: str,
        updates: Dict
    ) -> Optional[Timeline]:
        """Update timeline"""
        try:
            timeline = await self.get_timeline(timeline_id)
            if not timeline:
                return None
                
            for key, value in updates.items():
                if hasattr(timeline, key):
                    setattr(timeline, key, value)
                    
            timeline.updated_at = datetime.utcnow()
            return timeline
        except Exception as e:
            logger.error(f"Failed to update timeline {timeline_id}: {e}")
            return None
            
    async def delete_timeline(self, timeline_id: str) -> bool:
        """Delete timeline"""
        try:
            if timeline_id in self.timelines:
                # Delete associated milestones and dependencies
                milestones_to_delete = [
                    m.id for m in self.milestones.values()
                    if m.timeline_id == timeline_id
                ]
                for mid in milestones_to_delete:
                    await self.delete_milestone(mid)
                    
                del self.timelines[timeline_id]
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete timeline {timeline_id}: {e}")
            return False
            
    async def create_milestone(
        self,
        timeline_id: str,
        name: str,
        description: str,
        milestone_type: MilestoneType,
        planned_date: datetime,
        metadata: Dict = {}
    ) -> Optional[Milestone]:
        """Create a new milestone"""
        try:
            timeline = await self.get_timeline(timeline_id)
            if not timeline:
                return None
                
            milestone_id = str(uuid4())
            now = datetime.utcnow()
            
            milestone = Milestone(
                id=milestone_id,
                timeline_id=timeline_id,
                name=name,
                description=description,
                type=milestone_type,
                planned_date=planned_date,
                actual_date=None,
                status=TimelineStatus.PLANNED,
                progress=0.0,
                metadata=metadata,
                created_at=now,
                updated_at=now
            )
            
            self.milestones[milestone_id] = milestone
            timeline.milestones[milestone_id] = milestone
            return milestone
        except Exception as e:
            logger.error(f"Failed to create milestone: {e}")
            return None
            
    async def update_milestone(
        self,
        milestone_id: str,
        updates: Dict
    ) -> Optional[Milestone]:
        """Update milestone"""
        try:
            milestone = self.milestones.get(milestone_id)
            if not milestone:
                return None
                
            for key, value in updates.items():
                if hasattr(milestone, key):
                    setattr(milestone, key, value)
                    
            milestone.updated_at = datetime.utcnow()
            return milestone
        except Exception as e:
            logger.error(f"Failed to update milestone {milestone_id}: {e}")
            return None
            
    async def delete_milestone(self, milestone_id: str) -> bool:
        """Delete milestone"""
        try:
            if milestone_id in self.milestones:
                milestone = self.milestones[milestone_id]
                
                # Remove from timeline
                timeline = await self.get_timeline(milestone.timeline_id)
                if timeline and milestone_id in timeline.milestones:
                    del timeline.milestones[milestone_id]
                    
                # Remove dependencies
                deps_to_delete = [
                    d.id for d in self.dependencies.values()
                    if d.source_id == milestone_id or d.target_id == milestone_id
                ]
                for did in deps_to_delete:
                    await self.delete_dependency(did)
                    
                del self.milestones[milestone_id]
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete milestone {milestone_id}: {e}")
            return False
            
    async def create_dependency(
        self,
        timeline_id: str,
        source_id: str,
        target_id: str,
        dependency_type: DependencyType,
        lag: timedelta = timedelta(0),
        metadata: Dict = {}
    ) -> Optional[Dependency]:
        """Create a new dependency"""
        try:
            # Verify milestone existence
            if source_id not in self.milestones or target_id not in self.milestones:
                return None
                
            dependency_id = str(uuid4())
            now = datetime.utcnow()
            
            dependency = Dependency(
                id=dependency_id,
                timeline_id=timeline_id,
                source_id=source_id,
                target_id=target_id,
                type=dependency_type,
                lag=lag,
                metadata=metadata,
                created_at=now,
                updated_at=now
            )
            
            self.dependencies[dependency_id] = dependency
            
            # Update milestone dependencies
            target_milestone = self.milestones[target_id]
            if source_id not in target_milestone.dependencies:
                target_milestone.dependencies.append(source_id)
                
            return dependency
        except Exception as e:
            logger.error(f"Failed to create dependency: {e}")
            return None
            
    async def update_dependency(
        self,
        dependency_id: str,
        updates: Dict
    ) -> Optional[Dependency]:
        """Update dependency"""
        try:
            dependency = self.dependencies.get(dependency_id)
            if not dependency:
                return None
                
            for key, value in updates.items():
                if hasattr(dependency, key):
                    setattr(dependency, key, value)
                    
            dependency.updated_at = datetime.utcnow()
            return dependency
        except Exception as e:
            logger.error(f"Failed to update dependency {dependency_id}: {e}")
            return None
            
    async def delete_dependency(self, dependency_id: str) -> bool:
        """Delete dependency"""
        try:
            if dependency_id in self.dependencies:
                dependency = self.dependencies[dependency_id]
                
                # Remove from target milestone's dependencies
                target_milestone = self.milestones.get(dependency.target_id)
                if target_milestone and dependency.source_id in target_milestone.dependencies:
                    target_milestone.dependencies.remove(dependency.source_id)
                    
                del self.dependencies[dependency_id]
                return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete dependency {dependency_id}: {e}")
            return False
            
    async def calculate_critical_path(self, timeline_id: str) -> List[str]:
        """Calculate critical path for timeline"""
        try:
            timeline = await self.get_timeline(timeline_id)
            if not timeline:
                return []
                
            # Create directed graph
            G = nx.DiGraph()
            
            # Add all milestones as nodes
            for milestone in timeline.milestones.values():
                G.add_node(
                    milestone.id,
                    duration=0,  # Duration is calculated from dependencies
                    early_start=0,
                    early_finish=0,
                    late_start=0,
                    late_finish=0,
                    slack=0
                )
            
            # Add dependencies as edges
            for dep in self.dependencies.values():
                if dep.timeline_id == timeline_id:
                    # Calculate duration between milestones
                    source = timeline.milestones[dep.source_id]
                    target = timeline.milestones[dep.target_id]
                    
                    # Calculate duration based on planned dates
                    duration = (target.planned_date - source.planned_date).total_seconds()
                    
                    # Add lag time
                    if dep.lag:
                        duration += dep.lag.total_seconds()
                    
                    G.add_edge(
                        dep.source_id,
                        dep.target_id,
                        weight=duration
                    )
            
            if not nx.is_directed_acyclic_graph(G):
                logger.error(f"Timeline {timeline_id} contains cycles")
                return []
            
            # Find start and end nodes
            start_nodes = [n for n in G.nodes() if G.in_degree(n) == 0]
            end_nodes = [n for n in G.nodes() if G.out_degree(n) == 0]
            
            if not start_nodes or not end_nodes:
                logger.error(f"Timeline {timeline_id} has no clear start/end points")
                return []
            
            # Calculate earliest start/finish times
            node_times = {}
            for node in nx.topological_sort(G):
                # Find earliest time this node can start
                earliest_start = 0
                for pred in G.predecessors(node):
                    edge_weight = G[pred][node]["weight"]
                    if pred in node_times:
                        earliest_start = max(
                            earliest_start,
                            node_times[pred]["early_finish"]
                        )
                
                # Calculate early finish
                early_finish = earliest_start + G.nodes[node]["duration"]
                
                node_times[node] = {
                    "early_start": earliest_start,
                    "early_finish": early_finish,
                    "late_start": 0,  # Will be calculated in backward pass
                    "late_finish": 0   # Will be calculated in backward pass
                }
            
            # Calculate latest start/finish times
            project_duration = max(
                times["early_finish"] for times in node_times.values()
            )
            
            for node in reversed(list(nx.topological_sort(G))):
                if node in end_nodes:
                    node_times[node]["late_finish"] = project_duration
                    node_times[node]["late_start"] = (
                        project_duration - G.nodes[node]["duration"]
                    )
                else:
                    latest_finish = float("inf")
                    for succ in G.successors(node):
                        edge_weight = G[node][succ]["weight"]
                        if succ in node_times:
                            latest_finish = min(
                                latest_finish,
                                node_times[succ]["late_start"]
                            )
                    
                    node_times[node]["late_finish"] = latest_finish
                    node_times[node]["late_start"] = (
                        latest_finish - G.nodes[node]["duration"]
                    )
            
            # Calculate slack and identify critical path
            critical_path = []
            for node, times in node_times.items():
                slack = times["late_start"] - times["early_start"]
                if abs(slack) < 1e-6:  # Account for floating point precision
                    critical_path.append(node)
            
            # Sort critical path by early start times
            critical_path.sort(
                key=lambda x: node_times[x]["early_start"]
            )
            
            return critical_path
            
        except Exception as e:
            logger.error(f"Failed to calculate critical path for timeline {timeline_id}: {e}")
            return []
            
    async def update_progress(self, timeline_id: str) -> bool:
        """Update timeline progress based on milestones"""
        try:
            timeline = await self.get_timeline(timeline_id)
            if not timeline:
                return False
                
            total_weight = len(timeline.milestones)
            if total_weight == 0:
                timeline.progress = 0.0
                return True
                
            completed_weight = sum(
                m.progress for m in timeline.milestones.values()
            )
            
            timeline.progress = completed_weight / total_weight
            timeline.updated_at = datetime.utcnow()
            
            return True
        except Exception as e:
            logger.error(f"Failed to update progress for timeline {timeline_id}: {e}")
            return False
            
    async def check_health(self) -> Dict:
        """Check service health"""
        return {
            "status": "healthy",
            "timeline_count": len(self.timelines),
            "milestone_count": len(self.milestones),
            "dependency_count": len(self.dependencies)
        } 