#!/usr/bin/env python

import asyncio
import logging

from sfapi_client import Client, AsyncClient
from sfapi_client.compute import Machine

from sfapi_connector import KeyManager, OsSFAPI, OsWrapper, LOGGER


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

    os = OsWrapper()

    with os.open(target, "w", mk_target_dir=False) as f:
        f.write("hi\n")
        f.write("ho\n")
        f.write("hum\n")

    with os.open(target, "rb") as f:
        lines = f.readlines()

    print(lines)


def check_mkdir():
    target = "~/sfapi_test/testdir3\\0\""

    os = OsWrapper()

    os.mkdir(target)

if __name__ == "__main__":

    LOGGER.setLevel(logging.DEBUG)
    os = OsWrapper(backend=OsSFAPI)

    km = KeyManager()
    # asyncio.run(async_main())
    # check_dir()
    # check_open()
    check_mkdir()
