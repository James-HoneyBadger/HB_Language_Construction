"""
Phase 7 Production Tests

Comprehensive test suite for error handling, recovery, rate limiting, and operations.
"""

import pytest
import time
from unittest.mock import Mock, patch, MagicMock

from src.hb_lcs.production_error_handling import (
    RetryConfig,
    retry_with_backoff,
    RetryableError,
    CircuitBreakerConfig,
    CircuitBreaker,
    CircuitBreakerState,
    RateLimitConfig,
    RateLimiter,
    AuditLogger,
    ProductionErrorHandler,
    ErrorCategory,
    ErrorSeverity,
)

from src.hb_lcs.production_operations import (
    ServiceHealth,
    HealthCheck,
    HealthCheckProvider,
    ServiceHealthMonitor,
    RecoveryManager,
    RecoveryPlan,
    RecoveryStrategy,
    GracefulShutdown,
    OperationsGuide,
)


# ============================================================================
# Retry Logic Tests
# ============================================================================


class TestRetryLogic:
    """Test retry logic with exponential backoff."""

    def test_retry_success_on_first_attempt(self):
        """Test successful operation on first attempt."""
        call_count = 0

        @retry_with_backoff()
        def successful_function():
            nonlocal call_count
            call_count += 1
            return "success"

        result = successful_function()
        assert result == "success"
        assert call_count == 1

    def test_retry_success_after_failures(self):
        """Test retry succeeds after temporary failures."""
        call_count = 0

        @retry_with_backoff()
        def eventually_successful():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise ConnectionError("Temporary failure")
            return "success"

        result = eventually_successful()
        assert result == "success"
        assert call_count == 3

    def test_retry_fails_after_max_attempts(self):
        """Test retry fails after max attempts."""
        @retry_with_backoff()
        def always_fails():
            raise ConnectionError("Always fails")

        with pytest.raises(RetryableError):
            always_fails()

    def test_retry_custom_config(self):
        """Test retry with custom configuration."""
        config = RetryConfig(
            max_attempts=2,
            initial_delay=0.001,
            exponential_base=2.0,
        )

        call_count = 0

        @retry_with_backoff(config)
        def fails_twice():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError()
            return "success"

        result = fails_twice()
        assert result == "success"
        assert call_count == 2

    def test_retry_non_retryable_exception(self):
        """Test non-retryable exceptions are not retried."""
        call_count = 0

        @retry_with_backoff()
        def raises_non_retryable():
            nonlocal call_count
            call_count += 1
            raise ValueError("Not retryable")

        with pytest.raises(ValueError):
            raises_non_retryable()

        assert call_count == 1  # Not retried


class TestRetryConfig:
    """Test retry configuration."""

    def test_exponential_backoff_delay(self):
        """Test exponential backoff delay calculation."""
        config = RetryConfig(
            initial_delay=0.1,
            exponential_base=2.0,
            jitter=False,
        )

        assert config.get_delay(0) == 0.1
        assert config.get_delay(1) == 0.2
        assert config.get_delay(2) == 0.4
        assert config.get_delay(3) == 0.8

    def test_max_delay_capped(self):
        """Test max delay is capped."""
        config = RetryConfig(
            initial_delay=1.0,
            exponential_base=2.0,
            max_delay=5.0,
            jitter=False,
        )

        delay = config.get_delay(10)  # Would be 1024 without cap
        assert delay == 5.0


# ============================================================================
# Circuit Breaker Tests
# ============================================================================


