from dataclasses import replace
from datetime import datetime, timezone, timedelta
import json
from uuid import uuid4

import httpx
import jwt
import pytest
from fastapi.testclient import TestClient

from cardioia.config import Settings
from cardioia.main import create_app
from cardioia.services.risk import RiskService


@pytest.fixture
def settings(tmp_path):
    return Settings(secret="test-secret-"*5, password="test-password-1234", device_key="test-device-"*4, db_path=str(tmp_path/'test.db'))


@pytest.fixture
def client(settings):
    with TestClient(create_app(settings)) as client:
        yield client


@pytest.fixture
def auth(client, settings):
    response = client.post('/api/v1/auth/login',json={'email':settings.email,'password':settings.password})
    assert response.status_code == 200
    return {'Authorization':'Bearer '+response.json()['access_token']}


def reading(**kwargs):
    return {'event_id':uuid4().hex,'device_id':'esp32-001','patient_id':'demo-001','temperature_c':36.6,'heart_rate_bpm':76,**kwargs}


def send(client, settings, payload):
    return client.post('/api/v1/readings',json=payload,headers={'X-Device-Key':settings.device_key})


def test_health_and_login(client, auth):
    assert client.get('/health').json()['risk_model']=='loaded'
    assert client.get('/api/v1/auth/me',headers=auth).json()['mode']=='academic_demo'
    assert client.post('/api/v1/auth/login',json={'email':'demo@cardioia.local','password':'incorrect'}).status_code==401


@pytest.mark.parametrize('method,path,body',[
    ('GET','/api/v1/dashboard',None),('GET','/api/v1/readings',None),
    ('POST','/api/v1/demo/reading',None),('POST','/api/v1/chat',{'message':'teste'}),
    ('POST','/api/v1/symptoms',{'message':'teste'})])
def test_private_routes_require_authentication(client,method,path,body):
    assert client.request(method,path,json=body).status_code==401


def test_expired_and_forged_tokens(client,settings):
    claims={'sub':settings.email,'iat':datetime.now(timezone.utc)-timedelta(hours=3),'exp':datetime.now(timezone.utc)-timedelta(hours=1),'iss':'cardioia-api','aud':'cardioia'}
    for key in [settings.secret,'incorrect-secret'*4]:
        token=jwt.encode(claims,key,algorithm='HS256')
        assert client.get('/api/v1/dashboard',headers={'Authorization':'Bearer '+token}).status_code==401


def test_device_auth_and_scope(client,settings,auth):
    assert client.post('/api/v1/readings',json=reading(),headers=auth).status_code==401
    assert send(client,settings,reading(patient_id='other-patient')).status_code==403
    assert send(client,settings,reading(device_id='other-device')).status_code==403


@pytest.mark.parametrize('change',[
    {'heart_rate_bpm':0},{'heart_rate_bpm':76.5},{'temperature_c':999},
    {'movement_detected':'false'},{'extra':'unexpected'},
    {'timestamp':'2026-01-01T00:00:00Z'}, {'timestamp':'2026-10-31T10:00:00'},
])
def test_invalid_readings_rejected(client,settings,change):
    assert send(client,settings,reading(**change)).status_code==422


def test_sensor_to_dashboard_idempotency_and_restart(client,settings,auth):
    payload=reading(temperature_c=39.1,heart_rate_bpm=132,emergency_button_pressed=True)
    first=send(client,settings,payload)
    assert first.status_code==200
    result=first.json()
    assert result['sensor_alerts']['risk_level']=='CRITICAL'
    assert result['feedback']['led']=='red'
    assert result['prediction']['source']=='phase6_random_forest'
    assert result['feature_provenance']['system_load']=='contexto_sintetico_fixo'
    again=send(client,settings,payload).json()
    assert again['duplicate'] is True
    assert again['received_at']==result['received_at']
    assert send(client,settings,{**payload,'heart_rate_bpm':100}).status_code==409
    assert len(client.get('/api/v1/readings',headers=auth).json()['items'])==1
    with TestClient(create_app(settings)) as restarted:
        dashboard=restarted.get('/api/v1/dashboard',headers=auth).json()
        assert dashboard['latest']['event_id']==payload['event_id']
        assert not dashboard['stale']


def test_empty_stale_and_out_of_order_history(client,settings,auth):
    assert client.get('/api/v1/dashboard',headers=auth).json()['stale']
    now=datetime.now(timezone.utc)
    old=reading(timestamp=(now-timedelta(minutes=2)).isoformat())
    send(client,settings,old)
    assert client.get('/api/v1/dashboard',headers=auth).json()['stale']
    recent=reading()
    send(client,settings,recent)
    send(client,settings,reading(timestamp=(now-timedelta(minutes=1)).isoformat()))
    assert client.get('/api/v1/dashboard',headers=auth).json()['latest']['event_id']==recent['event_id']


