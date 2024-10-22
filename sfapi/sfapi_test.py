#!/usr/bin/env python

import asyncio
import logging

from sfapi_client import Client, AsyncClient
from sfapi_client.compute import Machine

from sfapi_connector import load_key, OpenSFAPI, LOGGER


async def async_main():

    id, key = load_key()
    print(f"Loaded: {id=}, {key=}")

    # Get the user info, "Who does the api think I am?"
    async with AsyncClient(key=key) as client:
        user = await client.user()

    # Let's see what the user object has in it
    print(f"Client corresponds to {user=}")


def check_dir():
    _, key = load_key()

    target = "~/sfapi_test"

    with Client(key=key) as client:
        user      = client.user()
        home_path = f"/global/homes/{user.name[0]}/{user.name}/"
        target = target.replace("~/", home_path)
        print(f"{home_path=}, {target=}")

        perlmutter = client.compute(Machine.perlmutter)
        print(perlmutter.status)

        perlmutter.run(f"mkdir -p {target}")
        [dir] = perlmutter.ls(target, directory=True)
        print(dir)


def check_open():
    target = "~/sfapi_test/test.txt"

    with OpenSFAPI(target) as f:
        f.write("hi\n")
        f.write("ho\n")


if __name__ == "__main__":

    LOGGER.setLevel(logging.DEBUG)

    asyncio.run(async_main())
    check_dir()
    check_open()
