import subprocess
from sys import version_info

if version_info.major >= 3 and version_info.minor >= 6:
    def popen(cmd, encoding='utf-8', **kwargs):
        return subprocess.Popen(cmd, encoding=encoding, shell=True, **kwargs)

    def run_cmd(cmd, encoding='utf-8', **kwargs):
        return subprocess.check_output(cmd, encoding=encoding, **kwargs)
else:  # Python 2 and Python <= 3.5
    def popen(cmd, encoding='utf-8', **kwargs):
        return subprocess.Popen(cmd, shell=True, **kwargs)

    def run_cmd(cmd, encoding='utf-8', **kwargs):
        return subprocess.check_output(cmd, **kwargs)
