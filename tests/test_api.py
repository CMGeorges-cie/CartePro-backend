import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

# Skip integration tests that require a running server
pytest.skip("Integration tests require a running server", allow_module_level=True)


