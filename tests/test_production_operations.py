import pytest
from src.parsercraft.production_operations import (
    ServiceHealthMonitor, RecoveryManager, RecoveryPlan, RecoveryStrategy,
    ServiceHealth, HealthCheck, HealthCheckProvider
)
from unittest.mock import MagicMock 

class MockProvider(HealthCheckProvider):
    def check_health(self) -> HealthCheck:
        return HealthCheck("test", ServiceHealth.HEALTHY, 1.0, 10, "ok")

def test_health_monitor():
    monitor = ServiceHealthMonitor()
    monitor.register_provider("test_svc", MockProvider())
    
    # Needs to handle the try/except in check_all
    # But check_all updates health_history
    monitor.check_all()
    
    # We can inspect monitor.health_history or similar if exposed
    # health_history is dict[name, list]
    assert "test_svc" in monitor.health_history
    assert len(monitor.health_history["test_svc"]) == 1
    assert monitor.health_history["test_svc"][0].status == ServiceHealth.HEALTHY

def test_retry_strategy():
    monitor = ServiceHealthMonitor()
    manager = RecoveryManager(monitor)
    
    plan = RecoveryPlan("op_retry", RecoveryStrategy.RETRY, max_retries=3, retry_delay_ms=1)
    monitor.register_recovery_plan("op", plan)
    
    mock_func = MagicMock(side_effect=[ValueError("fail"), ValueError("fail"), "success"])
    
    success, result = manager.execute_recovery("op", mock_func)
    
    assert success
    assert result == "success"
    assert mock_func.call_count == 3

def test_retry_strategy_fail():
    monitor = ServiceHealthMonitor()
    manager = RecoveryManager(monitor)
    
    plan = RecoveryPlan("op_retry_fail", RecoveryStrategy.RETRY, max_retries=2, retry_delay_ms=1)
    monitor.register_recovery_plan("op", plan)
    
    mock_func = MagicMock(side_effect=[ValueError("fail"), ValueError("fail"), ValueError("fail")])
    
    success, result = manager.execute_recovery("op", mock_func)
    
    assert not success
    assert isinstance(result, ValueError)
    assert mock_func.call_count == 2 # Max retries

def test_fallback_strategy():
    monitor = ServiceHealthMonitor()
    manager = RecoveryManager(monitor)
    
    fallback = MagicMock(return_value="fallback_val")
    plan = RecoveryPlan("op_fallback", RecoveryStrategy.FALLBACK, fallback_handler=fallback)
    monitor.register_recovery_plan("op", plan)
    
    mock_func = MagicMock(side_effect=ValueError("primary_fail"))
    
    success, result = manager.execute_recovery("op", mock_func)
    assert success
    assert result == "fallback_val"
    fallback.assert_called_once()

def test_degradation_strategy():
    monitor = ServiceHealthMonitor()
    manager = RecoveryManager(monitor)
    
    plan = RecoveryPlan("op_degrade", RecoveryStrategy.GRACEFUL_DEGRADE)
    monitor.register_recovery_plan("op", plan)
    
    mock_func = MagicMock(side_effect=ValueError("fail"))
    
    success, result = manager.execute_recovery("op", mock_func)
    assert not success
    assert isinstance(result, dict)
    assert result["degraded"] == True
