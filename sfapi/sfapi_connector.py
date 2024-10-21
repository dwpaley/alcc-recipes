from sfapi_client         import Client
from sfapi_client.compute import Machine

from pathlib import Path

import json


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
