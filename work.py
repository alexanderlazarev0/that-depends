









from contextlib import asynccontextmanager, contextmanager
import inspect
import typing

P = typing.ParamSpec("P")
T = typing.TypeVar("T")

def inject(
    func: typing.Callable[P, T],
) -> typing.Callable[P, T]:
    if inspect.iscoroutinefunction(func):
        print("async")
        return typing.cast(typing.Callable[P, T], func)
    print("sync")
    return func
@contextmanager
def sync_context_iterator() -> typing.Iterator[str]:
    print("ENTERING SYNC MANAGER")
    yield ""
    
@asynccontextmanager
async def async_context_iterator() -> typing.AsyncIterator[str]:
    print("ENTERING ASYNC MANAGER")
    yield ""
    
def manager_chooser() -> typing.Callable[[typing.Callable[P, T]], typing.Callable[P, T]]:
    #if inspect.iscoroutinefunction():
    #    return typing.cast(typing.Callable[[typing.Callable[P, T]], typing.Callable[P, T]] ,async_context_iterator())
    return sync_context_iterator()
    
    

@manager_chooser()
@inject
def some_func() -> str:
    return "str"



if __name__  == "__main__":
    some_func()