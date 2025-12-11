import logging
from pythonjsonlogger import jsonlogger
from opentelemetry import trace

class OTelJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super(OTelJsonFormatter, self).add_fields(log_record, record, message_dict)
        
        span = trace.get_current_span()
        if span != trace.INVALID_SPAN:
            ctx = span.get_span_context()
            log_record['trace_id'] = format(ctx.trace_id, '032x')
            log_record['span_id'] = format(ctx.span_id, '016x')
        else:
            log_record['trace_id'] = None
        
        log_record['service'] = record.name

def setup_logging(service_name: str, environment: str):
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = OTelJsonFormatter(
        '%(timestamp)s %(level)s %(name)s %(message)s %(trace_id)s %(span_id)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)