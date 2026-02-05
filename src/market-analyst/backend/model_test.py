import os
import asyncio
from dotenv import load_dotenv
load_dotenv()
from autogen_ext.models.openai import OpenAIChatCompletionClient

import sys
current_dir = os.path.dirname(os.path.abspath(__file__))
repo_root = os.path.abspath(os.path.join(current_dir, "../../../"))
if repo_root not in sys.path:
    sys.path.append(repo_root)

async def main():
    try:
        from common.utility.autogen_model_factory import AutoGenModelFactory
        client = AutoGenModelFactory.get_model(provider="openai", model_name="gpt-4o")
        from autogen_core.models import UserMessage
        resp = await client.create([UserMessage(content="Say hello", source="user")])
        print(f"Type: {type(resp)}")
        print(f"Response: {resp.content}")
    except Exception as e:
        import traceback
        print(f"DEBUG_ERROR: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
