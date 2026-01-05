# Type System & Static Analysis Guide

**Add Professional Type Safety to ParserCraft Languages**

## Overview

ParserCraft now includes an optional **Type System** with:

✅ **Type Annotations** - Declare variable and function types
✅ **Type Inference** - Automatic type deduction
✅ **Static Analysis** - Find errors before runtime
✅ **Type Checking Levels** - From lenient to very strict
✅ **IDE Integration** - Type-aware completions and hints
✅ **Generic Types** - `list[int]`, `dict[str, int]`
✅ **Union Types** - `int | str | bool`
✅ **Null Safety** - Optional types with `?`

## Quick Start

### Basic Type Annotations

```teach
# Variable with type annotation
x: int = 5
message: str = "hello"
values: list[int] = [1, 2, 3]

# Function with types
export function add(x: int, y: int) -> int
    return x + y
end

# Optional types
name: str? = none  # Can be string or none
```

### Type Checking Levels

**Lenient** (default for compatibility):
```python
checker = TypeChecker(config, level=AnalysisLevel.LENIENT)
# Minimal type checking, mostly type inference
```

**Moderate** (recommended):
```python
checker = TypeChecker(config, level=AnalysisLevel.MODERATE)
# Standard type safety checks
```

**Strict** (professional):
```python
checker = TypeChecker(config, level=AnalysisLevel.STRICT)
# Enforce all type safety rules
```

**Very Strict** (maximum safety):
```python
checker = TypeChecker(config, level=AnalysisLevel.VERY_STRICT)
# No implicit types, all annotations required
```

## Type Annotations

### Basic Types

```teach
x: int = 42
y: float = 3.14
name: str = "Alice"
active: bool = true
nothing: none = none
```

### Collection Types

```teach
# Lists
numbers: list[int] = [1, 2, 3]
mixed: list[any] = [1, "two", 3.0]

# Dictionaries
person: dict[str, any] = {"name": "Alice", "age": 30}
scores: dict[str, int] = {"math": 95, "english": 87}

# Sets
unique: set[int] = {1, 2, 3}

# Tuples
pair: tuple[int, str] = (42, "answer")
```

### Optional Types

```teach
# Can be string or none
maybe_name: str? = none
maybe_value: int? = 10

# Null coalescing
result = maybe_name ?? "unknown"
```

### Union Types

```teach
# Can be int or string
value: int | str = "hello"
value = 42  # Also valid

# Multiple types
result: int | float | str = 3.14
```

### Custom Types

```teach
export class Point
    x: int
    y: int
end

location: Point = Point()
```

## Function Type Signatures

### Simple Functions

```teach
export function greet(name: str) -> str
    return "Hello, " + name
end

export function abs_value(n: int) -> int
    when n < 0
        return -n
    end
    return n
end
```

### Multiple Parameters

```teach
export function distance(x1: float, y1: float, x2: float, y2: float) -> float
    dx = x2 - x1
    dy = y2 - y1
    return sqrt(dx * dx + dy * dy)
end
```

### Variadic Functions

```teach
export function sum(numbers: int...) -> int
    total = 0
    for number in numbers
        total = total + number
    end
    return total
end
```

### Generic Functions

```teach
export function first[T](items: list[T]) -> T?
    when len(items) > 0
        return items[0]
    end
    return none
end

# Usage
first([1, 2, 3])      # Returns int?
first(["a", "b"])     # Returns str?
```

## Type Inference

### Automatic Type Deduction

```teach
# Type inferred as int
count = 5

# Type inferred as str
greeting = "hello"

# Type inferred as list[int]
numbers = [1, 2, 3, 4]

# Type inferred as dict[str, int]
ages = {"alice": 30, "bob": 25}
```

### Context-Based Inference

```teach
# Function return type inferred
export function get_count()
    return 42  # Inferred as int
end

# Variable type from assignment
value = get_count()  # Type inferred as int
```

## Static Analysis

### Type Checking

```python
from hb_lcs.type_system import TypeChecker, AnalysisLevel

checker = TypeChecker(config, level=AnalysisLevel.STRICT)
errors = checker.check_file("program.lang")

for error in errors:
    print(f"{error.location}: {error.message}")
    if error.suggestion:
        print(f"  Suggestion: {error.suggestion}")
```

### Getting Type Information

```python
from hb_lcs.type_system import TypeEnvironment

env = TypeEnvironment()
env.define_variable("x", Type.int())

type_of_x = env.get_variable_type("x")
print(type_of_x)  # int
```

### Type Compatibility

```python
from hb_lcs.type_system import Type

int_type = Type.int()
float_type = Type.float()

# Check compatibility
if int_type.is_compatible_with(float_type):
    print("Compatible")
```

## Error Messages

### Type Mismatch

```teach
x: int = "hello"  # Error: Cannot assign str to int
```

Output:
```
[E101] Type mismatch: cannot assign str to int at line 1
Suggestion: Change source to int or target to str
```

### Undefined Variable

```teach
y = x + 1  # Error: x is undefined
```

Output:
```
[E102] Undefined variable 'x' at line 1
Suggestion: Define x before use
```

