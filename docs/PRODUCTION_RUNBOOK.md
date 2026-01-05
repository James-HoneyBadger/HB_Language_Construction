# Production Operations Runbook

## Overview

This document provides operational procedures, troubleshooting guides, and best practices for running ParserCraft Phase 5-7 in production.

## System Architecture

### Core Components
- **AST Integration**: AST parsing, code generation (C/WASM), type inference
- **Protocol Type Integration**: Structural typing, protocol conformance, type compatibility
- **LSP Features Integration**: IDE support (formatting, completion, refactoring)
- **Package Registry**: Remote package management with caching and dependencies
- **Error Handling**: Production error handling with retry, circuit breaker, rate limiting
- **Operations**: Health monitoring, recovery management, audit logging

### Critical Dependencies
- Python 3.13.11
- Type hints and static analysis (mypy, Pylance)
- Network connectivity for registry operations

## System Health Monitoring

### Health Check Endpoints

```python
from src.hb_lcs.phase5_error_handling import Phase5ErrorHandlingSystem

system = Phase5ErrorHandlingSystem()
health = system.get_health_summary()
# Returns: overall_status, services[], timestamps, response_times
```

### Health Status Levels

| Status | Meaning | Action |
|--------|---------|--------|
| HEALTHY | All systems operational | Continue normal operation |
| DEGRADED | Some systems impaired | Monitor, may have reduced performance |
| UNHEALTHY | Critical systems down | Immediate investigation required |

### Checking Individual Service Health

```python
# Check AST integration
ast_check = monitor.check_all()['ast_integration']
print(f"AST: {ast_check.status.value} ({ast_check.response_time_ms}ms)")

# Check Registry
registry_check = monitor.check_all()['registry']
print(f"Registry: {registry_check.status.value}")

# Check LSP
lsp_check = monitor.check_all()['lsp_integration']
print(f"LSP: {lsp_check.status.value}")
```

## Common Issues and Solutions

### Issue 1: High Memory Usage

**Symptoms:**
- Process using excessive RAM
- Slow response times
- Out of memory errors

**Root Causes:**
- Large AST parsing operations
- Cache growth without eviction
- Type inference on huge codebases

**Steps to Resolve:**
1. Check memory usage: `ps aux | grep python`
2. Review active operations in audit log
3. Check cache sizes:
   ```python
   stats = error_handler.get_error_stats()
   # Review cache statistics
   ```
4. Consider implementing:
   - Cache size limits
   - Periodic cache clearing
   - Request batching
5. Restart service if necessary

**Prevention:**
- Monitor memory trends
- Set cache TTL values
- Implement garbage collection
- Profile large operations

### Issue 2: Slow Response Times

**Symptoms:**
- Operations taking longer than expected
- Timeouts occurring
- IDE responsiveness degraded

**Root Causes:**
- Network latency to registry
- Large type inference operations
- Unoptimized AST processing

**Steps to Resolve:**
1. Check service health: `system.get_health_summary()`
2. Review response times in audit logs:
   ```python
   logs = error_handler.get_audit_log(limit=20)
   for log in logs:
       print(f"{log['event_type']}: {log['timestamp']} - {log['status']}")
   ```
3. Check rate limiter stats:
   ```python
   stats = rate_limiter.get_stats()
   print(f"Requests in window: {stats['requests_in_window']}")
   ```
4. Enable query caching for registry
5. Consider increasing timeouts:
   ```python
   config = RateLimitConfig(timeout_ms=10000)  # 10 seconds
   ```

**Prevention:**
- Implement connection pooling
- Cache type inference results
- Monitor baseline response times
- Set up alerts for regressions

### Issue 3: Circuit Breaker Opened

**Symptoms:**
- Circuit breaker status is OPEN
- Registry requests being rejected
- "Circuit breaker is OPEN" errors

**Root Causes:**
- Network connectivity issues
- Registry service down
- Too many consecutive failures

**Steps to Resolve:**
1. Check circuit breaker state:
   ```python
   cb_state = error_handler.circuit_breakers['registry_fetch'].get_state()
   print(f"State: {cb_state['state']}")
   print(f"Failures: {cb_state['failure_count']}")
   ```
2. Verify registry service health
3. Check network connectivity: `ping registry.example.com`
4. Review recent errors in audit log
5. Wait for automatic recovery (default: 60 seconds)
6. Monitor for recovery:
   ```python
   time.sleep(60)
   cb_state = error_handler.circuit_breakers['registry_fetch'].get_state()
   # Should be HALF_OPEN or CLOSED
   ```

**Prevention:**
- Monitor circuit breaker state continuously
- Implement redundant registry servers
- Use DNS failover
- Set up alerts for circuit breaker opens

### Issue 4: Rate Limiting Active

**Symptoms:**
- "Rate limit exceeded" errors
- Requests being queued
- Service throughput reduced

**Root Causes:**
- Too many concurrent requests
- Thundering herd pattern
- Insufficient rate limit configuration

