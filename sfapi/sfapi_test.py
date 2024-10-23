#!/usr/bin/env python

import asyncio
import logging

from sfapi_client import Client, AsyncClient
from sfapi_client.compute import Machine

from sfapi_connector import KeyManager, OpenSFAPI, LOGGER


async def async_main():
    km = KeyManager()
    print(f"Loaded: {km.id=}, {km.key=}")

    # Get the user info, "Who does the api think I am?"
    async with AsyncClient(key=km.key) as client:
        user = await client.user()

    # Let's see what the user object has in it
    print(f"Client corresponds to {user=}")


def check_dir():
    km = KeyManager()
    target = "~/sfapi_test"

    with Client(key=km.key) as client:
        target = target.replace("~/", km.home)
        print(f"{km.home=}, {target=}")

        perlmutter = client.compute(Machine.perlmutter)
        print(perlmutter.status)

        perlmutter.run(f"mkdir -p {target}")
        [dir] = perlmutter.ls(target, directory=True)
        print(dir)


def check_open():
    target = "~/sfapi_test/test.txt"

    with OpenSFAPI(target, "w", mk_target_dir=False) as f:
        f.write("hi\n")
        f.write("ho\n")
        f.write("hum\n")


    with OpenSFAPI(target, "rb") as f:
        lines = f.readlines()

    print(lines)


if __name__ == "__main__":

    LOGGER.setLevel(logging.DEBUG)

    km = KeyManager()
    # asyncio.run(async_main())
    # check_dir()
    check_open()
