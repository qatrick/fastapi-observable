import pyroscope
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from .config import settings
import logging

logger = logging.getLogger("app.observability")

def setup_tracing():
    resource = Resource(attributes={
        "service.name": settings.APP_NAME,
        "deployment.environment": settings.ENV,
        "k8s.pod.name": settings.POD_NAME
    })
    provider = TracerProvider(resource=resource)
    otlp_exporter = OTLPSpanExporter(endpoint=settings.TEMPO_ENDPOINT, insecure=True)
    provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
    trace.set_tracer_provider(provider)
    logger.info(f"Tracing enabled -> {settings.TEMPO_ENDPOINT}")

def setup_profiling():
    app_identifier = f"{settings.APP_NAME}.{settings.ENV}"
    pyroscope.configure(
        application_name=app_identifier,
        server_address=settings.PYROSCOPE_SERVER_ADDRESS,
        tags={"pod": settings.POD_NAME}
    )
    logger.info(f"Profiling enabled -> {settings.PYROSCOPE_SERVER_ADDRESS}")