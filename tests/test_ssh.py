import subprocess
import pytest
from sparktwin.ssh import aliases, inspect


def test_import_ssh_host_aliases(tmp_path):
    cfg=tmp_path/'config';cfg.write_text('Host my-spark\n HostName 192.168.1.20\nHost *.corp dev-box\n Hostname another\n')
    assert aliases(cfg)==['my-spark','dev-box']


def test_host_injection_rejected():
    for value in ['whoami; rm -rf /','abc\ncat /etc/shadow','-oProxyCommand=evil','host name']:
        with pytest.raises(ValueError):inspect(value)


def test_remote_read_only_ssh_args():
    def fake(args,**kwargs):
        assert args[0]=='ssh' and 'StrictHostKeyChecking=yes' in args
        assert 'BatchMode=yes' in args
        assert args[-2]=='my-spark'
        assert 'cat /proc/meminfo' in args[-1]
        return subprocess.CompletedProcess(args,0,stdout='MEMINFO\nMemTotal: 125000000 kB\nMemAvailable: 75000000 kB\nHOSTINFO\nLinux aarch64\nGPUINFO\nGPU 0: NVIDIA GB10',stderr='')
    result=inspect('my-spark',runner=fake)
    assert result['observed'] is True
    assert result['memory_available_gib'] < result['memory_total_gib']
