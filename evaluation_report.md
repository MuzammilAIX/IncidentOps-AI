# IncidentOps-AI Evaluation Report

- Total scenarios: 3
- Passed: 3
- Root cause accuracy: 3/3 (100%)

## Results

| Scenario | Expected | Actual | Correct | Confidence | Latency | Runbooks |
|----------|----------|--------|---------|------------|---------|----------|
| container_crash | container_oom_killed | There is a sudden increase in traffic that exceeds the API's capacity. | PASS | 80% | 12.67s | RB-101, RB-102, RB-103 |
| high_cpu | cpu_saturation | CPU saturation is caused by a recent code deployment introducing inefficient alg | PASS | 70% | 13.82s | RB-104, RB-101, RB-103 |
| memory_leak | memory_leak | There is a memory leak in the notification worker code. | PASS | 90% | 12.39s | RB-102 |

## Detailed Results

### container_crash

- Expected: container_oom_killed
- Actual: There is a sudden increase in traffic that exceeds the API's capacity.
- Match: keyword:capacity
- Confidence: 80%
- Latency: 12.67s
- Runbooks: RB-101, RB-102, RB-103
- Reasoning: The evidence of the container being OOM-killed during high traffic strongly supports the hypothesis of traffic exceeding capacity. While memory limits may also be a factor, the immediate cause appears

### high_cpu

- Expected: cpu_saturation
- Actual: CPU saturation is caused by a recent code deployment introducing inefficient algorithms.
- Match: keyword:cpu saturation
- Confidence: 70%
- Latency: 13.82s
- Runbooks: RB-104, RB-101, RB-103
- Reasoning: The high CPU usage and latency spike align with the possibility of inefficient algorithms introduced in a recent deployment. While a spike in requests could also contribute, there is no evidence of in

### memory_leak

- Expected: memory_leak
- Actual: There is a memory leak in the notification worker code.
- Match: keyword:memory leak
- Confidence: 90%
- Latency: 12.39s
- Runbooks: RB-102
- Reasoning: The evidence strongly supports the presence of a memory leak due to the consistent high memory usage and growth rate, along with multiple restarts indicating crashes from memory exhaustion.
