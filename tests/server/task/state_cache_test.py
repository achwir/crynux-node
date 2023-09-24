import pytest

from datetime import datetime

from h_server import db
from h_server.models import TaskState, TaskStatus
from h_server.task.state_cache import DbTaskStateCache, MemoryTaskStateCache


async def test_memory_state_cache():
    cache = MemoryTaskStateCache()

    state = TaskState(
        task_id=1,
        round=1,
        status=TaskStatus.Pending,
        files=["test.png"],
        result=bytes.fromhex("01020405060708"),
    )

    start = datetime.now()
    await cache.dump(state)

    _state = await cache.load(state.task_id)

    assert state == _state

    assert await cache.has(state.task_id)

    assert await cache.count() == 1
    assert await cache.count(start=start, end=datetime.now()) == 1
    assert await cache.count(start=datetime.now()) == 0
    assert await cache.count(start=start, end=datetime.now(), status=[TaskStatus.Pending]) == 1
    assert await cache.count(start=start, end=datetime.now(), status=[TaskStatus.Success]) == 0

    state.status = TaskStatus.Success
    await cache.dump(state)
    assert await cache.count() == 1
    assert await cache.count(start=start, end=datetime.now()) == 1
    assert await cache.count(start=datetime.now()) == 0
    assert await cache.count(start=start, end=datetime.now(), status=[TaskStatus.Pending]) == 0
    assert await cache.count(start=start, end=datetime.now(), status=[TaskStatus.Success]) == 1


@pytest.fixture
async def init_db():
    await db.init("sqlite+aiosqlite://")
    yield
    await db.close()


async def test_db_state_cache(init_db):
    cache = DbTaskStateCache()

    state = TaskState(
        task_id=1,
        round=1,
        status=TaskStatus.Pending,
        files=["test.png"],
        result=bytes.fromhex("01020405060708"),
    )
    
    start = datetime.now()
    await cache.dump(state)

    _state = await cache.load(state.task_id)

    assert state == _state

    assert await cache.has(state.task_id)
    assert await cache.count() == 1
    assert await cache.count(start=start, end=datetime.now()) == 1
    assert await cache.count(start=datetime.now()) == 0
    assert await cache.count(start=start, end=datetime.now(), status=[TaskStatus.Pending]) == 1
    assert await cache.count(start=start, end=datetime.now(), status=[TaskStatus.Success]) == 0

    state.status = TaskStatus.Success
    await cache.dump(state)
    assert await cache.count() == 1
    assert await cache.count(start=start, end=datetime.now()) == 1
    assert await cache.count(start=datetime.now()) == 0
    assert await cache.count(start=start, end=datetime.now(), status=[TaskStatus.Pending]) == 0
    assert await cache.count(start=start, end=datetime.now(), status=[TaskStatus.Success]) == 1
