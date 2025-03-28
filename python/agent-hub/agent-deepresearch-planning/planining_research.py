import json

from openai import OpenAI
from pydantic import BaseModel
from xml.etree import ElementTree as ET
from typing import List, Optional
import os
from dotenv import load_dotenv

from typing import List, Optional
from pydantic import BaseModel

class SubPlan(BaseModel):
    core_objective: str
    hypothesis: str
    design_thinking: str
    query_statement: List[str]
    data_sources: List[str]
    quantitative_analysis: str
    qualitative_analysis: str
    relationship_with_other_sub_plans: Optional[str] = None
    logical_connection_to_main_plan: str

class MainPlan(BaseModel):
    core_goal: str
    core_research_direction: str
    sub_plans: List[SubPlan]

class ResearchPlanOutput(BaseModel):
    main_plan: MainPlan

class MainPlanner:
    Main_Planner_PROMPT = """
Context: You are a senior research planning expert. Your task is to develop a detailed and logically structured research plan based on the user’s provided needs. The output must be directly in the JSON format that adheres to the following Pydantic class structure. Ensure that the JSON object you output is valid and does not contain any additional characters like \n, " or extra formatting.
```python

class SubPlan(BaseModel):
    core_objective: str
    hypothesis: str
    design_thinking: str
    query_statement: List[str]
    data_sources: List[str]
    quantitative_analysis: str
    qualitative_analysis: str
    relationship_with_other_sub_plans: Optional[str] = None
    logical_connection_to_main_plan: str

class MainPlan(BaseModel):
    core_goal: str
    core_research_direction: str
    sub_plans: List[SubPlan]

class ResearchPlanOutput(BaseModel):
    main_plan: MainPlan

```

Objective: To create a research plan that is logically structured, ensuring each section is detailed and adheres to the specified Pydantic class format. Ensure that you output the result as clean, structured JSON directly without escape sequences or any other extra formatting.
**Solution:**
- Understand the user's needs and core research goals.
- Break down the main research plan into 3 to 5 logically connected sub-plans.
- For each sub-plan, provide the necessary details including the core objective, hypothesis, design thinking, and the various research elements (data sources, analysis methods, relationships with other sub-plans).
- Ensure that the output is in JSON format, strictly following the structure defined by the Pydantic classes.

**Task:**
The task involves creating a structured research plan that includes:
1. A **main research plan** with a core goal and research direction.
2. **Sub-plans** that focus on different aspects or phases of the research.
3. Ensure each sub-plan includes:
   - core objective,
   - hypothesis,
   - design thinking,
   - query statement,
   - data sources,
   - quantitative and qualitative analysis,
   - relationships with other sub-plans (if any),
   - logical connection to the main plan.

**Action:**
Follow these steps:
1. Understand the user’s specific research needs and goals.
2. Define a **core goal** and **core research direction** for the **main plan**.
3. Break down the research into **3-5 sub-plans**, ensuring each sub-plan is logically connected to the main plan.
4. For each sub-plan, fill out all required details (core objective, hypothesis, etc.) in accordance with the structure outlined.
5. Provide the final research plan in the specified **JSON format**.

**Result:**
A JSON output that represents a detailed research plan, adhering to the structure defined by the Pydantic classes. This output will include a main plan and 3 to 5 sub-plans, each providing comprehensive details on the research approach, methodologies, and logical connections.
"""
    
    def __init__(self):
        self.client = self.create_openai_client()
        self.main_plan = None
    def create_openai_client(self):
        env_file = os.getenv('ENV_FILE', '.env.secret')
        if not os.path.exists(env_file):
            raise FileNotFoundError(f"未找到环境配置文件: {env_file}，请确保项目根目录存在该文件")
            
        load_dotenv(env_file)
        LLM_API_KEY = os.getenv("LLM_API_KEY")
        os.environ['OPENAI_API_KEY'] = LLM_API_KEY
        api_key = os.getenv("OPENAI_API_KEY") or os.getenv("LLM_API_KEY")
        if not api_key:
            raise ValueError("""
            未找到有效的API密钥配置，请按以下步骤操作：
            1. 在项目根目录创建.env.secret文件
            2. 添加以下内容：
               OPENAI_API_KEY=您的实际API密钥
               # 或
               LLM_API_KEY=您的实际API密钥
            """)
            
        base_url = os.getenv("LLM_BASE_URL")
        return OpenAI(api_key=api_key, base_url=base_url)

    def generate_main_plan(self, user_query: str) :
        try:
            response = self._call_llm(user_query)
            response = json.loads(response.replace("```json", "").replace("```", ""))
            self.main_plan = MainPlan(**response)
            return self.main_plan
        except Exception as e:
            return self._fallback_plan(user_query)

    def _call_llm(self, query: str, retries=3,temperature:float=0.75) -> str:
        for attempt in range(retries):
            try:
                response = self.client.chat.completions.create(
                    model=os.getenv("LLM_MODEL_NAME",'gpt-4o'),
                    messages=[
                        {"role": "system", "content": self.Main_Planner_PROMPT},
                        {"role": "user", "content": query}
                    ],
                    temperature=temperature,
                )
                return response.choices[0].message.content
            except Exception:
                if attempt == retries - 1:
                    raise
    def _search_web(self):
        pass
    def _run_sub_plan(self,sub_plan:SubPlan):


    def _parse_node(self, element: ET.Element) :
        # 解析主计划节点
        pass

    def _fallback_plan(self, query: str) :
        pass

if __name__ == "__main__":
    planner = MainPlanner()
    try:
        plan = planner.generate_main_plan("如何评估AI对就业市场的影响？")
        print(plan.model_dump_json(indent=2, exclude_unset=True))
    except Exception as e:
        print(f"研究计划生成失败: {str(e)}")
        print("请检查：1.环境变量配置 2.API服务可用性 3.网络连接")
