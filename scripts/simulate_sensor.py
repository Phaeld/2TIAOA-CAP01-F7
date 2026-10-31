"""Desktop contract check; this is not a completed Wokwi simulation."""
import argparse
import json
import os
from pathlib import Path
from uuid import uuid4

import httpx
from dotenv import load_dotenv

root = Path(__file__).resolve().parents[1]
load_dotenv(root / '.env')
parser = argparse.ArgumentParser()
parser.add_argument('--url', default='http://127.0.0.1:8000')
parser.add_argument('--alert', action='store_true')
args = parser.parse_args()
payload = json.loads((root / 'IoT/telemetry.example.json').read_text())
payload['event_id'] = 'desktop-' + uuid4().hex
if args.alert:
    payload.update(temperature_c=39.1, heart_rate_bpm=132)
response = httpx.post(args.url.rstrip('/')+'/api/v1/readings', json=payload,
                      headers={'X-Device-Key':os.environ['CARDIOIA_DEVICE_KEY']}, timeout=60)
response.raise_for_status()
result = response.json()
print(json.dumps({'event_id':result['event_id'], 'feedback':result['feedback'], 'prediction':result['prediction']}, ensure_ascii=False, indent=2))
