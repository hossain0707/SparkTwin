import pytest
from sparktwin.calibration import validate_record, calibrate
from sparktwin.model import DEFAULT


def record(**k):
    return dict(device='dgx-spark-128',params_b=8.,weight_bits=4,context_tokens=8192,concurrency=4,output_tokens_per_second=28.,source='Measured benchmark A',**k)


def test_no_invented_throughput():
    r=calibrate(DEFAULT,[])
    assert r['estimate'] is None
    assert r['confidence']=='uncalibrated'


def test_one_observation_not_enough():
    assert calibrate(DEFAULT,[record()])['estimate'] is None


def test_two_nearby_observations():
    other=record();other['output_tokens_per_second']=32;other['source']='Measured benchmark B'
    r=calibrate(DEFAULT,[record(),other])
    assert 28<=r['estimate']<=32
    assert r['matches']==2
    assert 'Measured benchmark B' in r['sources']


def test_mismatched_precision_not_used():
    other=record();other['weight_bits']=8
    assert calibrate(DEFAULT,[record(),other])['estimate'] is None


def test_mismatched_hardware_not_used():
    other=record();other['device']='custom'
    assert calibrate(DEFAULT,[record(),other])['estimate'] is None


def test_large_extrapolation_refused():
    other=record();other['params_b']=80
    assert calibrate(DEFAULT,[record(),other])['estimate'] is None


def test_bad_record_rejected():
    with pytest.raises(ValueError):validate_record({'hello':1})
    with pytest.raises(ValueError):validate_record({**record(),'output_tokens_per_second':float('nan')})
