import time
from typing import Dict


class MetricsCollector:
    def __init__(self) -> None:
        self._metrics: Dict[str, float] = {}

    def StartTimer(self, key: str) -> None:
        self._metrics[key] = time.perf_counter()

    def StopTimer(self, key: str) -> float:
        if key not in self._metrics:
            raise ValueError(f"Timer '{key}' was not started.")

        duration: float = time.perf_counter() - self._metrics[key]
        self._metrics[key] = duration
        return duration

    def GetMetric(self, key: str) -> float:
        if key not in self._metrics:
            raise ValueError(f"Metric '{key}' not found.")

        return self._metrics[key]

    def Reset(self) -> None:
        self._metrics.clear()


class RequestMetrics:
    def __init__(self) -> None:
        self.collector: MetricsCollector = MetricsCollector()

    def StartQuery(self) -> None:
        self.collector.StartTimer("query_latency")

    def EndQuery(self) -> float:
        return self.collector.StopTimer("query_latency")

    def StartRetrieval(self) -> None:
        self.collector.StartTimer("retrieval_time")

    def EndRetrieval(self) -> float:
        return self.collector.StopTimer("retrieval_time")

    def StartLLM(self) -> None:
        self.collector.StartTimer("llm_response_time")

    def EndLLM(self) -> float:
        return self.collector.StopTimer("llm_response_time")

    def GetAllMetrics(self) -> Dict[str, float]:
        return {
            "query_latency": self.collector.GetMetric("query_latency"),
            "retrieval_time": self.collector.GetMetric("retrieval_time"),
            "llm_response_time": self.collector.GetMetric("llm_response_time"),
        }