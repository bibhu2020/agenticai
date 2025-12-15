from ddgs import DDGS

print("Testing DDGS news keys...")
with DDGS() as ddgs:
    results = list(ddgs.news("AAPL", max_results=1))
    if results:
        print(f"Keys found: {results[0].keys()}")
        print(f"Sample result: {results[0]}")
    else:
        print("No results found.")
