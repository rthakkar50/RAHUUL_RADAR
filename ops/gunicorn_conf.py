# Gunicorn Configuration for Oracle VM / Linux VPS (VM.Standard.E2.1.Micro)
import multiprocessing

bind = "127.0.0.1:8000"
workers = 1
worker_class = "uvicorn.workers.UvicornWorker"
keepalive = 65
timeout = 120
graceful_timeout = 30
loglevel = "info"
accesslog = "/var/log/rahuul_radar/gunicorn_access.log"
errorlog = "/var/log/rahuul_radar/gunicorn_error.log"
capture_output = True
