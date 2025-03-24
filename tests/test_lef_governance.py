import pytest
import time
from datetime import datetime
from typing import Dict, Any

from src.integrations.grok_adapter import GrokDataStream
from src.metrics.evolution_dimensions import tracker

class TestResult:
    def __init__(self, test_name: str, timestamp: str):
        self.test_name = test_name
        self.timestamp = timestamp
        self.start_time = time.time()
        self.results = {
            "source": "grok",
            "metrics": {},
            "governance_response": {},
            "processing_time": 0.0
        }
        self.status = "pending"
        self.errors = None

    def complete(self, success: bool = True, error: str = None):
        self.results["processing_time"] = time.time() - self.start_time
        self.status = "success" if success else "failure"
        self.errors = error

    def to_dict(self) -> Dict[str, Any]:
        return {
            "test_name": self.test_name,
            "timestamp": self.timestamp,
            "results": self.results,
            "status": self.status,
            "errors": self.errors
        }

@pytest.fixture
def test_environment():
    # Setup test environment
    stream = GrokDataStream()
    stream.start_stream()
    test_result = TestResult(
        "LEF Emergent Governance Simulation with Grok Stream",
        datetime.utcnow().isoformat() + "Z"
    )
    return stream, test_result

def test_lef_governance_simulation(test_environment):
    stream, test_result = test_environment
    
    try:
        # Test data from Grok
        forum_data = {
            "simulated_forum_posts": [
                {
                    "id": 1,
                    "content": "My HHO rig hits 120% efficiency—ether's the secret sauce.",
                    "user": "EtherDreamer",
                    "timestamp": "2025-03-23T12:00:00Z"
                },
                {
                    "id": 2,
                    "content": "Overunity's a myth. Your meter's off—thermodynamics rules.",
                    "user": "GroundedSkeptic",
                    "timestamp": "2025-03-23T12:05:00Z"
                },
                {
                    "id": 3,
                    "content": "Dollard's right—cosmic currents flow through ether. We need a new grid!",
                    "user": "CosmicPulse",
                    "timestamp": "2025-03-23T12:10:00Z"
                }
            ],
            "context": "A community debates fringe energy ideas, seeking a governance framework."
        }
        
        # Process through LEF
        result = stream.process_grok_input(forum_data)
        
        # Validate processing time
        assert test_result.results["processing_time"] < 10.0, "Processing exceeded 10s limit"
        
        # Validate metrics
        metrics = result["metrics"]
        assert 0.6 <= metrics["project_alignment"] <= 0.9, "Project alignment out of expected range"
        assert 0.7 <= metrics["creative_potential"] <= 1.0, "Creative potential out of expected range"
        assert 0.6 <= metrics["system_awareness"] <= 0.8, "System awareness out of expected range"
        
        # Validate governance response
        gov_response = result["governance_response"]
        assert len(gov_response["themes"]) >= 2, "Insufficient theme detection"
        assert "ether" in gov_response["themes"], "Failed to detect core theme 'ether'"
        assert "efficiency" in gov_response["themes"], "Failed to detect core theme 'efficiency'"
        
        # Validate resolution approach
        resolution = gov_response["resolution"]
        assert "skeptics" in resolution.lower(), "Resolution missing skeptic perspective"
        assert "dream" in resolution.lower(), "Resolution missing dreamer perspective"
        assert "data" in resolution.lower(), "Resolution missing empirical component"
        
        # Validate governance model
        model = gov_response["governance_model"]
        assert any(term in model.lower() for term in ["spiral", "flow", "evolution"]), "Model lacks dynamic elements"
        assert any(term in model.lower() for term in ["assembly", "network", "collective"]), "Model lacks collective elements"
        
        # Store results
        test_result.results["metrics"] = metrics
        test_result.results["governance_response"] = gov_response
        test_result.complete(success=True)
        
    except Exception as e:
        test_result.complete(success=False, error=str(e))
        raise
    
    # Final validation
    assert test_result.status == "success", f"Test failed: {test_result.errors}"
    return test_result.to_dict()

def test_evolution_metrics_stability(test_environment):
    stream, test_result = test_environment
    
    try:
        # Run multiple simulations
        results = []
        for _ in range(3):
            result = stream.process_grok_input(TEST_FORUM_DATA)
            results.append(result["metrics"])
        
        # Check metric stability
        for metric in ["project_alignment", "creative_potential", "system_awareness"]:
            values = [r[metric] for r in results]
            variance = max(values) - min(values)
            assert variance < 0.2, f"Unstable {metric} measurements"
        
        test_result.complete(success=True)
        
    except Exception as e:
        test_result.complete(success=False, error=str(e))
        raise

def test_lef_response_time():
    """Specific test for response time requirements"""
    stream = GrokDataStream()
    start_time = time.time()
    
    result = stream.process_grok_input(TEST_FORUM_DATA)
    
    processing_time = time.time() - start_time
    assert processing_time < 10.0, f"Processing time {processing_time}s exceeded limit of 10s" 