class TestCircuitBreaker:
    """Test circuit breaker pattern."""

    def test_circuit_closed_allows_calls(self):
        """Test closed circuit allows calls."""
        cb = CircuitBreaker(name="test")
        assert cb.state == CircuitBreakerState.CLOSED

        def success_func():
            return "success"

        result = cb.call(success_func)
        assert result == "success"

    def test_circuit_opens_after_failures(self):
        """Test circuit opens after failure threshold."""
        config = CircuitBreakerConfig(failure_threshold=3)
        cb = CircuitBreaker(config, name="test")

        def fail_func():
            raise Exception("Failed")

        for _ in range(3):
            with pytest.raises(Exception):
                cb.call(fail_func)

        assert cb.state == CircuitBreakerState.OPEN

    def test_circuit_rejects_calls_when_open(self):
        """Test open circuit rejects calls."""
        cb = CircuitBreaker(
            CircuitBreakerConfig(failure_threshold=1),
            name="test",
        )

        # Open the circuit
        with pytest.raises(Exception):
            cb.call(lambda: 1 / 0)

        assert cb.state == CircuitBreakerState.OPEN

        # Subsequent calls should be rejected
        with pytest.raises(Exception, match="Circuit breaker"):
            cb.call(lambda: "success")

    def test_circuit_half_open_recovery(self):
        """Test circuit transitions to half-open for recovery."""
        config = CircuitBreakerConfig(
            failure_threshold=1,
            recovery_timeout=0.001,
        )
        cb = CircuitBreaker(config, name="test")

        # Open circuit
        with pytest.raises(Exception):
            cb.call(lambda: 1 / 0)

        assert cb.state == CircuitBreakerState.OPEN

        # Wait for recovery timeout
        time.sleep(0.002)

        # Should transition to half-open
        result = cb.call(lambda: "success")
        assert result == "success"
        assert cb.state in [CircuitBreakerState.CLOSED, CircuitBreakerState.HALF_OPEN]

    def test_circuit_breaker_stats(self):
        """Test circuit breaker statistics."""
        cb = CircuitBreaker(name="test")
        stats = cb.get_state()

        assert stats["name"] == "test"
        assert stats["state"] == CircuitBreakerState.CLOSED.value
        assert stats["failure_count"] == 0


# ============================================================================
# Rate Limiting Tests
# ============================================================================


class TestRateLimiter:
    """Test rate limiting."""

    def test_rate_limiter_allows_under_limit(self):
        """Test rate limiter allows requests under limit."""
        config = RateLimitConfig(max_requests=10, window_seconds=1.0)
        limiter = RateLimiter(config)

        for _ in range(5):
            assert limiter.acquire() is True

    def test_rate_limiter_blocks_over_limit(self):
        """Test rate limiter blocks requests over limit."""
        config = RateLimitConfig(max_requests=3, window_seconds=1.0)
        limiter = RateLimiter(config)

        # Acquire all tokens
        for _ in range(3):
            assert limiter.acquire() is True

        # Additional request should be blocked
        assert limiter.acquire() is False

    def test_rate_limiter_acquire_or_wait(self):
        """Test acquire_or_wait waits for token."""
        config = RateLimitConfig(max_requests=1, window_seconds=1.0)
        limiter = RateLimiter(config)

        assert limiter.acquire() is True
        assert limiter.acquire_or_wait(max_wait=0.05) is False  # Would need to wait

    def test_rate_limiter_stats(self):
        """Test rate limiter statistics."""
        config = RateLimitConfig(max_requests=10, window_seconds=1.0)
        limiter = RateLimiter(config)

        for _ in range(5):
            limiter.acquire()
        stats = limiter.get_stats()

        assert stats["max_tokens"] == 10
        assert len(limiter.requests_in_window) == 5


# ============================================================================
# Audit Logging Tests
# ============================================================================


class TestAuditLogger:
    """Test audit logging."""

    def test_audit_log_event(self):
        """Test logging an event."""
        logger = AuditLogger()
        logger.log_event(
            event_type="operation",
            action="fetch",
            resource="package",
            status="success",
        )

        events = logger.get_events()
        assert len(events) == 1
        assert events[0]["event_type"] == "operation"
        assert events[0]["status"] == "success"

    def test_audit_log_with_error(self):
        """Test logging event with error."""
        logger = AuditLogger()
        logger.log_event(
            event_type="operation",
            action="fetch",
            resource="package",
            status="failed",
            error="Connection timeout",
        )

        events = logger.get_events()
        assert events[0]["error"] == "Connection timeout"

    def test_audit_log_limit(self):
        """Test audit log limit."""
        logger = AuditLogger()
        for i in range(10):
            logger.log_event(
                event_type="test",
                action="test",
                resource="test",
                status=f"status_{i}",
            )

        events = logger.get_events(limit=5)
        assert len(events) == 5


# ============================================================================
# Error Handler Tests
# ============================================================================