def test_original_phase6_golden_case():
    result=RiskService().predict({'middle_ages':62,'system_load':92,'waiting_time':75,'average_hr':118,'average_spo2':89,'systolic_bp':100,'temperature':37.5,'event_density':7,'events_24h':5,'resource_availability':25})
    assert result['risk_probability']==0.99
    assert result['risk_level']=='HIGH'
    assert [p['id'] for p in result['suggested_protocols']]==['P02','P05','P08','P10']


def test_nlp_and_honest_fallback(client,auth):
    result=client.post('/api/v1/symptoms',headers=auth,json={'message':'sinto dor no peito e falta de ar'}).json()
    assert result['label']=='alto risco'
    assert 'dor no peito' in result['matched_symptoms']
    result=client.post('/api/v1/chat',headers=auth,json={'message':'insuficiência cardíaca'}).json()
    assert result['source']=='local_fallback'
    assert result['sources']


def test_provider_uses_real_prediction(settings,monkeypatch):
    from cardioia.services import chat
    captured=[]
    async def handler(request):
        captured.append(json.loads(request.content))
        assert request.headers['x-goog-api-key']=='test-key'
        return httpx.Response(200,json={'candidates':[{'content':{'parts':[{'text':'Explicação simulada.'}]}}]})
    original=httpx.AsyncClient
    monkeypatch.setattr(chat.httpx,'AsyncClient',lambda **kw:original(transport=httpx.MockTransport(handler),**kw))
    with TestClient(create_app(replace(settings,gemini_key='test-key'))) as client:
        token=client.post('/api/v1/auth/login',json={'email':settings.email,'password':settings.password}).json()['access_token']
        auth={'Authorization':'Bearer '+token}
        client.post('/api/v1/demo/reading',headers=auth)
        response=client.post('/api/v1/chat',headers=auth,json={'message':'Explique a previsão'})
        assert response.json()['source']=='gemini'
        context=json.loads(captured[0]['contents'][0]['parts'][0]['text'])
        assert context['phase6_latest_prediction']['source']=='phase6_random_forest'


@pytest.mark.parametrize('provider_status', [403, 429, 500])
def test_provider_failure_is_reported_without_leaking_secrets(settings,monkeypatch,provider_status):
    from cardioia.services import chat
    async def handler(request):
        return httpx.Response(provider_status,json={'error':'private-provider-detail-test-key'})
    original=httpx.AsyncClient
    monkeypatch.setattr(chat.httpx,'AsyncClient',lambda **kw:original(transport=httpx.MockTransport(handler),**kw))
    with TestClient(create_app(replace(settings,gemini_key='test-key'))) as client:
        token=client.post('/api/v1/auth/login',json={'email':settings.email,'password':settings.password}).json()['access_token']
        response=client.post('/api/v1/chat',headers={'Authorization':'Bearer '+token},json={'message':'Explique o resultado'})
        assert response.status_code==503
        assert 'test-key' not in response.text
        assert 'private-provider' not in response.text


def test_invalid_image_fails_before_loading_tensorflow(settings):
    with TestClient(create_app(replace(settings,vision_enabled=True))) as client:
        token=client.post('/api/v1/auth/login',json={'email':settings.email,'password':settings.password}).json()['access_token']
        response=client.post('/api/v1/vision',headers={'Authorization':'Bearer '+token},files={'image':('bad.png',b'invalid','image/png')})
        assert response.status_code==422
        assert client.app.state.vision.model is None


def test_vision_requires_auth_and_reports_unavailable(client,auth):
    files={'image':('test.png',b'not an image','image/png')}
    assert client.post('/api/v1/vision',files=files).status_code==401
    assert client.post('/api/v1/vision',files=files,headers=auth).status_code==503


def test_login_rate_limit(client,settings):
    for _ in range(10):
        assert client.post('/api/v1/auth/login',json={'email':settings.email,'password':'wrong'}).status_code==401
    assert client.post('/api/v1/auth/login',json={'email':settings.email,'password':'wrong'}).status_code==429


def test_payload_bound_and_cors(client):
    assert client.post('/api/v1/readings',content=b'x'*(6*1024*1024+1)).status_code==413
    response=client.options('/api/v1/readings',headers={'Origin':'https://untrusted.example','Access-Control-Request-Method':'POST'})
    assert 'access-control-allow-origin' not in response.headers
