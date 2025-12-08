from ddgs import DDGS
import json

with DDGS() as ddgs:
    print("--- TESTING PARAMETERS ---")
    try:
        print("Testing timelimit='d'...")
        results = list(ddgs.text("python", max_results=1, timelimit="d"))
        print(f"Success: {len(results)} results")
    except Exception as e:
        print(f"Failed timelimit: {e}")

    try:
        print("Testing region='us-en'...")
        results = list(ddgs.text("python", max_results=1, region="us-en"))
        print(f"Success: {len(results)} results")
    except Exception as e:
        print(f"Failed region: {e}")