class TestProductionErrorHandler:
    """Test production error handler."""

    def test_handle_error(self):
        """Test handling an error."""
        handler = ProductionErrorHandler()
        error = ValueError("Test error")

        context = handler.handle_error(
            error,
            ErrorCategory.VALIDATION,
            ErrorSeverity.MEDIUM,
        )

        assert context.category == ErrorCategory.VALIDATION
        assert context.severity == ErrorSeverity.MEDIUM
        assert "Test error" in context.message

    def test_circuit_breaker_registration(self):
        """Test circuit breaker registration."""
        handler = ProductionErrorHandler()
        cb = handler.register_circuit_breaker("test_cb")

        assert "test_cb" in handler.circuit_breakers
        assert handler.circuit_breakers["test_cb"] is cb

    def test_rate_limiter_registration(self):
        """Test rate limiter registration."""
        handler = ProductionErrorHandler()
        rl = handler.register_rate_limiter("test_rl")

        assert "test_rl" in handler.rate_limiters
        assert handler.rate_limiters["test_rl"] is rl

    def test_error_stats(self):
        """Test error statistics."""
        handler = ProductionErrorHandler()
        handler.register_circuit_breaker("test_cb")

        stats = handler.get_error_stats()
        assert "total_errors" in stats
        assert "circuit_breakers" in stats
        assert "rate_limiters" in stats


# ============================================================================
# Health Check Tests
# ============================================================================


class TestHealthCheck:
    """Test health checking."""

    def test_health_check_result(self):
        """Test health check result."""
        check = HealthCheck(
            name="test_service",
            status=ServiceHealth.HEALTHY,
            timestamp=time.time(),
            response_time_ms=10.5,
            message="Service healthy",
        )

        assert check.status == ServiceHealth.HEALTHY
        data = check.to_dict()
        assert data["status"] == "healthy"

    def test_service_monitor_registration(self):
        """Test service monitor registration."""
        monitor = ServiceHealthMonitor()

        provider = Mock(spec=HealthCheckProvider)
        provider.check_health.return_value = HealthCheck(
            name="mock",
            status=ServiceHealth.HEALTHY,
            timestamp=time.time(),
            response_time_ms=1.0,
            message="Mock healthy",
        )

        monitor.register_provider("mock", provider)
        assert "mock" in monitor.providers

    def test_overall_health_calculation(self):
        """Test overall health is calculated from services."""
        monitor = ServiceHealthMonitor()

        healthy_provider = Mock(spec=HealthCheckProvider)
        healthy_provider.check_health.return_value = HealthCheck(
            name="healthy",
            status=ServiceHealth.HEALTHY,
            timestamp=time.time(),
            response_time_ms=1.0,
            message="Healthy",
        )

        degraded_provider = Mock(spec=HealthCheckProvider)
        degraded_provider.check_health.return_value = HealthCheck(
            name="degraded",
            status=ServiceHealth.DEGRADED,
            timestamp=time.time(),
            response_time_ms=1.0,
            message="Degraded",
        )

        monitor.register_provider("healthy", healthy_provider)
        monitor.register_provider("degraded", degraded_provider)

        overall = monitor.get_overall_health()
        assert overall == ServiceHealth.DEGRADED


# ============================================================================
# Recovery Manager Tests
# ============================================================================


class TestRecoveryManager:
    """Test recovery manager."""

    def test_recovery_with_retry_success(self):
        """Test recovery with retry succeeds."""
        monitor = ServiceHealthMonitor()
        manager = RecoveryManager(monitor)

        monitor.register_recovery_plan(
            "test_op",
            RecoveryPlan(
                operation="test_op",
                strategy=RecoveryStrategy.RETRY,
                max_retries=3,
            ),
        )

        call_count = 0

        def failing_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Temporary failure")
            return "success"

        success, result = manager.execute_recovery("test_op", failing_operation)
        assert success is True
        assert result == "success"

    def test_recovery_with_fallback(self):
        """Test recovery with fallback."""
        monitor = ServiceHealthMonitor()
        manager = RecoveryManager(monitor)

        monitor.register_recovery_plan(
            "test_op",
            RecoveryPlan(
                operation="test_op",
                strategy=RecoveryStrategy.FALLBACK,
                fallback_handler=lambda: "fallback_result",
            ),
        )

        def failing_operation():
            raise ConnectionError("Primary failed")

        success, result = manager.execute_recovery("test_op", failing_operation)
        assert success is True
        assert result == "fallback_result"

    def test_recovery_history(self):
        """Test recovery history tracking."""
        monitor = ServiceHealthMonitor()
        manager = RecoveryManager(monitor)

        monitor.register_recovery_plan(
            "test_op",
            RecoveryPlan(
                operation="test_op",
                strategy=RecoveryStrategy.RETRY,
                max_retries=1,
            ),
        )

        def failing_operation():
            raise Exception("Failed")

        try:
            manager.execute_recovery("test_op", failing_operation)
        except Exception:
            pass

        history = manager.get_recovery_history()
        assert len(history) > 0


