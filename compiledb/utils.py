import subprocess
from sys import version_info
import os

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

try:
    from shlex import quote as cmd_quote
except ImportError:
    from pipes import quote as cmd_quote


def cmd_join(cmd):
    return ' '.join(cmd_quote(s) for s in cmd)



_cygdrive_prefix = "/cygdrive/"
_len_cygdrive_prefix = len(_cygdrive_prefix)


def to_native_pathname(pathname, win_posix_shell):
    if win_posix_shell == "msys":
        # MSYS drive-letter convention.
        if len(pathname) > 2 and pathname[0] == '/' and pathname[2] == '/':
            return pathname[1] + ':' + pathname[2:]
    elif win_posix_shell == "cygwin":
        # Cygwin "/cygdrive" convention
        if pathname.startswith(_cygdrive_prefix):
            prefix_len = len(cydrive_prefix)
            return pathname[_len_cygdrive_prefix+1] + ':' + pathname[_len_cygdrive_prefix+2:]
    else:
        return pathname


def joined_native_pathname(dir, pathname, win_posix_shell):
   
    pathname = to_native_pathname(pathname, win_posix_shell)
    return os.path.join(dir, pathname)
