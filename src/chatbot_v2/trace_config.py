# trace_config.py
import openai
from langsmith.wrappers import wrap_openai
import os

print("🔌 APPLYING LANGSMITH TRACE PATCH...")

# 1. Save original classes
_OriginalOpenAI = openai.OpenAI
_OriginalAsyncOpenAI = openai.AsyncOpenAI

# 2. Define the shim
def PatchedOpenAI(*args, **kwargs):
    print("✨ Creating Wrapped OpenAI Client (Sync)") # Debug print
    client = _OriginalOpenAI(*args, **kwargs)
    return wrap_openai(client)

def PatchedAsyncOpenAI(*args, **kwargs):
    print("✨ Creating Wrapped OpenAI Client (Async)") # Debug print
    client = _OriginalAsyncOpenAI(*args, **kwargs)
    return wrap_openai(client)

# 3. Apply patch
openai.OpenAI = PatchedOpenAI
openai.AsyncOpenAI = PatchedAsyncOpenAI

from langsmith import traceable

# You can't decorate the class directly with @traceable, 
# but you can use this helper to wrap all methods:

def instrument_class(cls):
    for attr_name, attr_value in cls.__dict__.items():
        if callable(attr_value) and not attr_name.startswith("__"):
            setattr(cls, attr_name, traceable(attr_value, run_type="tool"))
    return cls

