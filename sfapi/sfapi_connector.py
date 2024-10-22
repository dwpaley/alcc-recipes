from sfapi_client         import Client
from sfapi_client.compute import Machine

from pathlib import Path

import os
import io
import sys
import json

import logging
LOGGER = logging.getLogger(__name__)
# LOGGER.setLevel(logging.DEBUG)
HANDLER = logging.StreamHandler(sys.stdout)
HANDLER.setFormatter(
    logging.Formatter(
        "[%(levelname)8s | %(filename)s:%(lineno)s] %(message)s"
    )
)
LOGGER.addHandler(HANDLER)


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


class SFAPIFile(io.StringIO):
    def __init__(self, path):
        self.path     = path
        self.dirname  = os.path.dirname(path)
        self.filename = os.path.basename(path)

        super().__init__()

    def back_to_start(self):
        self.seek(0)
        bio = io.BytesIO(self.read().encode("utf8"))
        bio.dirname  = self.dirname
        bio.filename = self.filename
        return bio


class OpenSFAPI:
    def __init__(self, file_name):
        _, self.key    = load_key()
        LOGGER.debug(
            f"Intiating SFAPI connection using key file: {self.key}"
        )

        self.client    = Client(key=self.key)
        self.user      = self.client.user()
        self.home_path = f"/global/homes/{self.user.name[0]}/{self.user.name}/"
        self.compute   = self.client.compute(Machine.perlmutter)
        self.buffer = SFAPIFile(file_name.replace("~/", self.home_path))

        LOGGER.info((
            "Initiated SFAPI connection for: "
            f"user '{self.user.name}' on machine '{self.compute.name}'"
        ))

    def __enter__(self):
        return self.buffer

    def __exit__(self, type, value, traceback):
        LOGGER.info(f"Writing file to remote location: {self.buffer.path}")
        LOGGER.debug(f"The machine is: {self.compute.status}")

        LOGGER.debug(f"Ensuring that {self.buffer.dirname} exists")
        self.compute.run(f"mkdir -p {self.buffer.dirname}")

        LOGGER.debug(f"Getting remote path handle to: {self.buffer.dirname}")
        [dir] = self.compute.ls(self.buffer.dirname, directory=True)

        LOGGER.debug(f"Uploading data to: {self.buffer.filename}")
        dir.upload(self.buffer.back_to_start())

        self.client.close()
        LOGGER.debug("DONE")



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

