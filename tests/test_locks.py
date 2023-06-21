import asyncio
import unittest
import datetime
from unittest import IsolatedAsyncioTestCase
from potnanny.locks import LOCKS, init_locks


class TestLockFuncs(IsolatedAsyncioTestCase):
# ###############################################

    async def test_lock(self):
        await init_locks()
        assert LOCKS['bluetooth'] is not None
        assert LOCKS['db'] is not None
        assert LOCKS['gpio'] is not None

    async def test_lock_types(self):
        await init_locks()
        assert type(LOCKS['bluetooth']) is asyncio.Lock
        assert type(LOCKS['db']) is asyncio.Lock
        assert type(LOCKS['gpio']) is asyncio.Lock


if __name__ == '__main__':
    unittest.main()
