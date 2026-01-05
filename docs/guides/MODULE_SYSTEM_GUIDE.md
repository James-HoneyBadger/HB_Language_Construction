# Module & Package System Guide

**Multi-file Programs, Code Reuse, and Package Management for ParserCraft Languages**

## Overview

ParserCraft now includes a full **Module and Package System** that enables:

✅ **Multi-file Programs** - Organize code across multiple files
✅ **Module Imports** - `import math`, `import graphics as gfx`
✅ **Code Reuse** - Create libraries and packages
✅ **Dependency Management** - Automatic dependency resolution
✅ **Circular Dependency Detection** - Catch invalid imports
✅ **Version Management** - Semantic versioning for modules
✅ **Package Repositories** - Share code with others

## Quick Start

### 1. Create a Module File

Create `math_utils.teach`:
```teach
#@ version: 1.0.0
#@ author: Jane Doe
#@ description: Mathematical utilities

export function square(x)
    when x > 0
        return x * x
    end
end

export function cube(x)
    return x * x * x
end

export const PI = 3.14159
```

### 2. Import and Use

Create `main.teach`:
```teach
import math_utils

say math_utils.square(5)        # 25
say math_utils.cube(3)          # 27
say math_utils.PI               # 3.14159
```

Run it:
```bash
parsercraft run main.teach
```

### 3. Organize Code Hierarchically

```
project/
├── main.teach
├── modules/
│   ├── math/
│   │   ├── arithmetic.teach
│   │   ├── geometry.teach
│   │   └── module.yaml
│   ├── graphics/
│   │   ├── colors.teach
│   │   ├── shapes.teach
│   │   └── module.yaml
│   └── utils/
│       ├── strings.teach
│       ├── arrays.teach
│       └── module.yaml
└── lib/
    └── third-party-lib/
```

## Import Syntax

### Simple Import

```teach
import math
math.square(5)
```

### Import with Alias

```teach
import math_utilities as math
math.calculate(10)
```

### Selective Import (Destructuring)

```teach
import {square, cube, PI} from math_utils
say square(5)      # Direct access
say PI             # No need for prefix
```

### Version Constraints

```teach
import graphics version "^1.0.0"    # Major version 1
import utils version "1.2.*"        # Any patch version
```

### Optional Import (Try-Import)

```teach
try-import optional_feature
when optional_feature exists
    say "Feature available"
end
```

## Module Files

### Basic Module Structure

```teach
#@ version: 1.2.0
#@ author: Your Name
#@ description: Brief description of module purpose

# Private functions (internal use only)
function helper_function(x)
    return x * 2
end

# Exported functions (public API)
export function public_function(x)
    return helper_function(x) + 1
end

# Exported constants
export const VERSION = "1.2.0"
export const MAX_SIZE = 1000
```

### Metadata Comments

```teach
#@ version: 1.0.0           # Semantic version
#@ author: Jane Doe         # Module author
#@ description: Text        # Module description
#@ license: MIT             # License type
#@ homepage: https://...    # Project URL
#@ keywords: tag1, tag2     # Search keywords
#@ deprecated: true         # Mark as deprecated
#@ experimental: true       # Mark as experimental
```

## Module Metadata (module.yaml)

Create `module.yaml` for package metadata:

```yaml
name: math-utilities
version: 1.0.0
description: Mathematical and geometric utilities
author: Jane Doe
license: MIT

entry_point: main

exports:
  arithmetic: arithmetic.teach
  geometry: geometry.teach
  constants: constants.teach

dependencies:
  base-utils: "^1.0.0"
  graphics: "2.x"

dev_dependencies:
  test-framework: "^1.0.0"

keywords:
  - math
  - utilities
  - geometry
```

## Python API Usage

### Load a Module Directly

```python
from hb_lcs.module_system import ModuleManager
from hb_lcs.language_config import LanguageConfig

# Create manager
config = LanguageConfig.load("my_language.yaml")
manager = ModuleManager(
    config=config,
    search_paths=["./modules", "./lib", "."]
)

# Load module
module = manager.load_module("math_utils")
print(f"Module: {module.name}")
print(f"Exports: {list(module.exports.keys())}")

# Get module information
info = manager.get_module_info("math_utils")
print(info)
```

### Load Module with All Dependencies

```python
# Load module and recursively load all its dependencies
modules = manager.load_with_dependencies("main")

for name, module in modules.items():
    print(f"{name}: {module.description}")
```

### Detect Circular Dependencies

