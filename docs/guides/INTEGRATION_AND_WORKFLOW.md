# Integration and Workflow Guide

## Overview

This guide demonstrates how the Language Server Protocol (LSP), Module System, and Type System work together to create a professional language development and deployment workflow.

## Three High-Impact Features

### 1. **Language Server Protocol (LSP)**
- **Purpose**: IDE integration and real-time development support
- **Capabilities**: Code completion, hover information, diagnostics, jump-to-definition
- **Target Users**: IDE developers, language enthusiasts building tools
- **Impact**: Mainstream adoption - professional IDEs expect LSP support

### 2. **Module System**
- **Purpose**: Multi-file program organization and code reuse
- **Capabilities**: Import statements, dependency resolution, circular detection, semantic versioning
- **Target Users**: Application developers writing production code
- **Impact**: Enables real-world projects - large applications need modular structure

### 3. **Type System**
- **Purpose**: Static type safety and early error detection
- **Capabilities**: Type inference, static analysis, 4 strictness levels, integration with LSP
- **Target Users**: Professional development teams, safety-critical projects
- **Impact**: Production readiness - professional teams require type safety

---

## Complete Workflow Example

### Scenario: Building a Math Language with Modules and Types

#### Step 1: Create Your Language Configuration

```bash
# Create a math-focused language configuration
parsercraft create --preset python_like --output math_lang.yaml
```

Edit `math_lang.yaml`:
```yaml
name: MathScript
version: 1.0.0
description: A simple mathematical scripting language
author: Your Name

keywords:
  function: def
  return: return
  if: if
  else: else
  while: while
  for: for
  import: import
  from: from

builtin_functions:
  sqrt:
    arity: 1
  sin:
    arity: 1
  cos:
    arity: 1
  pow:
    arity: 2
  abs:
    arity: 1
```

#### Step 2: Organize Your Code with Modules

Create a project structure:
```
math_project/
├── main.teach
├── modules/
│   ├── math_utils.teach
│   └── matrix_ops.teach
└── module.yaml
```

**modules/math_utils.teach**:
```teach
# Type annotations for better IDE support
export function square(x: float) -> float
    return x * x
end

export function cube(x: float) -> float
    return x * x * x
end

export const PI: float = 3.14159
export const E: float = 2.71828
```

**modules/matrix_ops.teach**:
```teach
import {square, PI} from math_utils
import math from stdlib

export function matrix_multiply(a: matrix, b: matrix) -> matrix
    # Implementation using squared values
    result = create_matrix(rows(a), cols(b))
    for i in range(rows(a))
        for j in range(cols(b))
            sum: float = 0
            for k in range(cols(a))
                sum = sum + a[i][k] * b[k][j]
            end
            result[i][j] = sum
        end
    end
    return result
end
```

**main.teach**:
```teach
import {square, cube} from modules/math_utils
import {matrix_multiply} from modules/matrix_ops
import math from stdlib

# Use imported functions with type safety
x: float = 5.0
y: float = square(x)
z: float = cube(x)

result: matrix = matrix_multiply(matrix_A, matrix_B)

print(result)
```

#### Step 3: Verify Module Structure

```bash
# Check module information
parsercraft module-info math_utils --module-dir modules/

# View dependencies
parsercraft module-deps main

# Detect circular imports (prevents infinite loops)
parsercraft module-cycles
```

Output:
```
Module: math_utils
Version: 1.0.0
Description: Mathematical utility functions

Exports (3):
  square (public)
  cube (public)
  PI (public)

Imports (0):
```

#### Step 4: Perform Static Type Analysis

```bash
# Check types with moderate strictness (default)
parsercraft type-check --config math_lang.yaml --input main.teach

# Use strict analysis for production code
parsercraft type-check --config math_lang.yaml --input main.teach --level strict
```

Output:
```
Type checking: main.teach
Analysis level: moderate
======================================================================
✓ No type errors found
```

If there were errors:
```
Type checking: main.teach
Analysis level: strict
======================================================================
Found 2 error(s):

[TypeError] Incompatible types: expected int, got str
  Location: main.teach:5:12
  Suggestion: Ensure variable x is initialized with an integer

[TypeError] Function argument type mismatch: sqrt expects float, got int
  Location: main.teach:8:15
  Suggestion: Cast to float using float(x)
```

#### Step 5: Generate IDE Support (VS Code)

```bash
# Generate a VS Code extension
parsercraft extension --config math_lang.yaml --output vscode-mathscript

# Navigate to extension directory
cd vscode-mathscript

# Install dependencies
npm install

# Build the extension
npm run compile

# Install into VS Code
code --install-extension .
```

#### Step 6: Start LSP Server for IDE Integration

