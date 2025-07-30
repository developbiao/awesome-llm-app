# -*- coding: utf-8 -*-
#
"""
Test Qwen VL model
"""

import json
import os
import sys
from pathlib import Path
import time
from venv import logger


current_dir = os.path.dirname(os.path.abspath(__file__))
root_dir = os.path.dirname(current_dir)
sys.path.insert(0, root_dir)

import getpass

from agno.agent import Agent
from agno.media import File, Image
from agno.models.openai.like import OpenAILike


api_key = os.getenv("DASHSCOPE_API_KEY")
if not api_key:
    api_key = getpass.getpass("Enter your DashScope API key: ")
    os.environ["DASHSCOPE_API_KEY"] = api_key

def get_model_provider(model_id):
    return OpenAILike(
        id=model_id,
        base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        api_key=api_key,
        temperature=0.3,
    )

def run_agent(agent: Agent, prompt: str, files: list[File] = None, expect_json: bool = False) -> str:
    run = agent.run(prompt, files=files)
    if run.content:
        print(f"LLM response: {run.content}")
        content = run.content
        if expect_json:
            content = content.replace("```json", "").replace("```", "")
            return json.loads(content)
        return content
    else:
        print("LLM response is empty")
        raise ValueError("LLM response is empty")

def test_qwen_vl_model():
    model_id = "qwen-vl-plus"
    agent = Agent(model=get_model_provider(model_id), markdown=True)
    prompt = "请将图片中的内容以markdown格式输出，不要包含任何其他内容"
    # image_url = "https://intelligence.pre.sywldrmd.com/public/2024/12/25/40b81f78-9ec4-4f9c-9a9a-d5c6c766e6a9.jpg"
    # image = Image(url=image_url)

    # image input bytes content
    image_path = Path("sample/0001.png")
    # Read the image file content as bytes
    image_bytes = image_path.read_bytes()
    image = Image(content=image_bytes)
    start_time = time.time()
    agent.print_response(prompt, images=[image], stream=False)
    # Spend time keep 2 decimal places
    print(f"Time taken: {time.time() - start_time:.2f} seconds")

if __name__ == "__main__":
    test_qwen_vl_model()