import platform

from . import client, orm
VERSION = platform.python_version_tuple()
if VERSION[0] != '3' or VERSION[1] < '6':
    raise RuntimeError(f'version {platform.python_version()} < 3.6')


__all__ = [client, orm]
