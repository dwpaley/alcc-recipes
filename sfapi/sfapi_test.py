#!/usr/bin/env python

import asyncio

from sfapi_client import AsyncClient

from sfapi_connector import load_key


async def main():

    id, key = load_key()
    print(f"Loaded: {id=}, {key=}")

    # Get the user info, "Who does the api think I am?"
    async with AsyncClient(key=key) as client:
        user = await client.user()

    # Let's see what the user object has in it
    print(f"Client corresponds to {user=}")


if __name__ == "__main__":
    asyncio.run(main())