```python
# Check for circular imports
cycles = manager.detect_circular_dependencies()

if cycles:
    print("Circular dependencies detected:")
    for from_mod, to_mod in cycles:
        print(f"  {from_mod} → {to_mod}")
```

### Export Dependency Graph

```python
# Visualize dependencies
manager.export_dependency_graph("dependencies.json")
```

## Module Visibility

### Public (Exported) Symbols

```teach
export function calculate(x)
    return x * 2
end
```

Public symbols are accessible from other modules:
```teach
import my_module
my_module.calculate(5)  # ✓ Works
```

### Private (Internal) Symbols

```teach
function helper(x)
    return x * 2
end
```

Private symbols are NOT accessible:
```teach
import my_module
my_module.helper(5)     # ✗ Error: private function
```

### Protected (Package-level) Symbols

```teach
protected function internal_func(x)
    return x * 2
end
```

Accessible only within the same package.

## Module Organization Patterns

### Flat Structure (Small Projects)

```
project/
├── main.teach
├── utils.teach
└── config.teach
```

Usage:
```teach
import utils
import config
```

### Nested Structure (Medium Projects)

```
project/
├── main.teach
├── modules/
│   ├── math.teach
│   ├── graphics.teach
│   └── utils.teach
└── config.teach
```

Usage:
```teach
import config
import modules.math as math
```

### Hierarchical (Large Projects)

```
project/
├── main.teach
├── core/
│   ├── module.yaml
│   ├── types.teach
│   ├── errors.teach
│   └── utils.teach
├── features/
│   ├── module.yaml
│   ├── feature_a.teach
│   └── feature_b.teach
└── lib/
    ├── external/
    │   └── vendored_lib/
```

Usage:
```teach
import core.types
import core.errors
import features.feature_a as fa
```

## Version Management

### Semantic Versioning

ParserCraft uses **Semantic Versioning**:
- `MAJOR.MINOR.PATCH` (e.g., `1.2.3`)
- `1` = Major (breaking changes)
- `2` = Minor (new features, backward compatible)
- `3` = Patch (bug fixes)

### Version Constraints in Imports

```teach
import math_lib version "1.2.3"      # Exact version
import math_lib version "^1.2.3"     # Compatible (1.x where 1 ≥ 1, 2 ≥ 2, 3 ≥ 3)
import math_lib version "~1.2.3"     # Patch updates (1.2.x)
import math_lib version "1.2.*"      # Any patch
import math_lib version ">=1.0.0 <2.0.0"  # Range
```

### Declaring Module Version

In module header:
```teach
#@ version: 2.1.0
```

Or in `module.yaml`:
```yaml
version: 2.1.0
```

## Dependency Resolution

### Transitive Dependencies

If `main` imports `module_a`, and `module_a` imports `module_b`:

```
main
  └── module_a
      └── module_b
```

The module manager automatically loads `module_b`:

```python
manager.load_with_dependencies("main")
# Returns: {main, module_a, module_b}
```

### Dependency Order

Modules are loaded in **dependency order** - dependencies before dependents:

```python
modules = manager.load_with_dependencies("main")
# Order: module_b, module_a, main
```

### Circular Dependency Detection

```python
# Automatically detects if main→a→b→a
cycles = manager.detect_circular_dependencies()

if cycles:
    raise CircularDependencyError(f"Cycles found: {cycles}")
```

## Package Management

### Creating a Shareable Package

1. Create `module.yaml`:
```yaml
name: my-cool-lib
version: 1.0.0
description: "A cool library for TeachScript"
author: Your Name
license: MIT
keywords: [cool, lib, utils]

entry_point: main
exports:
  main: main.teach
  utils: utils.teach

dependencies:
  base-lib: "^1.0.0"
```

2. Create `README.md`:
```markdown
# My Cool Library

Cool features for your language!

## Installation

```
parsercraft install my-cool-lib
```

## Usage

```teach
import my_cool_lib
```
```

3. Create `LICENSE` file

### Publishing Packages

```bash
# Package the module
parsercraft package my_cool_lib

# Publish to registry
parsercraft publish my_cool_lib --registry https://registry.parsercraft.io
```

### Installing Packages

```bash
# Install from registry
parsercraft install math_utils

# Install specific version
parsercraft install math_utils@1.2.0

# Install from local path
parsercraft install ./my_local_lib

# Install from Git
parsercraft install github.com/user/repo
```

## Best Practices

### 1. Keep Modules Focused

Each module should have a single responsibility:

