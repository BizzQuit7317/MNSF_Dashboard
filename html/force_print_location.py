import builtins
import inspect
import sys

# Save the original print function
original_print = builtins.print

def debug_print(*args, **kwargs):
    # Get the caller's stack frame
    stack = inspect.stack()
    # Frame[1] is the caller of debug_print
    if len(stack) > 1:
        frame = stack[1]
        filename = frame.filename
        lineno = frame.lineno
        location_info = f"[{filename}:{lineno}]"
    else:
        location_info = "[unknown]"

    # Prepend location info to the original print output
    original_print(location_info, *args, **kwargs)

# Override the built-in print
builtins.print = debug_print
