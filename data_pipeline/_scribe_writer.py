import clog

from data_pipeline.message import Message
from data_pipeline.envelope import Envelope

logger = get_config().logger

# Since we are passing messages through scribe we don't support keys
class ScribeWriter(object):

    def __init__(self, dry_run=False, retry_interval=3):
        self.dry_run = dry_run
        self.envelope = Envelope()
        self.scriber = clog.ScribeLogger(clog.config.scribe_host, clog.config.scribe_port, retry_interval)

    def publish(self, message):
        if not self.dry_run:
            try:
                self.scriber.log_line(message.topic, self.envelope.pack(message))
            except:
                # Unfortunately if our scribe failed the logger will likely fail
                # but at least the clog handler will have a default error handling
                logger.error(
                    "Failed to scribe message - "
                    "uuid hex: {0}, "
                    "schema_id: {1}, "
                    "timestamp: {2}, "
                    "type: {3}".format(
                        message.uuid_hex,
                        message.schema_id,
                        message.timestamp,
                        message.message_type.name
                    )

    def close(self):
        if self.scriber:
            self.scriber.close()
