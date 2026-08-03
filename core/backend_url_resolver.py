"""
Centralized Backend URL Resolver for RAHUUL_RADAR Telegram and Client Subsystems.
Implements SPRINT-194A Centralized URL Resolution Priority:
1. BACKEND_URL environment variable
2. RENDER_EXTERNAL_URL environment variable
3. Active Local Server (http://127.0.0.1:$PORT)
4. config.json (backend_url / server_url)
5. Persisted last_working_server cache
"""
import os
import json
import time
import urllib.request
from pathlib import Path
from utils.logger import get_logger

logger = get_logger(__name__)

BASE_DIR = Path(__file__).parent.parent.absolute()
CONFIG_PATH = BASE_DIR / "config.json"
CACHE_WORKING_URL_PATH = BASE_DIR / "data" / "last_working_server.txt"

class BackendUrlResolver:
    _instance = None

    def __init__(self):
        self._cached_url = None
        self._detected_env = None

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def detect_environment(self) -> str:
        if self._detected_env:
            return self._detected_env

        if os.environ.get("RENDER") or os.environ.get("RENDER_SERVICE_ID"):
            self._detected_env = "Render Cloud"
        elif os.environ.get("TUNNEL_URL") or os.environ.get("LOCALTUNNEL_URL"):
            self._detected_env = "LocalTunnel"
        elif os.environ.get("VPS_ENV"):
            self._detected_env = "VPS"
        elif os.path.exists("/.dockerenv"):
            self._detected_env = "Docker"
        else:
            self._detected_env = "Local Environment"

        logger.info(f"[BackendUrlResolver] Detected Environment: {self._detected_env}")
        return self._detected_env

    def get_base_url(self, force_refresh: bool = False) -> str:
        if self._cached_url and not force_refresh:
            return self._cached_url

        self.detect_environment()

        candidates = []

        # 1. BACKEND_URL environment variable
        if os.environ.get("BACKEND_URL"):
            candidates.append(("BACKEND_URL env", os.environ.get("BACKEND_URL").rstrip("/")))

        # 2. RENDER_EXTERNAL_URL environment variable
        if os.environ.get("RENDER_EXTERNAL_URL"):
            render_url = os.environ.get("RENDER_EXTERNAL_URL").rstrip("/")
            if not render_url.startswith("http"):
                render_url = f"https://{render_url}"
            candidates.append(("RENDER_EXTERNAL_URL env", render_url))

        # 3. Active Local Server Check
        port = os.environ.get("PORT", "8000")
        candidates.append((f"Local $PORT ({port})", f"http://127.0.0.1:{port}"))

        # 4. config.json
        try:
            if CONFIG_PATH.exists():
                with open(CONFIG_PATH, "r", encoding="utf-8") as f:
                    cfg = json.load(f)
                    b_url = cfg.get("backend_url") or cfg.get("server_url") or cfg.get("api_base")
                    if b_url:
                        candidates.append(("config.json", b_url.rstrip("/")))
        except Exception as e:
            logger.warning(f"[BackendUrlResolver] Error reading config.json: {e}")

        # 5. last_working_server file
        try:
            if CACHE_WORKING_URL_PATH.exists():
                with open(CACHE_WORKING_URL_PATH, "r", encoding="utf-8") as f:
                    last_url = f.read().strip()
                    if last_url:
                        candidates.append(("last_working_server cache", last_url.rstrip("/")))
        except Exception:
            pass

        if port != "8000":
            candidates.append(("Local 8000 Fallback", "http://127.0.0.1:8000"))

        # Verify candidate health
        for source_label, candidate_url in candidates:
            if self._verify_health(candidate_url):
                logger.info(f"[BackendUrlResolver] Successfully resolved base URL via {source_label}: {candidate_url}")
                self._cached_url = candidate_url
                self._persist_working_url(candidate_url)
                return candidate_url

        # Fallback to candidate 0 if health check unverified
        fallback_url = candidates[0][1]
        self._cached_url = fallback_url
        logger.warning(f"[BackendUrlResolver] Health check unverified. Falling back to primary candidate: {fallback_url}")
        return fallback_url

    def _verify_health(self, url: str, timeout: int = 2) -> bool:
        health_url = f"{url}/api/v1/health" if not url.endswith("/health") else url
        try:
            req = urllib.request.Request(health_url, headers={"User-Agent": "RAHUUL_RADAR_TelegramResolver/1.0"})
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return resp.status == 200
        except Exception:
            return False

    def _persist_working_url(self, url: str):
        try:
            os.makedirs(CACHE_WORKING_URL_PATH.parent, exist_ok=True)
            with open(CACHE_WORKING_URL_PATH, "w", encoding="utf-8") as f:
                f.write(url)
        except Exception:
            pass

    def fetch_api_with_retry(self, endpoint: str, method: str = "GET", payload: dict = None, max_retries: int = 3) -> dict:
        base_url = self.get_base_url()
        clean_endpoint = endpoint if endpoint.startswith("/") else f"/{endpoint}"
        full_url = f"{base_url}{clean_endpoint}"
        env_label = self.detect_environment()

        backoff = 1
        last_error = None
        for attempt in range(1, max_retries + 1):
            start_t = time.time()
            try:
                data_bytes = json.dumps(payload).encode("utf-8") if payload else None
                headers = {"Content-Type": "application/json"} if payload else {}
                req = urllib.request.Request(full_url, data=data_bytes, headers=headers, method=method)

                with urllib.request.urlopen(req, timeout=8) as resp:
                    latency_ms = (time.time() - start_t) * 1000
                    if resp.status == 200:
                        logger.info(f"[BackendUrlResolver] Request SUCCESS | Attempt: {attempt}/{max_retries} | Env: {env_label} | URL: {full_url} | Code: 200 | Latency: {latency_ms:.1f}ms")
                        return json.loads(resp.read().decode("utf-8"))
                    else:
                        logger.warning(f"[BackendUrlResolver] Request NON-200 | Attempt: {attempt}/{max_retries} | Env: {env_label} | URL: {full_url} | Code: {resp.status}")
            except Exception as e:
                latency_ms = (time.time() - start_t) * 1000
                last_error = str(e)
                logger.warning(f"[BackendUrlResolver] Request FAILED | Attempt: {attempt}/{max_retries} | Env: {env_label} | URL: {full_url} | Error: {e} | Latency: {latency_ms:.1f}ms")
                if attempt < max_retries:
                    time.sleep(backoff)
                    backoff *= 2
                    # Try refreshing URL candidate on failure
                    base_url = self.get_base_url(force_refresh=True)
                    full_url = f"{base_url}{clean_endpoint}"

        logger.error(f"[BackendUrlResolver] All {max_retries} attempts failed for {full_url}. Last error: {last_error}")
        return {}
