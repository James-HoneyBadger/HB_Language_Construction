# ParserCraft ↔ CodeEx Integration Guide

Complete guide for integrating ParserCraft language definitions with CodeEx IDE.

## Overview

CodeEx and ParserCraft work together to enable:

1. **ParserCraft**: Define custom programming languages
2. **CodeEx**: Develop and run applications in those languages

The integration uses the `InterpreterGenerator` system to bridge both tools.

## Architecture

### System Flow

```
┌─────────────────────┐
│   ParserCraft IDE     │
│  (language config)  │
└──────────┬──────────┘
           │
     Creates/Exports
           │
           ▼
┌──────────────────────────────────┐
│ InterpreterGenerator System      │
│ (interpreter_generator.py)       │
│                                  │
│ - InterpreterPackage             │
│ - Serialization (JSON/Pickle)    │
│ - Export/Import                  │
└──────────┬───────────────────────┘
           │
    Generates/Imports
           │
           ▼
┌─────────────────────────────────┐
│    CodeEx IDE                   │
│  (load and execute code)        │
│                                 │
│ - Projects                      │
│ - Editor with syntax            │
│ - Console output                │
│ - Multi-language support        │
└─────────────────────────────────┘
```

## Creating a Language in ParserCraft

### Step 1: Define Language Configuration

Create `my_language.json`:

```json
{
  "name": "MyLanguage",
  "version": "1.0.0",
  "description": "Custom language for CodeEx",
  "file_extension": ".ml",
  "keywords": [
    "print", "if", "else", "while", "for",
    "define", "return", "end"
  ],
  "functions": {
    "print": {
      "params": ["value"],
      "description": "Output value to console",
      "example": "print 'Hello World'"
    },
    "len": {
      "params": ["string"],
      "description": "Get length of string",
      "example": "length = len 'hello'"
    }
  },
  "operators": ["+", "-", "*", "/", "=", "==", "!=", "<", ">"],
  "comments": "#",
  "string_delimiters": ["'", "\""],
  "case_sensitive": true,
  "indent_style": "spaces",
  "indent_size": 2
}
```

### Step 2: Test in ParserCraft IDE

1. Open ParserCraft IDE
2. Load your configuration file
3. Test the language features
4. Verify syntax highlighting works

## Exporting Language to CodeEx

### Method 1: Python API

```python
from src.hb_lcs.language_config import LanguageConfig
from src.hb_lcs.interpreter_generator import InterpreterGenerator

# Step 1: Load language configuration
config = LanguageConfig.load("my_language.json")

# Step 2: Create interpreter generator
generator = InterpreterGenerator()

# Step 3: Generate interpreter
interpreter = generator.generate(config)

# Step 4: Export for CodeEx
exported_path = generator.export_interpreter(config, format="json")
print(f"Exported to: {exported_path}")
```

### Method 2: Command Line

```bash
cd /path/to/ParserCraft

# Generate and export
python -c "
from src.hb_lcs.language_config import LanguageConfig
from src.hb_lcs.interpreter_generator import InterpreterGenerator

config = LanguageConfig.load('my_language.json')
gen = InterpreterGenerator()
path = gen.export_interpreter(config, format='json')
print(f'Exported: {path}')
"
```

## Using Exported Interpreter in CodeEx

### Step 1: Launch CodeEx

```bash
python codex.py
```

### Step 2: Create Project

1. Click **New Project**
2. Name it: `MyLanguageProject`
3. Click **Create**

### Step 3: Load Interpreter

1. Click **Load Interpreter**
2. Navigate to one of:
   - `~/.parsercraft/interpreters/` (exported by ParserCraft)
   - `configs/examples/` (pre-built examples)
   - Your custom JSON file
3. Select your language file
4. CodeEx loads the interpreter

### Step 4: Write and Execute Code

In the CodeEx editor:

```
print "Hello from MyLanguage!"
x = 10
y = 20
print x + y
```

Click **▶ Run** to execute.

## Advanced Integration

### Multiple Language Project

Create separate projects for different languages:

```
~/.codex/projects/
├── Python_Dialect/
│   ├── project.json (interpreter: python_like)
│   └── src/
├── Logo_Variant/
│   ├── project.json (interpreter: logo_like)
│   └── src/
└── Lisp_Edition/
    ├── project.json (interpreter: lisp_like)
    └── src/
```

Each project can have different language interpreter.

### Language Library

Create a collection of language configurations:

```
~/parsercraft_languages/
├── python_like.json
├── logo_like.json
├── scheme_like.json
└── basic_like.json
```

Load any of these in CodeEx to develop programs.

## Understanding Exported Interpreters

### JSON Export Format

```json
{
  "name": "MyLanguage",
  "version": "1.0.0",
  "created": "2024-01-15T10:30:45.123456",
  "metadata": {
    "keywords_count": 7,
    "functions_count": 2,
    "operators_count": 9
  },
  "config": {
    "name": "MyLanguage",
    "keywords": [...],
    "functions": {...},
    "operators": [...]
  }
}
```

### Pickle Export Format

Binary format for efficient loading and execution. Used internally by CodeEx.

## Interpreter Object Interface

Once loaded, interpreters provide:

### Execute Code

```python
# In CodeEx, internally:
result = interpreter.execute(code)
```

