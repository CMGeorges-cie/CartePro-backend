import pytest

# Skip integration tests that require a running server
pytest.skip("Integration tests require a running server", allow_module_level=True)


