"""MicroPython transport helper for Raphael; no board or sensor assumptions.

Import into the Wokwi project after adding its own config.py.
Keep the same payload/event_id on retry, and use a new ID for a new sample.
"""
import ujson
import urequests


def send_reading(base_url, device_key, payload):
    response = None
    try:
        response = urequests.post(
            base_url.rstrip('/') + '/api/v1/readings',
            data=ujson.dumps(payload),
            headers={'Content-Type': 'application/json', 'X-Device-Key': device_key},
        )
        if response.status_code != 200:
            raise OSError('CardioIA HTTP ' + str(response.status_code))
        result = response.json()
        return result['feedback']
    finally:
        if response is not None:
            response.close()