Result structure:
```python
{
    "status": "success" or "error",
    "output": "printed output or error message",
    "errors": [],  # list of error strings
    "variables": {}  # current variable state
}
```

### Access Metadata

```python
# Language name
name = interpreter.config.name

# Available keywords
keywords = interpreter.config.keywords

# Available functions
functions = interpreter.config.functions

# Available operators
operators = interpreter.config.operators
```

## Example Workflows

### Workflow 1: Create Simple Calculator Language

**In ParserCraft**:
```json
{
  "name": "Calculator",
  "keywords": ["var", "print", "add", "subtract"],
  "functions": {
    "add": {"params": ["a", "b"], "example": "add 5 3"},
    "subtract": {"params": ["a", "b"], "example": "subtract 10 3"}
  }
}
```

**Export and Use in CodeEx**:
```
# CodeEx editor:
var x = add 10 5
print x

var y = subtract x 3
print y
```

### Workflow 2: Multiple Language Classroom

**In ParserCraft**: Create 5 language variants
**Export**: Each to JSON
**In CodeEx**: 
- Student 1 loads Python variant
- Student 2 loads Logo variant
- Student 3 loads Lisp variant
- All in same IDE, different projects

### Workflow 3: Language Testing

**In ParserCraft**: Design language
**Export**: With test suite
**In CodeEx**:
1. Create "TestProject"
2. Load interpreter
3. Copy test code to editor
4. Run tests
5. Verify behavior

## Troubleshooting Integration

### Interpreter Won't Load in CodeEx

**Check configuration file**:
```python
from src.hb_lcs.language_config import LanguageConfig

# Verify file is valid
try:
    config = LanguageConfig.load("my_language.json")
    print(f"Valid: {config.name}")
except Exception as e:
    print(f"Error: {e}")
```

**Required fields** in JSON:
- `name`: Language name
- `keywords`: List of keywords
- `functions`: Dictionary of functions
- `operators`: List of operators

### Code Won't Execute

**Check syntax**:
- Code must follow language rules
- Keywords must match exactly
- Operators must be defined in config
- Comments must use correct delimiter

**Enable debug output**:
```python
# In CodeEx console, error appears with line number
# Check syntax against loaded language
```

### Wrong Syntax Highlighting

**Verify config loaded**:
- Status bar shows correct interpreter name
- Dropdown shows correct selection

**Check keywords in config**:
```python
config = LanguageConfig.load("my_language.json")
print(config.keywords)
# Should match code tokens
```

## Best Practices

### Language Design

1. **Keep keywords simple**: Shorter names easier to type
2. **Clear semantics**: Obvious what each keyword does
3. **Consistent style**: Similar patterns for similar operations
4. **Document well**: Use descriptions in config
5. **Provide examples**: Help users understand usage

### Configuration Management

1. **Version your languages**: Use semantic versioning
2. **Test before export**: Verify in ParserCraft first
3. **Organize exports**: Keep interpreters in standard location
4. **Document purpose**: Add description field
5. **Include examples**: Put example code in projects

### CodeEx Project Organization

```
Language_Project/
├── project.json          # Metadata + interpreter name
├── src/
│   ├── hello.ml          # Programs using the language
│   └── calculator.ml
├── examples/
│   ├── example1.ml       # Reference implementations
│   └── example2.ml
└── tests/
    └── test_program.ml   # Test code
```

## Integration API Reference

### InterpreterGenerator Class

**Location**: `src/hb_lcs/interpreter_generator.py`

**Key Methods**:

```python
# Generate interpreter from config
interpreter = gen.generate(config)

# Export for distribution
path = gen.export_interpreter(config, format="json|pickle")

# Import from exported data
interpreter = gen.import_interpreter(data, format="json|pickle")

# List all interpreters
all_interps = gen.list_interpreters()

# Get specific interpreter
interp = gen.get_interpreter("MyLanguage")
```

**Formats**:
- `"json"`: Human-readable JSON
- `"pickle"`: Binary format
- `"file"`: Writes to disk

### LanguageConfig Class

**Location**: `src/hb_lcs/language_config.py`

**Key Methods**:

```python
# Load from file
config = LanguageConfig.load("file.json")

# Save to file
config.save("file.json")

# Access attributes
name = config.name
keywords = config.keywords
functions = config.functions
operators = config.operators
```

## Related Documentation

- [LANGUAGE_DEVELOPMENT_GUIDE.md](./LANGUAGE_DEVELOPMENT_GUIDE.md) - ParserCraft language creation
- [CODEX_USER_GUIDE.md](./CODEX_USER_GUIDE.md) - CodeEx IDE usage
- [CODEX_QUICKSTART.md](./CODEX_QUICKSTART.md) - Quick start for CodeEx
- [interpreter_generator.py](../../src/hb_lcs/interpreter_generator.py) - Integration API

## Summary

1. **Design language** in ParserCraft
2. **Export interpreter** using InterpreterGenerator
3. **Load in CodeEx** using "Load Interpreter"
4. **Write and execute code** in CodeEx editor
5. **Iterate and improve** language design
6. **Share interpreters** with other users

Together, ParserCraft and CodeEx provide complete environment for:
- Creating custom languages
- Developing applications
- Teaching programming
- Experimenting with syntax
- Building educational tools
