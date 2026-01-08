import pytest
from src.parsercraft.package_registry import (
    Version, VersionConstraint, Package, PackageRegistry, VersionOp
)

def test_version_compare():
    v1 = Version(1, 0, 0)
    v2 = Version(2, 0, 0)
    v1_1 = Version(1, 1, 0)
    
    assert v1 < v2
    assert v2 > v1
    assert v1 < v1_1
    assert v1_1 < v2
    assert v1 == Version(1, 0, 0)

def test_version_parse():
    v = Version.parse("1.2.3")
    assert v.major == 1
    assert v.minor == 2
    assert v.patch == 3
    
    v_pre = Version.parse("1.0.0-alpha")
    assert v_pre.prerelease == "alpha"

def test_constraint_caret():
    c = VersionConstraint.parse("^1.2.3")
    assert c.satisfies(Version(1, 2, 3))
    assert c.satisfies(Version(1, 9, 9))
    assert not c.satisfies(Version(2, 0, 0))
    assert not c.satisfies(Version(1, 1, 0)) # Lower minor

def test_constraint_tilde():
    c = VersionConstraint.parse("~1.2.3")
    assert c.satisfies(Version(1, 2, 3))
    assert c.satisfies(Version(1, 2, 9))
    assert not c.satisfies(Version(1, 3, 0))

def test_registry_resolve():
    reg = PackageRegistry()
    pkg1 = Package("lib", Version(1, 0, 0))
    pkg2 = Package("lib", Version(1, 1, 0))
    pkg3 = Package("lib", Version(2, 0, 0))
    
    reg.register_package(pkg1)
    reg.register_package(pkg2)
    reg.register_package(pkg3)
    
    # Resolve ^1.0.0 -> should match 1.1.0 
    res = reg.resolve("lib", "^1.0.0")
    assert res is not None
    assert res.version == Version(1, 1, 0)
    
    # Resolve ^2.0.0 -> 2.0.0
    res2 = reg.resolve("lib", "^2.0.0")
    assert res2 is not None
    assert res2.version == Version(2, 0, 0)

def test_dependency_resolution():
    reg = PackageRegistry()
    # App -> LibA -> LibB
    libb = Package("libb", Version(1, 0, 0))
    liba = Package("liba", Version(1, 0, 0), dependencies={"libb": "^1.0.0"})
    app = Package("app", Version(1, 0, 0), dependencies={"liba": "^1.0.0"})
    
    reg.register_package(libb)
    reg.register_package(liba)
    reg.register_package(app)
    
    deps = reg.resolve_dependencies(app)
    assert "liba" in deps
    assert "libb" in deps
    assert deps["liba"].version == Version(1, 0, 0)
    assert deps["libb"].version == Version(1, 0, 0)