**Steps to Resolve:**
1. Check rate limiter stats:
   ```python
   rl = error_handler.rate_limiters['registry_query']
   stats = rl.get_stats()
   print(f"Requests in window: {stats['requests_in_window']}")
   print(f"Available tokens: {stats['available_tokens']}")
   ```
2. Analyze request pattern
3. Options:
   - Increase rate limit: `RateLimitConfig(max_requests=1000)`
   - Implement request batching
   - Add exponential backoff to client
4. Monitor for herd behavior:
   ```python
   # Check if requests are bursty
   cutoff = time.time() - 60
   recent = [t for t in limiter.requests_in_window if t > cutoff]
   ```

**Prevention:**
- Set rate limits based on capacity testing
- Implement client-side request batching
- Use jitter in retry logic
- Monitor request distribution

### Issue 5: Persistent Errors

**Symptoms:**
- Errors keep occurring despite retries
- Recovery attempts failing
- Error rate not decreasing

**Root Causes:**
- Fundamental service issue
- Data corruption
- Incompatible versions

**Steps to Resolve:**
1. Collect error context:
   ```python
   error_stats = error_handler.get_error_stats()
   audit_log = error_handler.get_audit_log(limit=100)
   ```
2. Analyze error categories:
   ```python
   by_category = {}
   for ctx in error_handler.error_contexts:
       cat = ctx.category.value
       by_category[cat] = by_category.get(cat, 0) + 1
   ```
3. Check dependency versions
4. Review recent deployments
5. Consider manual intervention

**Prevention:**
- Run pre-deployment tests
- Monitor error trends
- Set up alerts for error rate increases
- Keep detailed change logs

## Performance Monitoring

### Performance Baselines

These are established Phase 6 performance targets:

| Operation | Target | Optimized |
|-----------|--------|-----------|
| AST parsing (100 statements) | <2ms | <1ms |
| Type inference (50 vars) | ~5ms | <1ms (cached) |
| Protocol check (10 protocols) | ~5ms | <2ms (memoized) |
| Registry fetch (cached) | <1ms | <10μs (TTL cached) |
| LSP formatting | <2ms | <2ms |
| LSP completion (100 symbols) | <50ms | <50ms |

### Monitoring Queries

```python
# Get performance stats
health_summary = monitor.get_health_summary()
for service, check in health_summary['services'].items():
    print(f"{service}: {check['response_time_ms']}ms")

# Track trends
history = monitor.get_health_history('registry', limit=100)
response_times = [h['response_time_ms'] for h in history]
avg_time = sum(response_times) / len(response_times)
max_time = max(response_times)
print(f"Average: {avg_time}ms, Max: {max_time}ms")
```

### Setting Performance Alerts

```python
def check_performance_threshold():
    history = monitor.get_health_history('ast_integration', limit=10)
    avg = sum(h['response_time_ms'] for h in history) / len(history)
    
    if avg > 5.0:  # 5ms threshold
        logger.warning(f"AST performance degrading: {avg}ms average")
        # Trigger investigation
```

## Capacity Planning

### Load Testing

Conduct regular load tests to ensure capacity:

```python
import concurrent.futures

def load_test(num_concurrent=10, duration_seconds=60):
    """Simulate concurrent operations."""
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = []
        start = time.time()
        
        while time.time() - start < duration_seconds:
            futures.append(executor.submit(perform_operation))
        
        results = [f.result() for f in concurrent.futures.as_completed(futures)]
        return results
```

### Capacity Thresholds

| Resource | Warning Level | Critical Level |
|----------|---------------|-----------------|
| Memory | 70% | 90% |
| CPU | 80% | 95% |
| Connections | 80% | 95% |
| Queue depth | 100 items | 500 items |

## Graceful Shutdown

### Shutdown Procedure

```python
from src.hb_lcs.production_operations import GracefulShutdown

shutdown = GracefulShutdown()

# Register cleanup handlers (in reverse execution order)
shutdown.register_handler(close_registry_connections)
shutdown.register_handler(flush_audit_logs)
shutdown.register_handler(save_cache_state)

# Execute graceful shutdown
shutdown.execute_shutdown()
# System will close in-flight requests and clean up
```

### Pre-shutdown Checklist

1. Stop accepting new requests
2. Wait for in-flight requests to complete (with timeout)
3. Flush audit logs
4. Close database connections
5. Save cache state
6. Close network sockets
7. Exit cleanly

## Disaster Recovery

### Backup Strategy

```python
# Backup registry cache
import json

cache_backup = {
    'timestamp': time.time(),
    'cache_stats': registry.get_cache_stats(),
    'packages': registry.get_cached_packages(),
}

with open('cache_backup.json', 'w') as f:
    json.dump(cache_backup, f)
```

### Recovery from Cache Loss

