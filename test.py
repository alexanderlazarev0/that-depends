import asyncio
import random
import typing

import pytest

from that_depends.container import BaseContainer
from that_depends.injection import Provide, inject
from that_depends.providers.context_resources import MyContextResouce, fetch_context_item, my_container_context


random.seed(1)


async def async_yields_string() -> typing.AsyncIterator[str]:
    yield str(random.random())  # noqa: S311


def sync_yields_string() -> typing.Iterator[str]:
    yield str(random.random())  # noqa: S311


class MyContainer(BaseContainer):
    async_resource: MyContextResouce[str] = MyContextResouce(async_yields_string)
    sync_resource: MyContextResouce[str] = MyContextResouce(sync_yields_string)


@MyContainer.sync_resource.sync_context()
@inject
def sync_injected(val: str = Provide[MyContainer.sync_resource]) -> str:
    return val


@MyContainer.async_resource.async_context()
@inject
async def async_injected(val: str = Provide[MyContainer.async_resource]) -> str:
    return val


@MyContainer.async_resource.context()
@inject
async def async_injected_implicit(val: str = Provide[MyContainer.async_resource]) -> str:
    return val


@MyContainer.sync_resource.context()
@inject
def sync_injected_implicit(val: str = Provide[MyContainer.sync_resource]) -> str:
    return val


async def test_injected() -> None:
    async_result = await async_injected()
    sync_result = sync_injected()
    async_result_implicit = await async_injected_implicit()
    sync_result_implicit = sync_injected_implicit()
    assert isinstance(async_result, str)
    assert isinstance(sync_result, str)
    assert isinstance(async_result_implicit, str)
    assert isinstance(sync_result_implicit, str)


async def async_main() -> None:
    """Test async resolution."""
    async with MyContainer.async_resource.async_context():
        val_1 = await MyContainer.async_resource.async_resolve()
        val_2 = await MyContainer.async_resource.async_resolve()
        assert val_1 == val_2
        async with MyContainer.async_resource.async_context():
            val_3 = await MyContainer.async_resource.async_resolve()
            assert val_1 != val_3
            async with MyContainer.async_resource.async_context():
                val_4 = await MyContainer.async_resource.async_resolve()
                assert val_1 != val_4 != val_3
            val_5 = await MyContainer.async_resource.async_resolve()
            assert val_5 == val_3
        val_6 = await MyContainer.async_resource.async_resolve()
        assert val_6 == val_1


def sync_main() -> None:
    """Test sync resolution."""
    with MyContainer.sync_resource.sync_context():
        val_1 = MyContainer.sync_resource.sync_resolve()
        val_2 = MyContainer.sync_resource.sync_resolve()
        assert val_1 == val_2
        with MyContainer.sync_resource.sync_context():
            val_3 = MyContainer.sync_resource.sync_resolve()
            assert val_1 != val_3
            with MyContainer.sync_resource.sync_context():
                val_4 = MyContainer.sync_resource.sync_resolve()
                assert val_1 != val_4 != val_3
        val_5 = MyContainer.sync_resource.sync_resolve()
        assert val_5 == val_1


def check_sync_container_context() -> None:
    """Test sync provider resolution container_context."""
    with my_container_context(providers=[MyContainer.sync_resource]):
        val_1 = MyContainer.sync_resource.sync_resolve()
        val_2 = MyContainer.sync_resource.sync_resolve()
        assert val_1 == val_2
        with my_container_context(providers=[MyContainer.sync_resource]):
            val_3 = MyContainer.sync_resource.sync_resolve()
            assert val_3 != val_1

        val_4 = MyContainer.sync_resource.sync_resolve()
        assert val_4 == val_1
    with pytest.raises(RuntimeError):
        MyContainer.sync_resource.sync_resolve()


async def check_async_container_context() -> None:
    """Test async provider resolution container_context."""
    async with my_container_context(providers=[MyContainer.async_resource]):
        val_1 = await MyContainer.async_resource.async_resolve()
        val_2 = await MyContainer.async_resource.async_resolve()
        assert val_1 == val_2
        async with my_container_context(providers=[MyContainer.async_resource]):
            val_3 = await MyContainer.async_resource.async_resolve()
            assert val_3 != val_1

        val_4 = await MyContainer.async_resource.async_resolve()
        assert val_4 == val_1
    with pytest.raises(RuntimeError):
        await MyContainer.async_resource.async_resolve()


async def check_async_global_passing() -> None:
    with pytest.raises(RuntimeError):
        # TODO: This perhaps should not throw an exception because to just set an empty dict if no context was entered before.
        async with my_container_context(preserve_globals=True) as gs:
            assert gs
    my_global_resources = {"test_1": "test_1", "test_2": "test_2"}

    async with my_container_context(initial_context=my_global_resources):
        for key, item in my_global_resources.items():
            assert fetch_context_item(key) == item

        async with my_container_context(preserve_globals=True):
            for key, item in my_global_resources.items():
                assert fetch_context_item(key) == item

            async with my_container_context(preserve_globals=False):
                for key in my_global_resources:
                    assert fetch_context_item(key) is None


def check_sync_global_passing() -> None:
    with pytest.raises(RuntimeError):
        # TODO: This perhaps should not throw an exception because to just set an empty dict if no context was entered before.
        with my_container_context(preserve_globals=True) as gs:
            assert gs
    my_global_resources = {"test_1": "test_1", "test_2": "test_2"}

    with my_container_context(initial_context=my_global_resources):
        for key, item in my_global_resources.items():
            assert fetch_context_item(key) == item

        with my_container_context(preserve_globals=True):
            for key, item in my_global_resources.items():
                assert fetch_context_item(key) == item

            with my_container_context(preserve_globals=False):
                for key in my_global_resources:
                    assert fetch_context_item(key) is None


if __name__ == "__main__":
    asyncio.run(async_main())
    sync_main()
    check_sync_container_context()
    asyncio.run(check_async_container_context())
    asyncio.run(test_injected())
    asyncio.run(check_async_global_passing())
    check_sync_global_passing()
