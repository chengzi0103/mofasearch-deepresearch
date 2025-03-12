import json
from pathlib import Path

from dotenv import load_dotenv
from mofa.utils.ai.conn import generate_json_from_llm
from mofa.utils.files.read import read_yaml
from pydantic import BaseModel, Field
from typing import Optional
from openai import OpenAI

import os
# class LLMGeneratedRequire(BaseModel):
#     """
#     Schema for structured LLM output containing technical documentation and configuration
#     """
#     readme: Optional[str] = Field(
#         default=None,
#         json_schema_extra={
#             "description": "GitHub-standard README content with installation, usage, and contribution guidelines",
#             "example": """# Project\n\n## Installation\n```bash\npip install ...\n```"""
#         }
#     )
#
#     toml: Optional[str] = Field(
#         default=None,
#         json_schema_extra={
#             "description": "PEP 621-compliant pyproject.toml configuration content",
#             "example": """[tool.poetry]\nname = "..."\n"""
#         }
#     )
#
#     generation_time: str = Field(
#         default_factory=lambda: datetime.now().isoformat(),
#         json_schema_extra={
#             "description": "ISO 8601 timestamp of generation",
#             "example": "2023-10-01T12:00:00Z"
#         }
#     )
def read_markdown_file_basic(file_path:str):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            markdown_text = f.read()
            return markdown_text
    except FileNotFoundError:
        print(f"错误：文件未找到：{file_path}")
        return None
    except Exception as e:
        print(f"读取文件时发生错误：{e}")
        return None
agent_config_dir_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), )
config_yml = read_yaml(agent_config_dir_path + f'/configs/agent.yml')
prompt = config_yml.get('agent', {}).get('prompt', '')
readme_files = config_yml.get('agent', {}).get('connectors', None)
readme_data = {}
if readme_files is not None:
    for file_path in readme_files:
        readme_data.update({Path(file_path).parent.name: read_markdown_file_basic(file_path=file_path)})
load_dotenv(dotenv_path='.env.secret')
if os.getenv('LLM_API_KEY') is not None:
    os.environ['OPENAI_API_KEY'] = os.getenv('LLM_API_KEY')

if os.getenv('LLM_BASE_URL', None) is None:
    client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])
else:
    client=OpenAI(api_key=os.environ['OPENAI_API_KEY'], base_url=os.getenv('LLM_BASE_URL'), )

user_input = "我想知道关于deepseek的相关信息"
messages = [
            {"role": "system",
             "content": prompt + "  readme_data: " + json.dumps(readme_data)},
            {"role": "user", "content":  user_input},
        ]
response = client.chat.completions.create(
                    model=os.getenv('LLM_MODEL_NAME','gpt-4o'),
                    messages=messages,stream=True,)
is_thinking = False
reasoning_content = ""
content = ""
for chunk in response:
    if chunk.choices[0].delta.reasoning_content:
        think_data = chunk.choices[0].delta.reasoning_content
        # print("<think>  : ",think_data )
        if think_data is not None:
            reasoning_content += chunk.choices[0].delta.reasoning_content  # **thinking part**
    else:
        data = chunk.choices[0].delta.content
        # print("content :",data)
        if data is not None:
            content += chunk.choices[0].delta.content
print("<think> : ",reasoning_content)
print('-------------')
print("<content> ",content)