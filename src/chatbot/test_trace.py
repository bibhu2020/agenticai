import os
import time
from dotenv import load_dotenv
import logging

# Load envs
load_dotenv(override=True)

# Enable debug logs
import sys
logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
logging.getLogger("langfuse").setLevel(logging.DEBUG)


import langfuse
from langfuse import observe

# 1. Print config to verify keys
print(f"Host: {os.environ.get('LANGFUSE_HOST')}")
print(f"Public Key: {os.environ.get('LANGFUSE_PUBLIC_KEY')}")

# 2. Define observed function
@observe(name="test-trace-script")
def run_test():
    print("Executing observed function...")
    time.sleep(0.1)
    return "Test successful"

# 3. Run
run_test()

# 4. Flush / Wait
print("Waiting for background upload...")
time.sleep(3)

try:
    from langfuse import Langfuse
    # Try to flush using a new client instance (hoping for shared state or just to test connection)
    client = Langfuse()
    client.flush()
    print("Flush called on client instance.")
except Exception as e:
    print(f"Flush failed: {e}")

print("Script finished.")