### Function Arity Mismatch

```teach
result = add(5)  # Error: Expected 2 arguments, got 1
```

Output:
```
[E103] Function 'add' expects 2 arguments, got 1 at line 1
Suggestion: Pass 2 arguments to add()
```

## Advanced Features

### Type Aliases

```teach
#: type Integer = int
#: type StringDict = dict[str, str]

count: Integer = 10
config: StringDict = {"key": "value"}
```

### Structural Typing

```teach
export class Animal
    name: str
    age: int
end

export class Pet
    name: str
    age: int
    # Has same structure as Animal
end

# Compatible due to structural typing
animal: Animal = Pet()
```

### Type Guards

```teach
value: int | str = get_value()

when value is int
    # Inside this block, value is known to be int
    x = value + 1
end

when value is str
    # Inside this block, value is known to be str
    len = len(value)
end
```

### Generics

```teach
export class Container[T]
    value: T
end

export function wrap[T](item: T) -> Container[T]
    return Container(item)
end

# Usage
int_container = wrap[int](42)
str_container = wrap[str]("hello")
```

## LSP Integration

### Type-Aware Completions

```python
from hb_lcs.type_system import TypeAwareAnalyzer

analyzer = TypeAwareAnalyzer(checker)
completions = analyzer.get_type_completions(environment)

# Returns completions with type information:
# x: int
# name: str
# add: (int, int) -> int
```

### Hover Type Information

```python
hover_info = analyzer.get_hover_with_type("x", environment)
# Returns: "**x**: int"
```

### Inline Type Hints

In IDE with LSP:
```teach
x = 5         # Hover shows: x: int
message = "hi"  # Hover shows: message: str
```

## Best Practices

### 1. Annotate Public APIs

```teach
# Good: Public function has complete type info
export function calculate(x: int, y: int) -> int
    return x + y
end

# Avoid: No type information
export function process(x, y)
    return x + y
end
```

### 2. Use Type Inference for Locals

```teach
# Good: Let type inference handle local variables
function process(data: list[str]) -> int
    total = 0  # Type inferred as int
    for item in data
        count = len(item)  # Type inferred as int
        total = total + count
    end
    return total
end
```

### 3. Leverage Optional Types

```teach
# Good: Makes nullability explicit
function find_user(id: int) -> User?
    when id > 0
        return get_user_by_id(id)
    end
    return none
end

# Usage
user = find_user(123)
when user is not none
    say user.name
end
```

### 4. Use Union Types for Multiple Possibilities

```teach
# Good: Clear about what's possible
export function parse_value(input: str) -> int | float | str
    when starts_with(input, "0x")
        return parse_hex(input)
    end
    when contains(input, ".")
        return parse_float(input)
    end
    return input
end
```

### 5. Document Complex Types

```teach
#: Represents a 2D point in space
#: x and y coordinates as integers
export class Point
    x: int  #: X coordinate
    y: int  #: Y coordinate
end

export function distance(p1: Point, p2: Point) -> float
    #: Calculate Euclidean distance between two points
    return sqrt((p2.x - p1.x)^2 + (p2.y - p1.y)^2)
end
```

## Performance Impact

### Type Checking Overhead

- **Lenient**: ~1% overhead (mostly skipped)
- **Moderate**: ~5% overhead (recommended)
- **Strict**: ~10% overhead (for large programs)
- **Very Strict**: ~15% overhead

### Optimization Tips

1. **Enable caching** for incremental checking
2. **Check only changed files** in development
3. **Use lenient mode** during development
4. **Switch to strict mode** before deployment

## Troubleshooting

### Type Not Found

```
Error: Unknown type 'MyType'
```

**Solutions:**
1. Import the module defining MyType
2. Check type name spelling
3. Verify type is exported (not private)

### Incompatible Types

```
Error: Cannot assign str to int
```

**Solutions:**
1. Convert types explicitly: `int(x)`
2. Use union type: `x: int | str`
3. Change assignment target type

### Missing Type Annotation

```
Error: Strict mode requires type annotations
```

**Solutions:**
1. Add type annotation: `x: int = 5`
2. Switch to less strict mode
3. Use type inference (moderate mode only)

## Migration Guide

### From Untyped to Typed

**Before:**
```teach
export function add(x, y)
    return x + y
end
```

**After (Moderate):**
```teach
export function add(x: any, y: any) -> any
    return x + y
end
```

**After (Strict):**
```teach
export function add(x: int, y: int) -> int
    return x + y
end
```

## CLI Commands

```bash
# Type check a file
parsercraft type-check program.lang

# Type check with strict mode
parsercraft type-check program.lang --level strict

# Generate type information
parsercraft type-info program.lang

# Export type information as JSON
parsercraft type-export program.lang --output types.json
```

## Resources

- **Type System API**: See `src/hb_lcs/type_system.py`
- **TypeChecker class**: Core type checking engine
- **TypeEnvironment class**: Type scope management
- **Type class**: Type representation

---

**Last Updated:** January 2026
**ParserCraft Version:** 2.0.0