```python
# Recovery procedure
registry = RemotePackageRegistry()

# 1. Restore from backup if available
if os.path.exists('cache_backup.json'):
    with open('cache_backup.json', 'r') as f:
        backup = json.load(f)
    # Restore packages
    for pkg in backup['packages']:
        registry.cache[pkg['name']] = pkg

# 2. Verify critical packages can be fetched
for pkg_name in CRITICAL_PACKAGES:
    try:
        registry.fetch_package(pkg_name)
    except Exception as e:
        logger.error(f"Failed to fetch {pkg_name}: {e}")
        # May need to rebuild from scratch
```

### Data Corruption Recovery

```python
def verify_data_integrity():
    """Verify critical data structures."""
    issues = []
    
    # Check AST cache
    for node in ast_cache.values():
        if not node.validate():
            issues.append(f"Invalid AST node: {node.id}")
    
    # Check type system
    for type_def in type_system.all_types():
        if not type_def.is_valid():
            issues.append(f"Invalid type: {type_def.name}")
    
    if issues:
        logger.error(f"Data integrity issues found: {issues}")
        # May need to clear cache and rebuild
        clear_all_caches()
    
    return len(issues) == 0
```

## Deployment Procedures

### Pre-deployment Checklist

- [ ] All tests passing (Phase 5-7)
- [ ] Performance baselines met
- [ ] No breaking API changes
- [ ] Documentation updated
- [ ] Audit log configured
- [ ] Monitoring configured
- [ ] Rollback procedure prepared

### Deployment Steps

1. **Staging Deployment**
   ```bash
   # Deploy to staging
   ./deploy.sh staging
   # Run smoke tests
   pytest tests/test_smoke.py
   ```

2. **Production Deployment**
   ```bash
   # Create backup
   cp -r data data.backup.$(date +%s)
   
   # Deploy
   ./deploy.sh production
   
   # Verify health
   curl http://service/health
   ```

3. **Verification**
   ```python
   monitor.check_all()  # Should all be HEALTHY
   ```

### Rollback Procedure

```bash
# If issues detected within 5 minutes
./rollback.sh

# Verify rolled back version
curl http://service/health
```

## Monitoring and Alerting

### Key Metrics to Monitor

1. **Availability**
   - Service uptime
   - Health status
   - Circuit breaker state

2. **Performance**
   - Response times (by operation)
   - Error rate
   - Throughput

3. **Resource Usage**
   - Memory consumption
   - CPU usage
   - Network I/O

4. **Business Metrics**
   - Package resolution time
   - IDE responsiveness
   - Error-free operations percentage

### Alert Thresholds

```python
ALERT_THRESHOLDS = {
    'ast_response_time_ms': 10.0,        # >10ms warning
    'protocol_check_time_ms': 10.0,      # >10ms warning
    'registry_fetch_time_ms': 5000.0,    # >5s warning
    'circuit_breaker_open': True,         # Immediately alert
    'error_rate': 0.01,                   # >1% error rate
    'memory_usage_pct': 80.0,             # >80% memory
    'cpu_usage_pct': 80.0,                # >80% CPU
}
```

## Support and Escalation

### Level 1 Support (Automated)

- Monitor health status
- Check circuit breaker state
- Review recent audit logs
- Attempt automatic recovery

### Level 2 Support (On-Call)

- Analyze error patterns
- Check resource utilization
- Review performance metrics
- Coordinate with Level 1

### Level 3 Support (Engineering)

- Deep code analysis
- Database inspection
- Version investigation
- Performance profiling

### Escalation Path

```
Health Status UNHEALTHY
    ↓
L1: Automated recovery attempt
    ↓
    ├─ Success? → Log and continue
    └─ Failure? → Alert L2
        ↓
        L2: Manual diagnosis
        ↓
        ├─ Root cause found? → Implement fix
        └─ Complex issue? → Escalate to L3
            ↓
            L3: Deep investigation and resolution
```

## Performance Tuning

### Optimization Opportunities

1. **AST Processing**
   - Implement incremental parsing
   - Cache parse results
   - Parallelize type inference

2. **Type System**
   - Cache type checking results
   - Implement type narrowing
   - Use generic specialization

3. **Registry**
   - Increase TTL for stable packages
   - Implement batch fetching
   - Use compression for large packages

4. **LSP**
   - Cache symbol tables
   - Implement incremental analysis
   - Use semantic tokenization

### Configuration Tuning

```python
# Production-optimized configuration
PRODUCTION_CONFIG = {
    'ast_cache_size': 10000,
    'type_inference_cache_ttl': 3600,
    'registry_cache_ttl': 86400,
    'registry_batch_size': 100,
    'circuit_breaker_threshold': 10,
    'rate_limit_window': 60,
    'rate_limit_requests': 5000,
    'audit_log_retention': 7,  # days
    'health_check_interval': 30,  # seconds
}
```

## References

- [Error Handling](../src/hb_lcs/production_error_handling.py)
- [Operations](../src/hb_lcs/production_operations.py)
- [Phase 5 Integration](../src/hb_lcs/phase5_error_handling.py)
- [Test Suite](../tests/test_phase7_production.py)

## Revision History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-05 | Initial production runbook |
