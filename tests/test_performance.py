"""Performance and resource latency benchmarking suite (CA-19)."""

import time
import statistics


def test_request_latency_benchmarks(client):
    """Benchmark request latency across public, authenticated, and analytical endpoints."""
    # 1. Health liveness route latency (50 samples)
    health_times = []
    for _ in range(50):
        start = time.perf_counter()
        resp = client.get("/health")
        duration_ms = (time.perf_counter() - start) * 1000
        assert resp.status_code == 200
        health_times.append(duration_ms)

    avg_health = statistics.mean(health_times)
    median_health = statistics.median(health_times)

    # 2. Authenticated analytics route latency (25 samples)
    client.post("/login", data={"username": "admin", "password": "admin123"})
    analytics_times = []
    for _ in range(25):
        start = time.perf_counter()
        resp = client.get("/analytics")
        duration_ms = (time.perf_counter() - start) * 1000
        assert resp.status_code == 200
        analytics_times.append(duration_ms)

    avg_analytics = statistics.mean(analytics_times)
    median_analytics = statistics.median(analytics_times)

    # Acceptance criteria assertions: responsive local execution (< 150ms per request)
    assert avg_health < 150.0, f"Average health latency too high: {avg_health:.2f}ms"
    assert avg_analytics < 250.0, f"Average analytics latency too high: {avg_analytics:.2f}ms"

    print(f"\n[BENCHMARK] /health - Avg: {avg_health:.2f}ms, Median: {median_health:.2f}ms")
    print(f"[BENCHMARK] /analytics - Avg: {avg_analytics:.2f}ms, Median: {median_analytics:.2f}ms")

