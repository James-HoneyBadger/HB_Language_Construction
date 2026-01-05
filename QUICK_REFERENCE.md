# ParserCraft v2.0.0 - Quick Reference Card

## The Three High-Impact Features at a Glance

### 🔌 Language Server Protocol (LSP)
**IDE Integration for Professional Development**

```bash
# Start LSP server
parsercraft lsp --config lang.yaml --port 8080

# Generate VS Code extension (auto-ready for Marketplace)
parsercraft extension --config lang.yaml --output my-lang-ext
```

**What you get**: Syntax highlighting, completions, hover docs, error diagnostics, go-to-definition in VS Code, PyCharm, Vim, Sublime Text, Emacs, etc.

**Impact**: 5M+ developers on VS Code Marketplace can now use your language

---

### 📦 Module System
**Multi-File Projects with Organization**

```teach
# math_utils.teach
export function square(x: float) -> float
    return x * x
end

# main.teach
import {square} from modules/math_utils
result = square(5.0)
```

```bash
# Check module structure
parsercraft module-info math_utils
parsercraft module-deps main
parsercraft module-cycles  # Prevents circular imports
```

**What you get**: Multi-file organization, imports/exports, dependency resolution, circular dependency detection

**Impact**: Enable production applications instead of just scripts

---

### 🎯 Type System
**Static Type Safety with 4 Strictness Levels**

```teach
# Type annotations (optional - inference works too)
x: int = 5
function add(a: int, b: int) -> int
    return a + b
end

# Type inference (works automatically)
count = 10              # Inferred as int
message = "hello"       # Inferred as str
```

```bash
# Type check with different strictness
parsercraft type-check --config lang.yaml --input file.teach --level moderate
parsercraft type-check --config lang.yaml --input file.teach --level strict
```

**Strictness Levels**:
1. **Lenient** - Minimal checks, fastest
2. **Moderate** - Standard checks (recommended)
3. **Strict** - Comprehensive validation
4. **VeryStrict** - Maximum safety

**What you get**: Early error detection, self-documenting code, IDE support for refactoring

**Impact**: Professional teams require type safety

---

## CLI Command Quick Reference

### Type System Commands
```bash
# Basic type checking
parsercraft type-check --config lang.yaml --input file.teach

# Strict analysis (production)
parsercraft type-check --config lang.yaml --input file.teach --level strict

# Treat warnings as errors (CI/CD)
parsercraft type-check --config lang.yaml --input file.teach --warnings-as-errors
```

### Module Commands
```bash
# Show module details
parsercraft module-info module_name

# Show module dependencies
parsercraft module-deps main

# Detect circular dependencies
parsercraft module-cycles

# Specify module directory
parsercraft module-info math --module-dir src/modules/
```

### LSP and IDE Commands
```bash
# Start Language Server Protocol
parsercraft lsp --config lang.yaml --port 8080

# Generate VS Code extension
parsercraft extension --config lang.yaml --output ext-dir

# Show language info
parsercraft info lang.yaml
```

### Existing Commands (Still Work!)
```bash
# Create language
parsercraft create --preset python_like --output lang.yaml

# Validate configuration
parsercraft validate lang.yaml

# REPL for testing
parsercraft repl lang.yaml

# Run tests
parsercraft test --config lang.yaml --tests tests.yaml

# Batch process
parsercraft batch lang.yaml --script script.teach
```

---

## Python API Quick Reference

### Type System API
```python
from hb_lcs.type_system import TypeChecker, AnalysisLevel

# Create type checker
checker = TypeChecker(config, analysis_level=AnalysisLevel.Strict)

# Check file
errors = checker.check_file(
    source_path="program.teach",
    source="x: int = 5\ny: str = 10"  # Type error!
)

# Process errors
for error in errors:
    print(f"{error.kind.name}: {error.message}")
    print(f"  Location: {error.location.line}:{error.location.column}")
    print(f"  Suggestion: {error.suggestion}")
```

### Module System API
```python
from hb_lcs.module_system import ModuleManager

# Create manager
manager = ModuleManager(base_dir=".")

# Load single module
module = manager.load_module("math_utils")
print(f"Exports: {[e.name for e in module.exports]}")

# Load with dependencies
modules = manager.load_with_dependencies("main")
# Returns list in correct load order

# Check for circular dependencies
try:
    manager.load_with_dependencies("main")
except CircularDependencyError as e:
    print(f"Circular import detected: {e}")

# Get dependency graph
deps = manager.resolve_dependencies("main")
print(f"All dependencies: {deps}")
```

### LSP Server API
```python
from hb_lcs.lsp_server import create_lsp_server

# Create LSP server
server = create_lsp_server(config_path="lang.yaml")

# Get completions
items = server.completions(
    file_path="program.teach",
    line=5,
    column=10
)

# Get hover information
hover = server.hover(
    file_path="program.teach",
    line=5,
    column=10
)

# Get diagnostics
diagnostics = server.get_diagnostics("program.teach")

# Get document symbols (for outline view)
symbols = server.document_symbols("program.teach")
```

---

## Complete Workflow Example (5 minutes)

### 1. Create a Language
```bash
parsercraft create --preset python_like --output mypy.yaml
```

### 2. Test LSP Server
```bash
parsercraft lsp --config mypy.yaml --port 8080
```

### 3. Generate VS Code Extension
```bash
parsercraft extension --config mypy.yaml --output mypy-vscode
cd mypy-vscode && npm install && npm run compile
code --install-extension .
```

