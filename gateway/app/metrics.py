"""
Metrics collection for monitoring (Prometheus/StatsD compatible)
"""
import time
import threading
from typing import Dict, Any
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class MetricsCollector:
    """
    Collect application metrics.

    Metrics:
    - Counters (incrementing values)
    - Gauges (current values)
    - Histograms (distribution of values)
    - Timers (duration measurements)
    """

    def __init__(self):
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = {}
        self.histograms: Dict[str, list] = defaultdict(list)
        self.lock = threading.Lock()

    def increment(self, metric: str, value: int = 1, labels: Dict[str, str] = None):
        """
        Increment a counter metric.

        Args:
            metric: Metric name
            value: Value to add
            labels: Optional labels (e.g., {'status': '200'})
        """
        key = self._build_key(metric, labels)
        with self.lock:
            self.counters[key] += value

    def set_gauge(self, metric: str, value: float, labels: Dict[str, str] = None):
        """
        Set a gauge metric.

        Args:
            metric: Metric name
            value: Current value
            labels: Optional labels
        """
        key = self._build_key(metric, labels)
        with self.lock:
            self.gauges[key] = value

    def observe(self, metric: str, value: float, labels: Dict[str, str] = None):
        """
        Observe a value for histogram metric.

        Args:
            metric: Metric name
            value: Observed value
            labels: Optional labels
        """
        key = self._build_key(metric, labels)
        with self.lock:
            self.histograms[key].append(value)

            # Keep only last 1000 observations to prevent memory growth
            if len(self.histograms[key]) > 1000:
                self.histograms[key] = self.histograms[key][-1000:]

    def timer(self, metric: str, labels: Dict[str, str] = None):
        """
        Context manager for timing operations.

        Usage:
            with metrics.timer('api.generate'):
                # ... operation ...
                pass
        """
        return MetricTimer(self, metric, labels)

    def _build_key(self, metric: str, labels: Dict[str, str] = None) -> str:
        """Build metric key with labels"""
        if not labels:
            return metric

        label_str = ','.join(f'{k}={v}' for k, v in sorted(labels.items()))
        return f'{metric}{{{label_str}}}'

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get all metrics in Prometheus-compatible format.

        Returns:
            Dictionary of metrics
        """
        with self.lock:
            metrics = {
                'counters': dict(self.counters),
                'gauges': dict(self.gauges),
                'histograms': {}
            }

            # Calculate histogram statistics
            for key, values in self.histograms.items():
                if values:
                    sorted_values = sorted(values)
                    n = len(sorted_values)

                    metrics['histograms'][key] = {
                        'count': n,
                        'sum': sum(sorted_values),
                        'min': sorted_values[0],
                        'max': sorted_values[-1],
                        'avg': sum(sorted_values) / n,
                        'p50': sorted_values[int(n * 0.5)],
                        'p95': sorted_values[int(n * 0.95)],
                        'p99': sorted_values[int(n * 0.99)]
                    }

            return metrics

    def get_prometheus_format(self) -> str:
        """
        Export metrics in Prometheus text format.

        Returns:
            Metrics in Prometheus exposition format
        """
        lines = []
        metrics = self.get_metrics()

        # Counters
        for key, value in metrics['counters'].items():
            lines.append(f'# TYPE {key.split("{")[0]} counter')
            lines.append(f'{key} {value}')

        # Gauges
        for key, value in metrics['gauges'].items():
            lines.append(f'# TYPE {key.split("{")[0]} gauge')
            lines.append(f'{key} {value}')

        # Histograms
        for key, stats in metrics['histograms'].items():
            base_key = key.split("{")[0]
            labels_part = key[len(base_key):]

            lines.append(f'# TYPE {base_key} histogram')
            lines.append(f'{base_key}_count{labels_part} {stats["count"]}')
            lines.append(f'{base_key}_sum{labels_part} {stats["sum"]}')
            lines.append(f'{base_key}_min{labels_part} {stats["min"]}')
            lines.append(f'{base_key}_max{labels_part} {stats["max"]}')
            lines.append(f'{base_key}_avg{labels_part} {stats["avg"]}')

        return '\n'.join(lines) + '\n'

    def reset(self):
        """Reset all metrics"""
        with self.lock:
            self.counters.clear()
            self.gauges.clear()
            self.histograms.clear()


class MetricTimer:
    """Context manager for timing operations"""

    def __init__(self, collector: MetricsCollector, metric: str, labels: Dict[str, str] = None):
        self.collector = collector
        self.metric = metric
        self.labels = labels
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        self.collector.observe(f'{self.metric}_duration_seconds', duration, self.labels)


# Global metrics collector
metrics = MetricsCollector()


# Application-specific metrics
def record_generation_started():
    """Record image generation started"""
    metrics.increment('pod_generation_started_total')


def record_generation_completed(duration_seconds: float, batch_size: int = 1):
    """Record image generation completed"""
    metrics.increment('pod_generation_completed_total')
    metrics.observe('pod_generation_duration_seconds', duration_seconds)
    metrics.set_gauge('pod_last_generation_batch_size', batch_size)


def record_generation_failed(error_type: str = 'unknown'):
    """Record image generation failed"""
    metrics.increment('pod_generation_failed_total', labels={'error_type': error_type})


def record_image_approved():
    """Record image approved"""
    metrics.increment('pod_images_approved_total')


def record_image_rejected():
    """Record image rejected"""
    metrics.increment('pod_images_rejected_total')


def record_product_published(platform: str):
    """Record product published"""
    metrics.increment('pod_products_published_total', labels={'platform': platform})


def record_product_failed(platform: str, error_type: str = 'unknown'):
    """Record product publish failed"""
    metrics.increment('pod_products_failed_total', labels={'platform': platform, 'error_type': error_type})


def record_api_request(method: str, endpoint: str, status_code: int, duration_seconds: float):
    """Record API request"""
    metrics.increment('pod_api_requests_total', labels={
        'method': method,
        'endpoint': endpoint,
        'status': str(status_code)
    })
    metrics.observe('pod_api_request_duration_seconds', duration_seconds, labels={
        'method': method,
        'endpoint': endpoint
    })


def set_queue_size(queue_name: str, size: int):
    """Set queue size gauge"""
    metrics.set_gauge('pod_queue_size', size, labels={'queue': queue_name})