```bash
# Start Language Server Protocol server
parsercraft lsp --config math_lang.yaml --port 8080

# In VS Code settings, configure the LSP client:
# "mathscript.lspServer": "http://localhost:8080"
```

Once running, in VS Code you'll get:
- **Code Completion**: Type `square(` and get parameter hints
- **Hover Documentation**: Hover over `square` to see its signature
- **Error Diagnostics**: Type errors appear as red squiggles
- **Go to Definition**: Jump to module definitions with Ctrl+Click
- **Document Symbols**: Navigate with Ctrl+Shift+O

---

## Workflow Integration Points

### LSP ↔ Type System Integration

```python
# When LSP server runs type-check on document changes:
from lsp_server import LanguageServerAnalyzer
from type_system import TypeChecker

analyzer = LanguageServerAnalyzer(config)
checker = TypeChecker(config, analysis_level=AnalysisLevel.Moderate)

# Get diagnostics for LSP client (IDE)
diagnostics = checker.check_file(document_path, document_text)

# Convert to LSP format
lsp_diagnostics = [
    Diagnostic(
        range=Range(
            start=Position(error.location.line, error.location.column),
            end=Position(error.location.line, error.location.column + len(error_token))
        ),
        message=error.message,
        severity=DiagnosticSeverity.Error
    )
    for error in diagnostics
]
```

### Type System ↔ Module System Integration

```python
# When checking types in a file with imports:
from module_system import ModuleManager
from type_system import TypeChecker, TypeEnvironment

manager = ModuleManager(base_dir=".")
checker = TypeChecker(config)

# Load all imported modules
dependencies = manager.resolve_dependencies("main")

# Create unified type environment with exports from all modules
env = TypeEnvironment()
for module_name in dependencies:
    module = manager.load_module(module_name)
    for export in module.exports:
        # Add exported names to environment
        env.define(export.name, inferred_type)

# Now type-check with full knowledge of imported names
errors = checker.check_file("main.teach", text, environment=env)
```

### Module System ↔ LSP Integration

```python
# When providing completions in VS Code:
from lsp_server import LanguageServerAnalyzer
from module_system import ModuleManager

manager = ModuleManager(base_dir=".")

# Parse import statements to find what's available
imports = manager.load_module("current_file")

# Generate completion items from:
# 1. Built-in keywords
# 2. Imported symbols from modules
# 3. Local variables
# 4. Available functions

completions = []
for module in imports:
    for export in module.exports:
        completions.append(CompletionItem(
            label=export.name,
            detail=f"From module {module.name}",
            kind=CompletionItemKind.Function
        ))
```

---

## Development Workflow

### Daily Development Cycle

```
1. Edit Code
   ├── Editor provides real-time feedback via LSP
   ├── Type checking on save
   └── Errors shown in editor

2. Organize with Modules
   ├── Create new modules as code grows
   ├── Export public API
   └── Import dependencies

3. Validate
   ├── Run module-deps to verify structure
   ├── Run module-cycles to check for circular imports
   └── Run type-check with strict level for final verification

4. Deploy
   ├── Generate VS Code extension for distribution
   ├── Start LSP server for team collaboration
   └── Share module via package registry (future)
```

### Best Practices

#### Module Organization
```
project/
├── lib/
│   ├── core/        # Core functionality
│   ├── utils/       # Utility functions
│   └── io/          # Input/output operations
├── examples/        # Example programs
├── tests/           # Test files
└── main.teach       # Entry point
```

#### Type Annotations
```teach
# Good: Clear type signatures
export function calculate(a: int, b: int) -> int
    return a + b
end

# Also good: Type inference still works
export const DEFAULT_VALUE = 42  # Inferred as int

# Avoid: Unclear types
function process(data)  # Type of 'data' unclear
    return data * 2     # Type of return value unclear
end
```

#### Module Dependencies
```teach
# Good: Acyclic dependencies
# math_utils.teach has no imports
# matrix_ops.teach imports from math_utils
# main.teach imports from both

# Avoid: Circular dependencies
# auth.teach imports from user
# user.teach imports from auth  ❌ Creates cycle!
```

---

## CLI Quick Reference

### Type System Commands
```bash
# Check types with default analysis level
parsercraft type-check --config lang.yaml --input file.teach

# Use strict analysis
parsercraft type-check --config lang.yaml --input file.teach --level strict

# Treat warnings as errors (for CI/CD)
parsercraft type-check --input file.teach --warnings-as-errors
```

### Module Commands
```bash
# Show module details
parsercraft module-info math_utils

# Show module dependencies
parsercraft module-deps main

# Detect circular dependencies
parsercraft module-cycles

# All with custom module directory
parsercraft module-info math_utils --module-dir src/modules/
```

