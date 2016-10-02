"""
This script run a simple test to check whether backend is responsing correctly.
"""

import requests
import json

settings = json.load(open('config.json'))


def test_backend():
    backend_url = 'http://' + settings['backend_host'] + ':' + settings['backend_port']
    backend_headers = {'content-type': 'application/json'}

    request_payload = {
        "method": "query_test",
        "jsonrpc": "2.0",
        "id": 0,
    }
    response = requests.post(
        backend_url, data=json.dumps(request_payload), headers=backend_headers).json()

    assert response['result'] is True

if __name__ == '__main__':
    test_backend()
