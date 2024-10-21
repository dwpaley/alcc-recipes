from sfapi_client         import Client
from sfapi_client.compute import Machine

from pathlib import Path

import os
import io
import json


# TODO: replace with simple singleton
def load_key():
    key_store = Path("~/.superfacility/").expanduser().resolve()

    if not key_store.is_dir():
        raise RuntimeError(f"Secret store {key_store} does not exist") 

    # Load the client_id for the key
    with open(key_store / "clientid.txt", "r") as f:
        client_id = "".join(f.readlines())

    # Get the path for your json file here
    sfapi_key = key_store / "priv_key.pem"
    # ensure the correct file permissions required by the SFAPI
    if sfapi_key.stat() != 0o600:
        sfapi_key.chmod(0o600)

    # ensure that the client key file starts with the client id:
    with sfapi_key.open("r") as f:
        sfapi_key_file = [x.strip() for x in f.readlines()]

    if sfapi_key_file[0] != client_id:
        with open(sfapi_key, "w") as f:
            f.write(f"{client_id}\n" + "\n".join(sfapi_key_file))

    return client_id, sfapi_key


class SFAPIFile:
    def __init__(self, name):
        self.name = name
        self.buffer = io.StringIO()

    def back_to_start(self):
        self.buffer.seek(0)

    def __getattr__(self, name):
        return getattr(self.buffer, name)


class OpenSFAPI:
    def __init__(self, file_name):
        self.lines_buffer = SFAPIFile(file_name)

    def __enter__(self):
        return self.lines_buffer

    def __exit__(self, type, value, traceback):
        self.lines_buffer.back_to_start()
        print(self.lines_buffer.readlines())


class OsBackend:
    @staticmethod
    def open(
        file,
        mode='r', buffering=-1, encoding=None, errors=None, newline=None,
        closefd=True, opener=None
    ):
        return open(
            file, mode, buffering, encoding, errors, newline, closefd, opener
        )

    @staticmethod
    def mkdir(path, mode=0o777, *, dir_fd=None): 
        return os.mkdir(path, mode, dir_fd)

    @staticmethod
    def stat(fd):
        return os.stat(fd)

    @staticmethod
    def chmod(path, mode, *, dir_fd=None, follow_symlinks=True):
        os.chmod(path, mode, dir_fd, follow_symlinks)


class OsSFAPI:
    @staticmethod
    def open(
        file,
        mode='r', buffering=-1, encoding=None, errors=None, newline=None,
        closefd=True, opener=None, key=None
    ):
        return OpenSFAPI(file)

    @staticmethod
    def mkdir(path, mode=0o777, *, dir_fd=None): 
        pass

    @staticmethod
    def stat(fd):
        pass

    @staticmethod
    def chmod(path, mode, *, dir_fd=None, follow_symlinks=True):
        pass


class OsWrapper:

    def __init__(self, backend):
        pass

