import logging

import structlog
from fastapi import FastAPI
from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ALWAYS_ON, TraceIdRatioBased

from config.base import OpenTelemetryConfig

logger = structlog.get_logger(__name__)


class OpenTelemetry:
    _instance: "OpenTelemetry | None" = None
    _initialized: bool = False
    _tracer_provider: TracerProvider | None = None
    _meter_provider: MeterProvider | None = None
    _logger_provider: LoggerProvider | None = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def _create_resource(self, config: OpenTelemetryConfig) -> Resource:
        return Resource.create(
            {
                "service.name": config.service_name,
                "deployment.environment": config.environment,
            }
        )

    def _instrument_traces(
        self, resource: Resource, config: OpenTelemetryConfig
    ) -> None:
        sampler = (
            ALWAYS_ON
            if config.sampling_rate >= 1.0
            else TraceIdRatioBased(config.sampling_rate)
        )
        self._tracer_provider = TracerProvider(resource=resource, sampler=sampler)
        exporter = OTLPSpanExporter(endpoint=config.otlp_endpoint, insecure=True)
        self._tracer_provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(self._tracer_provider)

    def _instrument_metrics(
        self, resource: Resource, config: OpenTelemetryConfig
    ) -> None:
        exporter = OTLPMetricExporter(endpoint=config.otlp_endpoint, insecure=True)
        reader = PeriodicExportingMetricReader(exporter, export_interval_millis=15000)
        self._meter_provider = MeterProvider(resource=resource, metric_readers=[reader])
        metrics.set_meter_provider(self._meter_provider)

    def _instrument_logging(
        self, resource: Resource, config: OpenTelemetryConfig
    ) -> None:
        self._logger_provider = LoggerProvider(resource=resource)
        set_logger_provider(self._logger_provider)

        log_exporter = OTLPLogExporter(endpoint=config.otlp_endpoint, insecure=True)
        self._logger_provider.add_log_record_processor(
            BatchLogRecordProcessor(log_exporter)
        )
        handler = LoggingHandler(
            level=logging.NOTSET, logger_provider=self._logger_provider
        )
        logging.getLogger().addHandler(handler)

        LoggingInstrumentor().instrument(set_logging_format=False)

    def instrument(self, app: FastAPI, config: OpenTelemetryConfig) -> None:
        if not config.enabled:
            logger.info("otel_disabled")
            return

        if self._initialized:
            logger.info("otel_already_initialized")
            return

        try:
            resource = self._create_resource(config)
            self._instrument_traces(resource, config)
            self._instrument_metrics(resource, config)
            self._instrument_logging(resource, config)

            FastAPIInstrumentor.instrument_app(app)
            SQLAlchemyInstrumentor().instrument()

            self._initialized = True
            logger.info("otel_initialized")
        except Exception as e:
            logger.error("otel_initialization_failed", error=str(e))

    def shutdown(self) -> None:
        if not self._initialized:
            return

        if self._tracer_provider:
            self._tracer_provider.shutdown()
        if self._meter_provider:
            self._meter_provider.shutdown()
        if self._logger_provider:
            self._logger_provider.shutdown()

        logger.info("otel_shutdown")
