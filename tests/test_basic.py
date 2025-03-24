"""Basic tests to ensure CI pipeline functionality."""
import pytest

def test_basic_setup():
    """Ensure basic test setup is working."""
    assert True

@pytest.mark.asyncio
async def test_async_setup():
    """Ensure async test setup is working."""
    assert True

def test_python_environment():
    """Test Python environment and key dependencies."""
    import sys
    import numpy
    import pandas
    try:
        import tensorflow.keras  # More specific import to verify TensorFlow setup
        print(f"TensorFlow version: {tensorflow.version.VERSION}")
    except ImportError as e:
        pytest.fail(f"TensorFlow import failed: {e}")
    
    assert sys.version_info >= (3, 9)
    assert numpy.__version__, "NumPy version should be available"
    assert pandas.__version__, "Pandas version should be available" 