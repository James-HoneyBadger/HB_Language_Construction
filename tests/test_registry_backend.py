import pytest
from unittest.mock import MagicMock
from src.parsercraft.registry_backend import RemotePackageRegistry, PackageMetadata, RegistryResponse

class MockRegistry(RemotePackageRegistry):
    def __init__(self, url="http://mock"):
        super().__init__(url)
        
    def _make_request_with_retry(self, url):
        if url.endswith("/versions"):
            return {"success": True, "data": ["1.0.0", "1.1.0", "2.0.0"]}
        if "/packages/lib" in url:
            version = url.split("/")[-1]
            if version == "lib": version = "1.0.0" # Default
            return {
                "success": True, 
                "data": {
                    "name": "lib", 
                    "version": version,
                    "description": "lib desc"
                }
            }
        return {"success": False, "error": "Not found"}

def test_fetch_package():
    reg = MockRegistry("http://mock")
    reg._get_cached_metadata = MagicMock(return_value=None)
    reg._cache_metadata = MagicMock()
    
    resp = reg.fetch_package_metadata("lib", "1.0.0")
    assert resp.success
    assert resp.data.name == "lib"
    assert resp.data.version == "1.0.0"

def test_resolve_version():
    reg = MockRegistry("http://mock")
    
    # Test ^1.0.0 -> Matches 1.0.0, 1.1.0. Highest is 1.1.0.
    # 2.0.0 is excluded by ^1.0.0.
    resp = reg.resolve_version("lib", "^1.0.0")
    
    assert resp.success
    assert resp.data == "1.1.0"

def test_resolve_version_exact():
    reg = MockRegistry("http://mock")
    resp = reg.resolve_version("lib", "==2.0.0")
    assert resp.success
    assert resp.data == "2.0.0"
