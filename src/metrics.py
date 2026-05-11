from prometheus_client import Counter, Histogram, Gauge

# Request metrics
request_count = Counter(
    "lru_kr_requests_total",
    "Total number of requests",
    ["method", "endpoint", "status"],
)

request_duration = Histogram(
    "lru_kr_request_duration_seconds",
    "Request duration in seconds",
    ["method", "endpoint"],
)

# Cache metrics
cache_hits = Counter(
    "lru_kr_cache_hits_total",
    "Total number of cache hits",
    ["cache_type"],
)

cache_misses = Counter(
    "lru_kr_cache_misses_total",
    "Total number of cache misses",
    ["cache_type"],
)

cache_size = Gauge(
    "lru_kr_cache_size",
    "Current cache size",
    ["cache_type"],
)

# Key generation metrics
key_generation_attempts = Histogram(
    "lru_kr_key_generation_attempts",
    "Number of attempts to generate a unique key",
    ["key_type"],
)

key_collisions = Counter(
    "lru_kr_key_collisions_total",
    "Total number of key collisions",
    ["key_type"],
)

# Redis metrics
redis_operation_duration = Histogram(
    "lru_kr_redis_operation_duration_seconds",
    "Redis operation duration in seconds",
    ["operation"],
)

# QR code metrics
qr_generation_duration = Histogram(
    "lru_kr_qr_generation_duration_seconds",
    "QR code generation duration in seconds",
)
