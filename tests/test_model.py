import math
import pytest
from sparktwin.model import DEFAULT, GB_TO_GIB, normalize, assess, recommend_variant, InvalidScenario


def test_dgx_spark_decimal_memory_conversion():
    r=assess(DEFAULT)
    assert r['physical_gib']==round(128e9/1024**3,3)
    assert 119 < r['physical_gib'] < 120
    assert r['profile_source'].startswith('https://docs.nvidia.com/')
    assert r['status'] in {'fits-estimate','tight','exceeds'}
    assert r['throughput_tokens_per_s'] is None


def test_kv_formula_gqa():
    r=assess({**DEFAULT,'layers':1,'kv_heads':1,'head_dim':128,'kv_bytes':2,'context_tokens':1024,'concurrency':1})
    assert r['kv_bytes_per_token']==512
    assert r['kv_gib']==round(512*1024/1024**3,3)


def test_more_concurrency_increases_kv():
    a=assess({**DEFAULT,'concurrency':1})
    b=assess({**DEFAULT,'concurrency':8})
    assert b['kv_gib'] > a['kv_gib']
    assert b['headroom_gib'] < a['headroom_gib']


def test_high_memory_exceeds():
    r=assess({**DEFAULT,'params_b':405,'weight_bits':16})
    assert r['status']=='exceeds'
    assert r['headroom_gib'] < 0


def test_custom_profile():
    r=assess({**DEFAULT,'profile':'custom','custom_memory_gb':64,'custom_bandwidth_gbs':90})
    assert r['physical_gib']==round(64*GB_TO_GIB,3)
    assert r['bandwidth_gbs']==90


@pytest.mark.parametrize('field,value',[('params_b',float('nan')),('params_b',float('inf')),('concurrency',0),('context_tokens',100),('layers',2.3),('weight_bits',True),('profile','unknown'),('name','')])
def test_invalid_inputs(field,value):
    with pytest.raises(InvalidScenario): normalize({**DEFAULT,field:value})


def test_unknown_scenario_field_rejected():
    with pytest.raises(InvalidScenario):normalize({**DEFAULT,'dangerous':'field'})


def test_variants_are_memory_models_not_false_perf():
    variants=recommend_variant(DEFAULT)
    assert len(variants)==4
    assert variants[0]['label']=='As configured'
    assert variants[1]['total_gib']<=variants[0]['total_gib']
    assert variants[2]['total_gib']<=variants[0]['total_gib']
