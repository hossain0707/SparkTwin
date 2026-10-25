import pytest
from sparktwin.store import Store
from sparktwin.model import DEFAULT


def test_scenario_crud_and_export(tmp_path):
    db=Store(tmp_path/'data.sqlite3')
    assert db.list_scenarios()==[]
    ident=db.save_scenario(DEFAULT)
    assert db.list_scenarios()[0]['id']==ident
    assert db.export()['format']=='sparktwin-backup-v1'
    assert len(db.export()['scenarios'])==1
    assert db.remove_scenario(ident) is True
    assert db.remove_scenario(ident) is False
    db.close()


def test_bulk_import_atomic_validation(tmp_path):
    db=Store(tmp_path/'data.sqlite3')
    good=dict(device='dgx-spark-128',params_b=8.,weight_bits=4,context_tokens=8192,concurrency=4,output_tokens_per_second=25.,source='Real run')
    with pytest.raises(ValueError):db.insert_benchmarks([good,{'invalid':True}])
    assert not db.list_benchmarks()
    assert db.insert_benchmarks([good,good])==2
    assert len(db.list_benchmarks())==2
    id=db.list_benchmarks()[0]['id']
    assert db.remove_benchmark(id)
    db.close()


def test_sql_metacharacters_are_data(tmp_path):
    db=Store(tmp_path/'data.sqlite3')
    payload=dict(DEFAULT,name="Robert'); DROP TABLE scenarios; --")
    ident=db.save_scenario(payload)
    assert db.list_scenarios()[0]['name']==payload['name']
    db.close()
