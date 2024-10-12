
import contextvars
import time
from uuid import uuid4

from that_depends.providers.base import ResourceContext

my_var = contextvars.ContextVar("MY_CONTEXT_VAR")



if __name__ == "__main__":
    # Trials | 1 Context | 10 Context | 100 Context | 1000 Context
    # 100 | 1.5974044799804688e-05 | 3.719329833984375e-05 | 9.012222290039062e-05 | 3.886222839355469e-05
    # 1000000 | 0.4496629238128662 | 0.47083497047424316 | 0.4283409118652344 | 0.43338894844055176
    trials = 10000000
    context_size  =  1000
    tokens = []
    context = {}
    for i in range(context_size):
        context[uuid4()] = ResourceContext(is_async=False)
    
    start_time = time.time()
    # setup
    for _ in range(trials):
        tokens.append(my_var.set(context))
        
    tokens.reverse()
    for token in tokens:
        my_var.reset(token)
        
    print(f"{time.time() - start_time}")