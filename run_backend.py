from werkzeug.serving import run_simple
import json
from backend.core import ATBackendServer

settings = json.load(open('config.json'))


if __name__ == '__main__':
    backend = ATBackendServer()
    run_simple(settings['backend_host'], settings['backend_port'], backend.application)