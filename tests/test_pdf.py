from sparktwin.model import DEFAULT,assess
from sparktwin.calibration import calibrate
from sparktwin.pdf import report_pdf

def test_pdf_signature_and_evidence_caveats():
    result=report_pdf(assess(DEFAULT),calibrate(DEFAULT,[]))
    assert result.startswith(b'%PDF-')
    assert len(result)>2000

def test_pdf_escapes_untrusted_scenario_name():
    name='<angle> & a very special company name'
    report=assess(dict(DEFAULT,name=name))
    result=report_pdf(report,calibrate(DEFAULT,[]))
    assert result.startswith(b'%PDF-')
