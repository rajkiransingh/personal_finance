import socket
import threading
import time
from typing import Optional, Dict, Any

import requests

from utilities.common.app_config import config

logger = config.setup_logger("api.raiden")


class RaidenIntegration:
    def __init__(self):
        self.raiden_url = config.RAIDEN_URL.rstrip("/")
        self.n8n_url = config.N8N_WEBHOOK_URL
        self.service_name = config.SERVICE_NAME
        self.host_ip = self._get_host_ip()
        self.port = 8000
        self.stop_event = threading.Event()
        self.thread: Optional[threading.Thread] = None

    def _get_host_ip(self) -> str:
        """Get the container's IP address."""
        try:
            return socket.gethostbyname(socket.gethostname())
        except Exception:
            return "127.0.0.1"

    def register(self) -> bool:
        """Register the service with Raiden."""
        payload = {
            "name": self.service_name,
            "role": "financer",
            "host": f"{self.host_ip}",
            "ip": self.host_ip,
            "port": self.port,
            "heartbeat_interval": 10,
            "version": "1.0.0",
        }

        try:
            logger.info(f"Attempting to register with Raiden at {self.raiden_url}...")
            response = requests.post(
                f"{self.raiden_url}/register", json=payload, timeout=5
            )
            response.raise_for_status()
            logger.info(f"Successfully registered {self.service_name} with Raiden.")
            return True
        except Exception as e:
            logger.error(f"Failed to register with Raiden: {e}")
            return False

    def start_heartbeat(self):
        """Start the background heartbeat thread."""
        if self.thread and self.thread.is_alive():
            return

        self.stop_event.clear()
        self.thread = threading.Thread(target=self._heartbeat_loop, daemon=True)
        self.thread.start()
        logger.info("Heartbeat thread started.")

    def stop_heartbeat(self):
        """Stop the heartbeat thread."""
        self.stop_event.set()
        if self.thread:
            self.thread.join(timeout=2)
            logger.info("Heartbeat thread stopped.")

    def _heartbeat_loop(self):
        """Send heartbeat to Raiden every 10 seconds."""
        while not self.stop_event.is_set():
            try:
                payload = {
                    "name": self.service_name,
                    "status": "online",
                    "metrics": {"uptime": "running"},
                }
                response = requests.post(
                    f"{self.raiden_url}/heartbeat", json=payload, timeout=5
                )
                if response.status_code != 200:
                    logger.warning(
                        f"Heartbeat failed with status: {response.status_code}"
                    )
                    # If 404, we might need to re-register
                    if response.status_code == 404:
                        logger.info(
                            "Service not found in Raiden, attempting to re-register..."
                        )
                        self.register()
            except Exception as e:
                logger.debug(f"Heartbeat error: {e}")

            time.sleep(10)

    def send_event(self, event_type: str, data: Optional[Dict[str, Any]] = None):
        """Send an event to N8N."""
        if not self.n8n_url:
            logger.warning("N8N_WEBHOOK_URL not configured. Skipping event emission.")
            return

        payload = {
            "event": event_type,
            "data": data or {},
            "source": self.service_name,
            "timestamp": time.time(),
        }

        try:
            # Run in a separate thread to not block main execution
            threading.Thread(
                target=self._send_event_async, args=(payload,), daemon=True
            ).start()
        except Exception as e:
            logger.error(f"Failed to trigger event send: {e}")

    def _send_event_async(self, payload):
        try:
            logger.info(f"Emit event: {payload['event']}")
            requests.post(self.n8n_url, json=payload, timeout=5)
        except Exception as e:
            logger.error(f"Failed to send event to N8N: {e}")


# Global instance
raiden_client = RaidenIntegration()
