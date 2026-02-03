import logging
from typing import Optional

from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from src.config import OpenTelemetryConfig

from . import StructLogger

logger = StructLogger()


class OpenTelemetry:
    _instance: Optional["OpenTelemetry"] = None
    _initialized: bool = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(OpenTelemetry, cls).__new__(cls)
        return cls._instance

    def instrument_logging(self, resource: Resource, otlp_endpoint: str):
        logger_provider = LoggerProvider(resource=resource)
        set_logger_provider(logger_provider)

        logger_exporter = OTLPLogExporter(endpoint=otlp_endpoint)
        logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(logger_exporter)
        )
        handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)
        logging.getLogger().addHandler(handler)

    def instrument(self, app: FastAPI, config: OpenTelemetryConfig):
        if self._initialized:
            logger.info("OpenTelemetry instrumentation already initialized")
            return

        try:
            resource = Resource.create(
                {
                    "service.name": config.service_name,
                    "deployment.environment": config.environment,
                }
            )
            tracer_provider = TracerProvider(resource=resource)

            otlp_exporter = OTLPSpanExporter(endpoint=config.otlp_endpoint)
            span_processor = BatchSpanProcessor(otlp_exporter)
            tracer_provider.add_span_processor(span_processor)

            trace.set_tracer_provider(tracer_provider)

            self.instrument_logging(
                resource=resource, otlp_endpoint=config.otlp_endpoint
            )

            FastAPIInstrumentor.instrument_app(app)

            self._initialized = True
            logger.info("OpenTelemetry instrumentation initialized")
        except Exception as e:
            logger.error(f"Failed to initialize OpenTelemetry instrumentation: {e}")
