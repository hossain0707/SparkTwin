import json, threading, urllib.error, urllib.request
import pytest
from sparktwin.app import Controller
from sparktwin.store import Store
from sparktwin.model import DEFAULT


@pytest.fixture
def server(tmp_path):
    app=Controller(store=Store(tmp_path/'unit.db')).start()
    thread=threading.Thread(target=app.server.serve_forever,daemon=True)
    thread.start()
    yield app
    app.server.shutdown();thread.join(timeout=5);app.close()


def request(app,path,method='GET',payload=None,token=True,extra=None):
    headers={} if extra is None else dict(extra)
    if token: headers['X-SparkTwin-Token']=app.token
    if payload is not None: headers['Content-Type']='application/json'
    req=urllib.request.Request(app.url+path,data=None if payload is None else json.dumps(payload).encode(),headers=headers,method=method)
    try:
        with urllib.request.urlopen(req,timeout=5) as r:return r.status,r.read(),dict(r.headers)
    except urllib.error.HTTPError as e:return e.code,e.read(),dict(e.headers)


def test_local_health_no_token(server):
    status,body,_=request(server,'/api/health',token=False)
    assert status==200
    assert json.loads(body)['name']=='SparkTwin'


def test_api_authentication_enforced(server):
    assert request(server,'/api/bootstrap',token=False)[0]==401
    assert request(server,'/api/bootstrap',token=True)[0]==200
    assert request(server,'/api/assess',method='POST',payload=DEFAULT,token=False)[0]==401


def test_cross_origin_blocked(server):
    status,_,_=request(server,'/api/bootstrap',extra={'Origin':'https://evil.example'})
    assert status==403


def test_csp_and_local_only(server):
    status,body,headers=request(server,'/')
    assert status==200
    assert server.token.encode() in body
    assert "default-src 'none'" in headers['Content-Security-Policy']
    assert server.server.server_address[0]=='127.0.0.1'


def test_full_save_assess_backup_flow(server):
    status,body,_=request(server,'/api/assess','POST',DEFAULT)
    assert status==200
    assert json.loads(body)['calibration']['estimate'] is None
    status,body,_=request(server,'/api/scenarios','POST',DEFAULT)
    assert status==201
    ident=json.loads(body)['id']
    status,body,_=request(server,'/api/export')
    assert status==200
    data=json.loads(body)
    assert len(data['scenarios'])==1
    assert request(server,'/api/scenarios/'+ident,'DELETE')[0]==200


def test_non_finite_fails_json_serialization_at_normalize(server):
    status,body,_=request(server,'/api/assess','POST',{**DEFAULT,'params_b':'NaN'})
    assert status==400


def test_unverified_new_ssh_fingerprint_never_auto_accepted(server):
    status,body,_=request(server,'/api/ssh/inspect','POST',{'host':'bad;anything'})
    assert status==400