```teach
# ✓ Good: Single purpose
# geometry.teach - Only geometric calculations
export function circle_area(radius)
    return PI * radius * radius
end

# ✗ Bad: Mixed concerns
# everything.teach - Geometry, math, graphics, parsing
```

### 2. Use Clear Public APIs

Clearly separate public from private:

```teach
# Private helpers
function _validate_input(x)
    # ...
end

# Public API
export function process(x)
    when _validate_input(x)
        # ...
    end
end
```

### 3. Document Exports

```teach
# Calculate factorial
# Args: n (positive integer)
# Returns: factorial value
export function factorial(n)
    when n <= 1
        return 1
    end
    return n * factorial(n - 1)
end
```

### 4. Use Semantic Versioning

When publishing updates:
- `1.0.0` → `1.0.1` for bug fixes
- `1.0.0` → `1.1.0` for new features
- `1.0.0` → `2.0.0` for breaking changes

### 5. Manage Dependencies

```yaml
# Good: Specific versions
dependencies:
  utils: "1.2.0"
  graphics: "2.x"

# Avoid: Too permissive
dependencies:
  utils: "*"
  graphics: "any"
```

## CLI Commands

```bash
# Load and inspect a module
parsercraft module-info math_utils

# Check dependencies
parsercraft module-deps main.teach

# Detect circular dependencies
parsercraft module-cycles project/

# Export dependency graph
parsercraft module-graph main.teach --output deps.json

# Create a new module template
parsercraft module-create mymodule

# Package a module for distribution
parsercraft module-package mymodule

# Publish module to registry
parsercraft module-publish mymodule --registry registry.io
```

## Common Issues & Solutions

### Issue: "Module not found: math"

**Solutions:**
1. Check file exists: `math.teach` or `math.lang`
2. Verify search paths:
   ```python
   manager.search_paths  # Check current paths
   manager.search_paths.append(Path("./new_path"))
   ```
3. Use absolute import:
   ```teach
   import /full/path/to/math
   ```

### Issue: "Circular dependency detected"

**Solutions:**
1. Refactor to remove circular imports
2. Create intermediate modules:
   ```
   Before: A → B → A
   After:  A → Common ← B
   ```

### Issue: "Version constraint not satisfied"

**Solutions:**
1. Check installed versions:
   ```bash
   parsercraft list-modules
   ```
2. Install specific version:
   ```bash
   parsercraft install graphics@2.0.0
   ```

## Advanced Features

### Lazy Loading

Load modules on demand:

```python
manager = ModuleManager(config, lazy=True)
# Only load when first accessed
module = manager.load_module("heavy_lib")
```

### Module Caching

Control caching behavior:

```python
manager = ModuleManager(config, enable_caching=True)

# Clear cache when needed
manager.loader.cache.clear()
```

### Custom Module Loaders

Extend module loading:

```python
from hb_lcs.module_system import ModuleLoader

class CustomLoader(ModuleLoader):
    def _parse_module(self, module):
        super()._parse_module(module)
        # Custom parsing logic
```

## Integration with Other Systems

### LSP Integration

Modules are accessible via LSP:

```python
from hb_lcs.lsp_server import LanguageServerAnalyzer

class ModuleAwareAnalyzer(LanguageServerAnalyzer):
    def __init__(self, config, module_manager):
        super().__init__(config)
        self.modules = module_manager
    
    def get_completions(self, content, position):
        completions = super().get_completions(content, position)
        
        # Add exported symbols from loaded modules
        for module_name, module in self.modules.loaded_modules.items():
            for export_name in module.exports:
                completions.append({
                    'label': f"{module_name}.{export_name}",
                    'kind': 3,  # Function
                })
        
        return completions
```

### Type System Integration

Modules can declare types:

```teach
export type Point = {x, y}
export type Color = {r, g, b, a}

export function distance(p1: Point, p2: Point) -> float
    # ...
end
```

## Migration Guide

### Existing Code to Modules

Before:
```
large_program.teach  # 500 lines
```

After:
```
modules/
  ├── math.teach
  ├── graphics.teach
  ├── utils.teach
  └── constants.teach

main.teach  # 50 lines, uses imports
```

```teach
# main.teach
import modules.math
import modules.graphics as gfx
import modules.utils

# Use: math.calculate(), gfx.draw(), utils.format()
```

## Resources

- **Module System API**: See `src/hb_lcs/module_system.py`
- **CLI Commands**: `parsercraft module-* --help`
- **Examples**: `examples/multi-file/`

---

**Last Updated:** January 2026
**ParserCraft Version:** 2.0.0
