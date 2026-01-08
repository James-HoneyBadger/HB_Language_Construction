import pytest
from src.parsercraft.advanced_debugging_hardware import (
    TimeTravelDebugger, ExecutionSnapshot, DebugAction
)

def test_debugger_lifecycle():
    debugger = TimeTravelDebugger(max_snapshots=5)
    debugger.start_recording()
    
    # Record 3 steps
    debugger.record_snapshot(DebugAction.VARIABLE_ASSIGN, "f:1", {"x": 1}, [], 100)
    debugger.record_snapshot(DebugAction.VARIABLE_ASSIGN, "f:2", {"x": 2}, [], 100)
    debugger.record_snapshot(DebugAction.VARIABLE_ASSIGN, "f:3", {"x": 3}, [], 100)
    
    assert len(debugger.snapshots) == 3
    assert debugger.current_step == 3
    
    # Step Back -> To snapshot index 2 (Step 3)
    snap = debugger.step_backward()
    assert snap.step_number == 2
    assert snap.variables["x"] == 3
    assert debugger.current_step == 2
    
    # Step Back -> To snapshot index 1 (Step 2)
    snap = debugger.step_backward()
    assert snap.step_number == 1
    assert snap.variables["x"] == 2
    assert debugger.current_step == 1
    
    # Step Forward -> To snapshot index 2 (Step 3) - Logic check
    # step_forward increments current_step (to 2) then returns snapshots[2-1=1] ???
    # Let's check logic:
    # if 1 < 3: step=2; return snap[1] (which is step 2, var x=2)
    # This implies step_forward returns the state *just executed* to reach new current_step?
    # Or is it replays the step?
    
    # Current code:
    # current_step = 1.
    # step_forward(): current_step=2. return snapshots[1] (the one at index 1).
    # This means we are "at" index 2, and we replayed index 1. Correct.
    snap = debugger.step_forward()
    assert snap.step_number == 1
    assert snap.variables["x"] == 2
    
    snap = debugger.step_forward()
    assert snap.step_number == 2
    assert snap.variables["x"] == 3

def test_max_snapshots():
    debugger = TimeTravelDebugger(max_snapshots=2)
    debugger.start_recording()
    
    debugger.record_snapshot(DebugAction.VARIABLE_ASSIGN, "1", {}, [], 0)
    debugger.record_snapshot(DebugAction.VARIABLE_ASSIGN, "2", {}, [], 0)
    debugger.record_snapshot(DebugAction.VARIABLE_ASSIGN, "3", {}, [], 0)
    
    assert len(debugger.snapshots) == 2
    # Should have popped the first one (step 0).
    # Remaining should be step 1 and step 2.
    assert debugger.snapshots[0].step_number == 1
    assert debugger.snapshots[1].step_number == 2

def test_jump_to_step():
    debugger = TimeTravelDebugger()
    debugger.start_recording()
    debugger.record_snapshot(DebugAction.VARIABLE_ASSIGN, "1", {}, [], 0)
    debugger.record_snapshot(DebugAction.VARIABLE_ASSIGN, "2", {}, [], 0)
    
    snap = debugger.jump_to_step(0)
    assert snap.step_number == 0
    assert debugger.current_step == 0
