# Phase 5: Deep Integration Guide

## Overview

Phase 5 focuses on **deep integration** of Phase 4 frameworks with existing systems. This document provides architecture and integration patterns.

## Completed in Phase 5 So Far

### 1. ✅ AST Integration for Code Generators

**File**: `src/hb_lcs/ast_integration.py` (500+ lines)

Provides bridges between Phase 4 code generators and the existing AST system:

#### Components

- **ASTNode**: Generic AST node representation
- **ASTVisitor**: Base class for AST traversal patterns
- **SymbolTable**: Symbol tracking across scopes
- **ASTToCGenerator**: Converts AST to C code
- **ASTToWasmGenerator**: Converts AST to WASM bytecode
- **TypeInferencePass**: Type inference from AST
- **ControlFlowAnalyzer**: Control flow analysis

#### Usage Example

```python
from hb_lcs.ast_integration import ASTToCGenerator, ASTToWasmGenerator

# Convert to C
c_gen = ASTToCGenerator(config)
c_code = c_gen.translate(ast, config)

# Convert to WASM
wasm_gen = ASTToWasmGenerator(config)
wasm_module = wasm_gen.translate(ast, config)
```

#### Architecture

```
Language AST
    ↓
ASTVisitor Pattern
    ↓ (visit_* methods)
Symbol Table (scope management)
    ↓
Type Inference Pass
    ↓
Code Generation
    ├─ C Code (CCodeGenerator)
    └─ WASM (WasmModule)
```

### 2. ✅ Generics System Integration with Type Checker

**File**: `src/hb_lcs/type_system_generics.py` (450+ lines)

Integrates Phase 4 generics with existing type system:

#### Components

- **GenericsTypeChecker**: Extended type checker with generic support
  - Generic function checking
  - Generic class checking
  - Type instantiation validation
  - Type argument inference
  - Variance checking
  
- **ProtocolTypeChecker**: Protocol system integration
  - Conformance checking
  - Structural type extraction
  - Protocol registration
  
- **TypeNarrowingPass**: Type narrowing via control flow
  - isinstance narrowing
  - Truthiness narrowing
  - Comparison narrowing

#### Usage Example

```python
from hb_lcs.type_system_generics import GenericsTypeChecker

checker = GenericsTypeChecker(config)

# Check generic function
errors = checker.check_generic_function("Map", ["K", "V"], func_def)

# Check instantiation
success, errors = checker.check_generic_instantiation("Map", ["str", "int"])

# Infer type arguments
inferred, errors = checker.infer_type_arguments("Map", actual_args)

# Check variance
valid, msg = checker.check_variance("Map", 0, Variance.COVARIANT)
```

#### Architecture

```
TypeChecker (existing)
    ↑
    └─ GenericsTypeChecker (extends)
        ├─ GenericChecker (generics module)
        ├─ ProtocolChecker (protocols module)
        └─ TypeNarrowingPass
```

## In Progress & Upcoming

### 3. Protocol/Type System Integration (Next)

Will add protocol checking to main type system:

```python
# Check protocol conformance
checker.check_protocol_conformance(type_name, protocol_name)

# Register protocols
checker.register_protocol("Comparable", protocol_def)
```

### 4. Type Narrowing Implementation

Will implement comprehensive type narrowing:

```python
# In if condition: isinstance(x, int)
if x is int:
    # x is narrowed to int type
    pass

# In if condition: x is not None
if x is not None:
    # x is narrowed to non-optional type
    pass
```

### 5. LSP Server Integration

Will connect all LSP features to the server:

```python
# Refactoring
server.register_refactoring_provider(RefactoringEngine)

# Formatting
server.register_formatting_provider(CodeFormatter)

# Debugging (DAP)
server.register_debug_adapter(DebugAdapter)

# Semantic highlighting
server.register_semantic_token_provider(SemanticHighlighter)
```

### 6. Package Registry Remote Backend

Will add remote package server:

```python
# Register with remote registry
registry.add_remote("https://packages.example.com")

# Search packages
results = registry.search("json-parser")

# Install from remote
registry.install("json-parser@^1.0.0")
```

## Integration Patterns Used

