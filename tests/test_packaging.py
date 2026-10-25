from pathlib import Path
from sparktwin.packaged import root

def test_assets_exist_for_local_source():
    r=root()
    assert (r/'sparktwin'/'web'/'index.html').exists()
    assert (r/'sparktwin'/'web'/'app.js').exists()
    assert (r/'sparktwin'/'web'/'styles.css').exists()

def test_gitignore_blocks_private_keys():
    text=(root()/'.gitignore').read_text()
    assert '*.pem' in text and '.env' in text