### LSP and IDE Commands
```bash
# Start Language Server Protocol
parsercraft lsp --config lang.yaml --port 8080

# Generate VS Code extension
parsercraft extension --config lang.yaml --output ext-name

# Show language info for editor support
parsercraft info lang.yaml
```

---

## Advanced Integration Scenarios

### CI/CD Pipeline

```bash
#!/bin/bash
# ci-pipeline.sh - Complete language validation

CONFIG=math_lang.yaml

# 1. Validate configuration
parsercraft validate $CONFIG || exit 1

# 2. Check for circular dependencies
parsercraft module-cycles || exit 1

# 3. Strict type checking (all files)
for file in src/**/*.teach; do
    parsercraft type-check --config $CONFIG --input $file --level strict || exit 1
done

# 4. Run tests
parsercraft test --config $CONFIG --tests tests/test_suite.yaml || exit 1

echo "✓ All validations passed"
```

### Team IDE Setup

```bash
#!/bin/bash
# setup-team-ide.sh - Prepare IDE for team development

CONFIG=math_lang.yaml
OUTPUT_EXT=vscode-mathscript

# 1. Generate extension
parsercraft extension --config $CONFIG --output $OUTPUT_EXT

# 2. Build extension
cd $OUTPUT_EXT
npm install
npm run compile
cd ..

# 3. Start LSP server for team
parsercraft lsp --config $CONFIG --stdio > lsp.log 2>&1 &

# 4. Show setup instructions
echo "IDE Setup Complete:"
echo "1. Install extension: code --install-extension $OUTPUT_EXT"
echo "2. LSP server running on stdio"
echo "3. Open any .teach file for full IDE support"
```

### Documentation Generation

```bash
# Export configuration to markdown
parsercraft export math_lang.yaml --format markdown --output LANGUAGE_SPEC.md

# Then combine with module docs:
echo "# MathScript Language Guide" > FULL_GUIDE.md
echo "" >> FULL_GUIDE.md
echo "## Language Specification" >> FULL_GUIDE.md
cat LANGUAGE_SPEC.md >> FULL_GUIDE.md
echo "" >> FULL_GUIDE.md
echo "## Module API" >> FULL_GUIDE.md
echo "### math_utils" >> FULL_GUIDE.md
parsercraft module-info math_utils >> FULL_GUIDE.md
echo "" >> FULL_GUIDE.md
echo "### matrix_ops" >> FULL_GUIDE.md
parsercraft module-info matrix_ops >> FULL_GUIDE.md
```

---

## Performance Considerations

### Type Checking Performance
- **Lenient**: < 10ms (educational use)
- **Moderate**: 10-50ms (recommended default)
- **Strict**: 50-200ms (thorough analysis)
- **VeryStrict**: 200ms+ (maximum safety)

### Module Loading
- First load: Parses all files and builds dependency graph
- Subsequent loads: Cached (use `ModuleManager.clear_cache()` to reset)
- Circular detection: O(V+E) where V=modules, E=dependencies

### LSP Performance
- Completions: < 100ms (serves hundreds per file)
- Diagnostics: < 500ms (full file analysis on change)
- Hover information: < 50ms (symbol lookup)

---

## Troubleshooting

### "Module not found"
```bash
# Check module path:
parsercraft module-info mymodule --module-dir src/

# Verify import statement:
# import {func} from modules/mymodule  ← path from current file
```

### "Type mismatch" errors
```bash
# Check with less strict analysis first:
parsercraft type-check --level lenient --input file.teach

# Gradually increase strictness:
parsercraft type-check --level moderate --input file.teach
parsercraft type-check --level strict --input file.teach
```

### LSP Server not responding
```bash
# Start with verbose output:
parsercraft lsp --config lang.yaml --debug

# Check port is available:
netstat -an | grep 8080

# Use stdio mode for debugging:
parsercraft lsp --config lang.yaml --stdio
```

### Circular dependency detected
```bash
# Show the cycle:
parsercraft module-cycles --debug

# Fix by removing one import link or reorganizing:
# Option 1: Move common code to separate module
# Option 2: Use late binding / dependency injection
# Option 3: Combine modules if logically related
```

---

## Next Steps

1. **Create a language** using the workflow above
2. **Share modules** via package registry (planned)
3. **Integrate with build systems** (Makefile, CMake, etc.)
4. **Connect to cloud IDEs** (VS Code Web, Gitpod, etc.)
5. **Enable collaborative development** with multi-user LSP server

---

## Related Documentation

- [LSP Integration Guide](LSP_INTEGRATION_GUIDE.md)
- [Module System Guide](MODULE_SYSTEM_GUIDE.md)
- [Type System Guide](TYPE_SYSTEM_GUIDE.md)
- [CLI Reference](../reference/CLI_REFERENCE.md)
- [API Reference](../reference/API_REFERENCE.md)