### 4. Create Program with Modules
```teach
# mymodule.teach
export function greet(name: str) -> str
    return "Hello, " + name
end

# main.teach
import {greet} from mymodule
message: str = greet("World")
print(message)
```

### 5. Type Check
```bash
parsercraft type-check --config mypy.yaml --input main.teach --level strict
```

**Result**: Full IDE support + modular code + type safety in 5 minutes! ✨

---

## Architecture Overview

```
┌─────────────────────────────────────┐
│      Your Custom Language Config    │ (YAML/JSON)
└────────────┬────────────────────────┘
             │
    ┌────────┴────────┬──────────┬──────────┐
    │                 │          │          │
┌───▼──┐         ┌───▼────┐ ┌──▼────┐ ┌──▼──┐
│ Type │         │ Module │ │  LSP  │ │ CLI │
│System│         │ System │ │Server │ │Cmds │
└───┬──┘         └───┬────┘ └──┬────┘ └──┬──┘
    │                │         │         │
    └────────────────┼─────────┼─────────┘
                     │         │
            ┌────────▼────┬────▼──────┐
            │             │           │
        ┌───▼──┐      ┌───▼──┐    ┌──▼──┐
        │Errors│      │IDE   │    │Test │
        │Output│      │Support   │Proof │
        └──────┘      └──────┘    └─────┘
```

---

## Performance Expectations

### Type Checking
- **Lenient**: < 10ms per file
- **Moderate**: 10-50ms per file  
- **Strict**: 50-200ms per file
- **VeryStrict**: 200ms+ per file

### Module Loading
- Single module: 1-5ms
- Full graph: O(V+E) complexity
- Cached: < 1ms repeat loads

### LSP Server
- Completions: < 100ms
- Diagnostics: < 500ms
- Hover info: < 50ms
- Handles 100+ req/sec

---

## File Structure

```
src/hb_lcs/
├── lsp_server.py          ← LSP protocol implementation
├── vscode_integration.py  ← VS Code extension generator
├── module_system.py       ← Module loading & management
├── type_system.py         ← Type checking & inference
├── cli.py                 ← CLI integration (modified)
└── (existing files)       ← Fully backward compatible

docs/guides/
├── LSP_INTEGRATION_GUIDE.md       ← LSP deep dive
├── MODULE_SYSTEM_GUIDE.md         ← Module deep dive
├── TYPE_SYSTEM_GUIDE.md           ← Type system deep dive
└── INTEGRATION_AND_WORKFLOW.md    ← Complete workflows
```

---

## Troubleshooting

### "Module not found" error
```bash
# Check exact module path
parsercraft module-info mymodule --module-dir .

# Fix: Verify import path matches file location
# If file is: modules/math_utils.teach
# Import should be: import {func} from modules/math_utils
```

### Type mismatch errors
```bash
# Try less strict analysis first
parsercraft type-check --input file.teach --level lenient

# Gradually increase strictness to find issues
parsercraft type-check --input file.teach --level moderate
parsercraft type-check --input file.teach --level strict
```

### LSP not responding
```bash
# Start with debug output
parsercraft lsp --config lang.yaml --stdio

# Check port availability
netstat -an | grep 8080

# Verify client configuration in IDE
```

### Circular dependency
```bash
# Detect which modules have cycles
parsercraft module-cycles --debug

# Fix by:
# 1. Moving common code to separate module
# 2. Using dependency injection
# 3. Reorganizing module hierarchy
```

---

## Key Statistics

| Metric | Value |
|--------|-------|
| **Total New Code** | 2,193+ lines |
| **Documentation** | 2,000+ lines |
| **External Dependencies** | 0 |
| **Breaking Changes** | 0 |
| **CLI Commands** | 20+ (4 new) |
| **IDE Support** | VS Code, PyCharm, Vim, Neovim, Sublime, Emacs |
| **Type Checking Levels** | 4 |
| **Module Features** | Import/export, versioning, circular detection |
| **LSP Features** | Completions, hover, diagnostics, symbols, signatures |

---

## Next Steps

1. **Read**: [Integration and Workflow Guide](docs/guides/INTEGRATION_AND_WORKFLOW.md)
2. **Try**: Create a language with `parsercraft create`
3. **Test**: Use `parsercraft extension` to get VS Code support
4. **Scale**: Organize code with modules using `parsercraft module-*`
5. **Validate**: Type check with `parsercraft type-check --level strict`
6. **Deploy**: Publish VS Code extension to Marketplace

---

## Documentation Map

```
START HERE
    ↓
┌────────────────────────────────────────┐
│ INTEGRATION_AND_WORKFLOW.md             │ ← Complete workflows
│                                          │
└────────────────────────────────────────┘
    ↙                              ↖
   /                                \
  /                                  \
LSP_INTEGRATION_GUIDE.md    MODULE_SYSTEM_GUIDE.md    TYPE_SYSTEM_GUIDE.md
      (IDE Support)              (Multi-file)          (Type Safety)
```

---

## Support & Resources

- **API Reference**: `docs/reference/API_REFERENCE.md`
- **CLI Reference**: `docs/reference/CLI_REFERENCE.md`
- **Technical Reference**: `docs/reference/TECHNICAL_REFERENCE.md`
- **Examples**: `configs/examples/` and `demos/`
- **Tests**: `tests/` directory

---

**ParserCraft v2.0.0 - Making Custom Languages Professional**

*Built for language creators, IDE developers, and application developers*