### 1. Visitor Pattern (AST Traversal)
```python
class MyVisitor(ASTVisitor):
    def visit_function(self, node):
        # Process function node
        for child in node.children:
            self.visit(child)
```

### 2. Symbol Table (Scope Management)
```python
symbol_table = SymbolTable()
symbol_table.push_scope()  # Enter scope
symbol_table.declare("x", TypeInfo("int"))
symbol_table.pop_scope()   # Exit scope
```

### 3. Type Inference (Bottom-Up)
```python
type_info = TypeInferencePass().infer(ast)
# Results in Dict[node_id, Type]
```

### 4. Control Flow Analysis
```python
flow = ControlFlowAnalyzer().analyze(ast)
# Returns: {branches: [...], loops: [...], returns: [...]}
```

## File Structure

```
src/hb_lcs/
├── Phase 4 Modules (2,600+ lines)
│   ├── generics.py (300)
│   ├── protocols.py (350)
│   ├── codegen_c.py (300)
│   ├── codegen_wasm.py (400)
│   ├── package_registry.py (400)
│   ├── lsp_advanced.py (500)
│   ├── testing_framework.py (400)
│   └── debug_adapter.py (450)
│
├── Phase 5 Integration (950+ lines)
│   ├── ast_integration.py (500) ← NEW
│   └── type_system_generics.py (450) ← NEW
│
└── Existing Systems
    ├── type_system.py (547)
    ├── language_config.py
    ├── lsp_server.py (551)
    ├── module_system.py (624)
    └── cli.py (1900+)
```

## Next Phase Tasks

### High Priority (Impact & Dependencies)

1. **Protocol-Type Integration** (impacts type safety)
   - Add protocol conformance to type checker
   - Implement structural type extraction
   - Wire to LSP server

2. **LSP Server Extensions** (impacts IDE experience)
   - Add refactoring provider
   - Add formatting provider
   - Add semantic tokens provider
   - Wire DAP for debugging

3. **Package Registry Backend** (impacts module ecosystem)
   - Implement remote registry client
   - Add authentication
   - Add package discovery

### Medium Priority (Quality & Features)

4. **Type Narrowing Implementation**
   - Control flow analysis
   - Type guards
   - Narrowing inference

5. **Comprehensive Test Suite**
   - Unit tests for all modules
   - Integration tests
   - End-to-end tests

6. **Performance Optimization**
   - Caching strategies
   - Algorithm optimization
   - Benchmarking

## Quality Checklist

- [ ] All Phase 5 modules have 100% type hints
- [ ] All Phase 5 modules have comprehensive docstrings
- [ ] All integrations tested with existing code
- [ ] Zero breaking changes
- [ ] All imports resolvable
- [ ] MyPy compatibility verified
- [ ] Documentation updated
- [ ] CLI commands tested
- [ ] Examples working

## Performance Targets

- Type checking: < 100ms for medium file
- Code generation: Linear in AST size
- Module resolution: O(log n) for n modules
- Debug breakpoint hit: < 1ms
- Formatting: < 50ms for medium file

## Success Criteria

✅ **Phase 5 Success** when:
1. All code generators connected to AST system
2. Generics fully integrated with type checker
3. Protocols integrated with type checking
4. LSP features connected to server
5. Package registry has remote backend
6. Comprehensive test suite passes
7. All documentation updated
8. Zero breaking changes maintained
9. Performance targets met
10. Ready for Phase 6 (Polish & Optimization)

## Resources

- AST Integration: [ast_integration.py](../src/hb_lcs/ast_integration.py)
- Generics Integration: [type_system_generics.py](../src/hb_lcs/type_system_generics.py)
- Phase 4 Modules: [src/hb_lcs/](../src/hb_lcs/)
- Type System: [type_system.py](../src/hb_lcs/type_system.py)
- LSP Server: [lsp_server.py](../src/hb_lcs/lsp_server.py)

## Contact & Support

For questions about Phase 5 integration:
- Review documentation files
- Check existing integration patterns
- Refer to Phase 4 module docstrings
- See inline code comments

---

**Phase 5 Status**: In Progress
**Last Updated**: 2026-01-04
**Next Review**: After protocol integration complete
