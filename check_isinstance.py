import time
import typing

from that_depends import providers


async def some_async_iterator() -> typing.AsyncIterator[str]:
    yield str


def some_sync_func() -> typing.Iterator[str]:
    return str


correct_provider: providers.ContextResource = providers.ContextResource(some_async_iterator)
incorrect_provider: providers.Factory = providers.Factory(some_sync_func)


if __name__ == "__main__":
    # Using isinstance():
    # Trials | Correct Seconds | Incorrect Seconds
    # 100 | 7.867813110351562e-06 s | 4.792213439941406e-05 s
    # 1 000 | 8.296966552734375e-05 s | 0.0004382133483886719 s
    # 1 000 000 | 0.0984947681427002 s | 0.41033482551574707 s
    # 100 000 000 | 9.722477197647095 s | TimeOut

    trials = 1000000
    start_time = time.time()
    for _ in range(trials):
        isinstance(correct_provider, providers.ContextResource)
    print(f"{time.time() - start_time}")

    start_time = time.time()
    for _ in range(trials):
        isinstance(incorrect_provider, providers.ContextResource)
