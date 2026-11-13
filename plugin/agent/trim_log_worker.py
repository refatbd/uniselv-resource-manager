"""Trim a tenant-owned log with the tenant UID and a single file descriptor."""

import json
import os
import pathlib
import stat
import sys


def _trim_open_log(home: str, relative: str, keep_lines: int) -> tuple[int, int]:
    parts = pathlib.PurePosixPath(relative).parts
    if not parts or any(part in ('/', '..') for part in parts):
        raise ValueError('Invalid log path')
    directory_flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
    directory = os.open(home, directory_flags)
    try:
        for part in parts[:-1]:
            child = os.open(part, directory_flags, dir_fd=directory)
            os.close(directory)
            directory = child
        fd = os.open(parts[-1], os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory)
    finally:
        os.close(directory)
    with os.fdopen(fd, 'r+b') as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1 or info.st_uid != os.geteuid():
            raise ValueError('Expected an account-owned regular log with one link')
        tail = b''
        if keep_lines and info.st_size:
            stream.seek(max(0, info.st_size - 262144))
            lines = stream.read(262144).splitlines()[-keep_lines:]
            tail = b'\n'.join(lines) + (b'\n' if lines else b'')
        if os.fstat(stream.fileno()).st_size != info.st_size:
            raise ValueError('Log changed during trim. Retry or rotate it instead.')
        stream.seek(0)
        stream.write(tail)
        stream.truncate(len(tail))
        return info.st_size, len(tail)


if __name__ == "__main__":
    try:
        print(json.dumps(_trim_open_log(sys.argv[1], sys.argv[2], int(sys.argv[3]))))
    except (OSError, ValueError):
        sys.exit(1)
