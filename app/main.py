import logging
import sys
import threading
import time

from signalrcore.hub.base_hub_connection import BaseHubConnection
from signalrcore.hub.handlers import StreamHandler
from signalrcore.hub_connection_builder import HubConnectionBuilder

from config import get_app_settings, AppSettings


def configure_logging():
    logging.basicConfig(
        format='%(asctime)s - %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[logging.StreamHandler(sys.stdout)]
    )


class App:

    def _next_callback(self, msg):
        count_bids = len(msg.get('bids')) if msg.get('bids') else 0
        count_asks = len(msg.get('asks')) if msg.get('asks') else 0
        msg = f'count_bids={count_bids} count_asks={count_asks}'

        logging.info(msg)

    def _complete_callback(self, msg):
        self.stop_event.set()

    def _error_callback(self, msg):
        self.stop_event.set()

    def _setup_stream_callbacks(self):
        self.stream.subscribe(
            {
                "next": self._next_callback,
                "complete": self._complete_callback,
                "error": self._error_callback
            }
        )

    def _setup_stream(self):
        self.stream = self.conn.stream(
            event=self.settings.stream_event,
            event_params=self.settings.stream_event_args
        )
        self._setup_stream_callbacks()

    def _setup_conn(self):
        self.conn: BaseHubConnection = HubConnectionBuilder() \
            .with_url(self.settings.b2bx_url) \
            .with_automatic_reconnect({
                "type": "interval",
                "keep_alive_interval": 10,
                "reconnect_interval": 5,
                "max_attempts": 5
            }) \
            .build()

        self.conn.on_open(lambda: self._setup_stream())

    def __init__(self, settings: AppSettings):
        self.settings = settings
        self.conn: BaseHubConnection
        self.stream: StreamHandler
        self.stop_event = threading.Event()

        self._setup_conn()

    def start(self):
        self.conn.start()

        while not self.stop_event.is_set():
            time.sleep(1)


def get_application() -> App:
    settings = get_app_settings()
    configure_logging()

    return App(settings=settings)


if __name__ == '__main__':
    app = get_application()
    app.start()
