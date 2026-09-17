import logging
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer

logger = logging.getLogger(__name__)

HEALTH_PORT = 8080
STALE_AFTER_SECONDS = 60

# Plain module global, no lock: the worker loop (record_heartbeat) and the health
# server thread (heartbeat_age_seconds) only ever do a single float read/write each,
# which the GIL already makes atomic.
_last_heartbeat: float | None = None


def record_heartbeat() -> None:
    global _last_heartbeat
    _last_heartbeat = time.time()


def heartbeat_age_seconds() -> float | None:
    if _last_heartbeat is None:
        return None
    return time.time() - _last_heartbeat


class _HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path != "/healthz":
            self.send_response(404)
            self.end_headers()
            return

        age = heartbeat_age_seconds()
        healthy = age is not None and age <= STALE_AFTER_SECONDS
        self.send_response(200 if healthy else 503)
        self.end_headers()

    def log_message(self, log_format: str, *args) -> None:
        pass


def start_health_server() -> None:
    server = HTTPServer(("0.0.0.0", HEALTH_PORT), _HealthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    logger.info("Health endpoint listening on :%d/healthz", HEALTH_PORT)