# ============================================================================
# Graceful Shutdown Tests
# ============================================================================


class TestGracefulShutdown:
    """Test graceful shutdown."""

    def test_shutdown_handlers_called(self):
        """Test shutdown handlers are called."""
        shutdown = GracefulShutdown()
        called = []

        def handler1():
            called.append(1)

        def handler2():
            called.append(2)

        shutdown.register_handler(handler1)
        shutdown.register_handler(handler2)
        shutdown.execute_shutdown()

        assert 1 in called
        assert 2 in called
        # Should be called in LIFO order
        assert called[-1] == 1

    def test_shutdown_continues_on_handler_error(self):
        """Test shutdown continues even if handler raises."""
        shutdown = GracefulShutdown()
        called = []

        def failing_handler():
            raise Exception("Handler failed")

        def success_handler():
            called.append("success")

        shutdown.register_handler(failing_handler)
        shutdown.register_handler(success_handler)
        shutdown.execute_shutdown()  # Should not raise

        assert "success" in called


# ============================================================================
# Operations Guide Tests
# ============================================================================


class TestOperationsGuide:
    """Test operations guide."""

    def test_list_runbooks(self):
        """Test listing available runbooks."""
        runbooks = OperationsGuide.list_runbooks()
        assert len(runbooks) > 0
        assert "high_memory_usage" in runbooks

    def test_get_runbook(self):
        """Test getting specific runbook."""
        runbook = OperationsGuide.get_runbook("high_memory_usage")
        assert runbook is not None
        assert "steps" in runbook
        assert len(runbook["steps"]) > 0

    def test_get_nonexistent_runbook(self):
        """Test getting nonexistent runbook."""
        runbook = OperationsGuide.get_runbook("nonexistent")
        assert runbook is None

    def test_print_guide(self):
        """Test printing operations guide."""
        guide = OperationsGuide.print_guide()
        assert isinstance(guide, str)
        assert len(guide) > 0
        assert "HIGH_MEMORY_USAGE" in guide


# ============================================================================
# Integration Tests
# ============================================================================


class TestProductionSystemIntegration:
    """Integration tests for production systems."""

    def test_circuit_breaker_with_retry(self):
        """Test circuit breaker with retry logic."""
        cb = CircuitBreaker(
            CircuitBreakerConfig(failure_threshold=3),
            name="test",
        )

        call_count = 0

        @retry_with_backoff(RetryConfig(max_attempts=5, initial_delay=0.001))
        def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Temporary")
            return "success"

        # Should succeed even with retries
        result = cb.call(operation)
        assert result == "success"

    def test_rate_limiter_with_handler(self):
        """Test rate limiter with error handler."""
        handler = ProductionErrorHandler()
        rl = handler.register_rate_limiter(
            "test",
            RateLimitConfig(max_requests=2, window_seconds=1.0),
        )

        # Use up tokens
        assert rl.acquire() is True
        assert rl.acquire() is True
        assert rl.acquire() is False

        # Verify stats are tracked
        stats = handler.get_error_stats()
        assert "rate_limiters" in stats

    def test_full_error_handling_flow(self):
        """Test full error handling flow."""
        handler = ProductionErrorHandler()
        monitor = ServiceHealthMonitor()
        recovery_manager = RecoveryManager(monitor)

        # Register recovery plan
        monitor.register_recovery_plan(
            "operation",
            RecoveryPlan(
                operation="operation",
                strategy=RecoveryStrategy.RETRY,
                max_retries=2,
            ),
        )

        call_count = 0

        def operation():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ConnectionError("Network error")
            return "success"

        # Execute with recovery
        success, result = recovery_manager.execute_recovery("operation", operation)
        assert success is True
        assert result == "success"

        # Check audit log
        audit_log = handler.get_audit_log()
        # Should have logged something
        assert isinstance(audit_log, list)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
