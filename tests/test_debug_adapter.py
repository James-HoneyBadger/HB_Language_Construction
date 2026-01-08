import pytest
from src.parsercraft.debug_adapter import (
    Debugger, Breakpoint, StackFrame, ExecutionState, SourceReference
)

def test_debugger_initialization():
    dbg = Debugger("main.pc")
    assert dbg.state == ExecutionState.IDLE
    assert dbg.program_path == "main.pc"
    assert len(dbg.call_stack) == 0

def test_breakpoint_management():
    dbg = Debugger("main.pc")
    
    # Add Breakpoint
    bp = dbg.set_breakpoint("main.pc", 10, condition="x > 5")
    assert bp.id == 1
    assert bp.line == 10
    assert bp.verified
    
    bps = dbg.get_breakpoints("main.pc")
    assert len(bps) == 1
    assert bps[0] == bp
    
    # Remove Breakpoint
    removed = dbg.remove_breakpoint(1)
    assert removed
    assert len(dbg.get_breakpoints("main.pc")) == 0
    
    # Remove non-existent
    assert not dbg.remove_breakpoint(99)

def test_execution_control():
    dbg = Debugger("main.pc")
    
    dbg.start()
    assert dbg.state == ExecutionState.RUNNING
    
    dbg.pause()
    assert dbg.state == ExecutionState.STOPPED
    
    dbg.continue_execution()
    assert dbg.state == ExecutionState.RUNNING

def test_stepping_logic():
    dbg = Debugger("main.pc")
    dbg.start()
    
    # Step In - should create a frame
    dbg.step_in()
    assert len(dbg.call_stack) == 1
    assert dbg.call_stack[0].name == "function_call"
    
    # Step Over - should increment line
    frame_line_before = dbg.call_stack[0].line
    dbg.step_over()
    assert dbg.call_stack[0].line == frame_line_before + 1
    
    # Step Out - should pop frame
    dbg.step_out()
    assert len(dbg.call_stack) == 0

def test_data_classes_serialization():
    bp = Breakpoint(1, "test.pc", 5)
    d = bp.to_dict()
    assert d["id"] == 1
    assert d["source"]["path"] == "test.pc"
    
    sf = StackFrame(1, "main", "test.pc", 10)
    d2 = sf.to_dict()
    assert d2["id"] == 1
    assert d2["name"] == "main"
    
    sr = SourceReference("path/to/file", 1)
    d3 = sr.to_dict()
    assert d3["name"] == "file"
