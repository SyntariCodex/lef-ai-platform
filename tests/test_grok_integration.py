import pytest
from datetime import datetime
from src.integrations.grok_adapter import GrokDataStream

TEST_FORUM_DATA = {
    "test_name": "LEF Emergent Governance Simulation",
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
    "context": "A community debates fringe energy ideas"
}

@pytest.fixture
def grok_stream():
    stream = GrokDataStream()
    stream.start_stream()
    return stream

def test_forum_analysis(grok_stream):
    result = grok_stream.process_grok_input(TEST_FORUM_DATA)
    
    # Verify basic structure
    assert result["source"] == "grok"
    assert "metrics" in result
    assert "governance_response" in result
    
    # Verify theme detection
    themes = result["governance_response"]["themes"]
    assert "ether" in themes
    assert len(themes) >= 2
    
    # Verify metrics calculation
    metrics = result["metrics"]
    assert 0 <= metrics["project_alignment"] <= 1
    assert 0 <= metrics["creative_potential"] <= 1
    assert 0 <= metrics["system_awareness"] <= 1
    
    # Verify governance model generation
    assert result["governance_response"]["resolution"]
    assert result["governance_response"]["governance_model"]

def test_evolution_tracking(grok_stream):
    # Process data
    result = grok_stream.process_grok_input(TEST_FORUM_DATA)
    
    # Get feedback
    feedback = grok_stream.get_grok_feedback()
    
    # Verify feedback structure
    assert "framework_state" in feedback
    assert "suggestions" in feedback
    
    # Verify evolution tracking
    assert len(feedback["framework_state"]) > 0

def test_stream_lifecycle(grok_stream):
    assert grok_stream.is_active() == True
    
    grok_stream.stop_stream()
    assert grok_stream.is_active() == False
    
    grok_stream.start_stream()
    assert grok_stream.is_active() == True 