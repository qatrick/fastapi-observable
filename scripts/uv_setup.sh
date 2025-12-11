# 1. 初始化
uv init
# 2. 安裝核心依賴
uv add fastapi uvicorn pydantic-settings
# 3. 安裝 Observability 依賴
uv add opentelemetry-api opentelemetry-sdk opentelemetry-instrumentation-fastapi opentelemetry-exporter-otlp opentelemetry-exporter-prometheus
uv add python-json-logger pyroscope-io
# 4. 安裝測試依賴
uv add --dev locust