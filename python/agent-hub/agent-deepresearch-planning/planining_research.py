import json
from firecrawl import FirecrawlApp
from openai import OpenAI
from xml.etree import ElementTree as ET
import os
from dotenv import load_dotenv
from typing import List, Optional, Any
from pydantic import BaseModel



class SubPlan(BaseModel):
    core_objective: str
    hypothesis: str
    design_thinking: List[str]
    query_statement: List[str]
    data_sources: List[str]
    quantitative_analysis: str
    qualitative_analysis: str
    relationship_with_other_sub_plans: Optional[str] = None
    logical_connection_to_main_plan: str
    sub_id:str
    source_urls:Any = None
    source_data:Any = None
    summary:Any = None
    modification_reason: str = None  # 新增参数，表示修改原因


class MainPlan(BaseModel):
    core_goal: str
    core_research_direction: str
    sub_plans: List[SubPlan]

class ResearchPlanOutput(BaseModel):
    main_plan: MainPlan


class FireCrawl:
    def __init__(self, api_key: str=None,env_file:str='.env.secret',crawl_params:dict=None):
        if api_key is None:
            load_dotenv(env_file)
            api_key = os.getenv("FIRECRAWL_API_KEY")
        self.crawl = FirecrawlApp(api_key=api_key)
        if crawl_params is None:
            crawl_params =  {
    "maxDepth": 1,  # Number of research iterations
    "timeLimit": 180,  # Time limit in seconds
    "maxUrls": 3  # Maximum URLs to analyze
}
        self.crawl_params = crawl_params

    def on_activity(self,activity):
        print(f"[{activity['type']}] {activity['message']}")

    def deep_research(self, query: str,):
        results = self.crawl.deep_research(query=query,
        params=self.crawl_params,on_activity=self.on_activity)
        source_data = results['data']['sources']
        analysis_data = results['data']['finalAnalysis']
        return source_data,analysis_data

class MainPlanner:
    Main_Planner_PROMPT = """
Context: You are a senior research planning expert. Your task is to develop a detailed and logically structured research plan based on the user’s provided needs. The output must be directly in the JSON format that adheres to the following Pydantic class structure. Ensure that the JSON object you output is valid and does not contain any additional characters like \n, " or extra formatting.

Objective: To create a research plan where the main plan and its constituent sub-plans are logically interconnected and collectively aim to achieve the overall research goal. Ensure that each sub-plan builds upon previous ones (where applicable) and contributes a necessary component to the final research outcome. Output the result as clean, structured JSON directly without escape sequences or any other extra formatting.

Solution:

Understand the user's needs and core research goals.
Break down the main research plan into 3 to 5 logically connected sub-plans, ensuring each sub-plan's objective directly contributes to the overarching research goal.
For each sub-plan, provide the necessary details including the core objective (clearly stating its role in the overall research), hypothesis (relevant to the sub-plan's objective and the main research goal), design thinking (explaining how this sub-plan will contribute to the larger research narrative), and the various research elements (data sources, analysis methods, relationships with other sub-plans – explicitly detailing how this sub-plan builds upon or informs others).
Ensure that the output is in JSON format, strictly following the structure defined by the Pydantic classes.
Task:
The task involves creating a structured research plan that includes:

A main research plan with a core goal and research direction.
Sub-plans that focus on different aspects or phases of the research, with a clear and demonstrable connection to each other and the main plan.
Ensure each sub-plan includes:
core objective (clearly indicating its contribution to the main research goal and potentially its dependency on or influence over other sub-plans),
hypothesis (focused on the specific aspect addressed by the sub-plan and its relevance to the broader research question),
design thinking (outlining the rationale and methodology for this specific sub-plan in the context of the entire research project),
query statement,
data sources,
quantitative and qualitative analysis,
relationships with other sub-plans (explicitly describe how this sub-plan relates to and interacts with other sub-plans, e.g., "This sub-plan will provide foundational data for Sub-plan 3," or "The findings of Sub-plan 2 will be used to refine the hypothesis of this sub-plan."),
logical connection to the main plan (reiterate how this sub-plan directly contributes to achieving the core goal of the main research plan).
Action:
Follow these steps:
Understand the user’s specific research needs and goals.
Define a core goal and core research direction for the main plan.
Break down the research into 3-5 sub-plans, ensuring each sub-plan is logically connected to the main plan and, where applicable, to each other in a sequential or dependent manner.
For each sub-plan, fill out all required details (core objective, hypothesis, etc.) in accordance with the structure outlined, paying particular attention to explicitly defining the relationships between sub-plans and their individual contributions to the main research goal.
Provide the final research plan in the specified JSON format.

```python
class SubPlan(BaseModel):
    core_objective: str
    hypothesis: str
    design_thinking: List[str]
    query_statement: List[str]
    data_sources: List[str]
    quantitative_analysis: str
    qualitative_analysis: str
    relationship_with_other_sub_plans: Optional[str] = None
    logical_connection_to_main_plan: str
    sub_id:str

class MainPlan(BaseModel):
    core_goal: str
    core_research_direction: str
    sub_plans: List[SubPlan]

class ResearchPlanOutput(BaseModel):
    main_plan: MainPlan
```
"""
    Sub_Plan_Summary_PROMPT = """
    Context: You have been provided with the details of a specific sub-plan within a larger research project focused on [Placeholder: Main Plan's Core Goal]. This sub-plan aims to [Placeholder: Sub-plan's Core Objective] and seeks to answer the following question(s) or explore the following area(s): [Placeholder: Sub-plan's Specific Query Statement(s) or Focus Areas]. You have also been provided with the results of your research or data gathering efforts related to this sub-plan, which may include search results, extracted data, or preliminary analysis.
    
    Objective: Your goal is to generate a concise and insightful summary of the key findings and insights derived from the provided research results, directly addressing the objective and query/focus of this specific sub-plan.
    
    Task: Based on the provided information about the sub-plan and its corresponding research results, create a summary that includes the following elements:
    
    Sub-plan Objective Alignment: Clearly state how the findings from the research results directly relate to and contribute to the stated objective of this sub-plan: [Placeholder: Sub-plan's Core Objective].
    Answering the Query/Focus: Summarize the key answers, insights, or trends observed in the research results that address the sub-plan's specific question(s) or focus areas: [Placeholder: Sub-plan's Specific Query Statement(s) or Focus Areas].
    Key Supporting Evidence: Briefly mention the types of data or evidence from your research results that support your summary points. You don't need to provide exhaustive details, but indicate the nature of the supporting information.
    Contribution to Main Goal: Explain how the potential findings or insights from this sub-plan contribute to the overarching [Placeholder: Main Plan's Core Goal] of the main research project.
    Potential Next Steps or Implications: Briefly suggest any potential next steps in the research or the implications of these findings for the overall project.
    Action:
    
    Carefully review the provided details of the specific sub-plan, paying close attention to its [Placeholder: Sub-plan's Core Objective] and [Placeholder: Sub-plan's Specific Query Statement(s) or Focus Areas].
    Thoroughly analyze the provided research results (e.g., search results, data extracts, analysis summaries) to identify the most relevant findings and insights.
    Synthesize the information to address each of the points outlined in the Task section. Ensure that your summary directly links the research results back to the sub-plan's objectives and questions.
    Present your summary in a clear, concise, and well-organized manner.

    """
    Sub_Plan_Update = """
    Objective: Your sole objective is to evaluate the Next Sub-plan based on the details of the Current Sub-plan and determine if the Next Sub-plan requires modification to logically follow and contribute effectively to the overall research project. The final output MUST be a single JSON object representing the Next Sub-plan (modified or not), strictly adhering to the provided SubPlan Pydantic class structure. If modification is needed, the suggested changes should be reflected in the JSON output, along with a clear modification_reason for each change. If no modification is needed, the original Next Sub-plan should be outputted in JSON format with a modification_reason indicating why no changes were made.
Task: Based on the provided details of the Current Sub-plan and the Next Sub-plan, perform the following:
Analyze the Current Sub-plan: Understand the core_objective, hypothesis, design_thinking, and query_statement of the Current Sub-plan.
Evaluate the Next Sub-plan: Compare the core_objective, hypothesis, design_thinking, query_statement, data_sources, quantitative_analysis, qualitative_analysis, and relationship_with_other_sub_plans of the Next Sub-plan against the details of the Current Sub-plan to assess its logical flow, relevance, and potential impact on the main research goal.
Generate JSON Output for the Next Sub-plan:
If modifications are deemed necessary: Construct a JSON object representing the modified Next Sub-plan. This JSON object must include all fields of the SubPlan class, with the proposed new content for the modified fields and a clear and concise modification_reason explaining why each change was made. The sub_id must remain the same as the original Next Sub-plan.
If no modifications are deemed necessary: Construct a JSON object representing the original Next Sub-plan. This JSON object must include all fields of the SubPlan class, with the original content and a modification_reason field set to explain why no changes were needed (e.g., "No modification needed based on the logical flow from the Current Sub-plan").
Action:

Carefully review the provided JSON objects representing both the Current Sub-plan and the Next Sub-plan.
Analyze the logical progression from the Current Sub-plan to the Next Sub-plan, considering the research questions and overall goal: [Placeholder: Main Plan's Core Goal].
Determine if the Next Sub-plan, in its current form, is a logical and effective continuation of the research. Consider factors such as whether it builds upon the findings or objectives of the Current Sub-plan, addresses a relevant next step in the research, and utilizes appropriate methodologies and data sources.
Construct a single JSON object representing the evaluated (and potentially modified) Next Sub-plan, strictly adhering to the SubPlan Pydantic class structure. Ensure the modification_reason field accurately reflects the outcome of your evaluation.
```python
class SubPlan(BaseModel):
    core_objective: str
    hypothesis: str
    design_thinking: List[str]
    query_statement: List[str]
    data_sources: List[str]
    quantitative_analysis: str
    qualitative_analysis: str
    relationship_with_other_sub_plans: Optional[str] = None
    logical_connection_to_main_plan: str
    sub_id:str
    summary:Any = None
    modification_reason: str = None  # 新增参数，表示修改原因
```
    """
    def __init__(self):
        self.client = self.create_openai_client()
        self.main_plan = None
        self.fire_crawl = FireCrawl()
        self.old_main_plan = None
        self.retry_num = 2
    def create_sub_plan_summary(self, sub_plan:SubPlan, sub_plan_source_data:list, ):
        messages = [
            {"role": "system", "content": self.Sub_Plan_Summary_PROMPT},
            {"role": "user", "content": json.dumps(sub_plan_source_data)},
            {"role": "system", "content": json.dumps({'core_goal':self.main_plan.core_goal,'core_research_direction':self.main_plan.core_research_direction,'sub_plan':sub_plan.json()})},
        ]
        result = self._call_llm(messages=messages)
        return  result

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
    def remove_json_format(self, response: str) -> str:
        return response.replace("```json", "").replace("```", "")
    def generate_main_plan(self, user_query: str) :
        try:
            response = self._call_llm(user_query)
            response = json.loads(response.replace("```json", "").replace("```", ""))
            self.main_plan = MainPlan(**response['main_plan'])
            self.old_main_plan = response
            return self.main_plan
        except Exception as e:
            return self._fallback_plan(user_query)
    def update_sub_plan(self, sub_plan:SubPlan, next_sub_plan:SubPlan,):
        messages = [
            {"role": "system", "content": self.Sub_Plan_Update},
            {"role": "user", "content": "This is the next plan  : "+next_sub_plan.json()},
            {"role": "system", "content": "This is the current plan  : "+sub_plan.json()},
            {"role": "system", "content": "This is the overall plan  : "+ json.dumps(self.old_main_plan)},
        ]
        result = self._call_llm(messages=messages)
        return  self.remove_json_format(result)
    def _call_llm(self, query: str='', retries:int=3,temperature:float=0.75,messages:list[dict]=None) -> str:
        if messages is None:
            messages = [
                {"role": "system", "content": self.Main_Planner_PROMPT},
                {"role": "user", "content": query}
            ]
        for attempt in range(retries):
            try:
                response = self.client.chat.completions.create(
                    model=os.getenv("LLM_MODEL_NAME",'gpt-4o'),
                    messages=messages,
                    temperature=temperature,
                )
                return response.choices[0].message.content
            except Exception:
                if attempt == retries - 1:
                    raise
    def _search_web(self):
        pass

    def run_sub_plan(self):
        plan_results = []
        for index_num,sub_plan in enumerate(self.main_plan.sub_plans):
            sub_queries = sub_plan.query_statement
            sub_plan_results = []
            for sub_query in sub_queries:
                source_data,analysis_data = self.fire_crawl.deep_research(query=sub_query)
                query_data = {'source_urls':source_data,'analysis_data':analysis_data}
                plan_results.append(query_data)
                sub_plan_results.append(query_data)
                sub_plan.source_urls = source_data
                sub_plan.source_data = analysis_data
            print(sub_plan_results)
            sub_plan.summary = self.create_sub_plan_summary(sub_plan=sub_plan, sub_plan_source_data=sub_plan_results)
            if index_num != len(self.main_plan.sub_plans) - 1:
                try:
                    new_sub_plan = self.update_sub_plan(sub_plan=sub_plan, next_sub_plan=self.main_plan.sub_plans[index_num + 1])
                    self.main_plan.sub_plans[index_num + 1] = SubPlan(**json.loads(new_sub_plan))
                except Exception as e :
                    for attempt in range(self.retry_num):
                        try:
                            new_sub_plan = self.update_sub_plan(sub_plan=sub_plan, next_sub_plan=self.main_plan.sub_plans[index_num + 1])
                            self.main_plan.sub_plans[index_num + 1] = SubPlan(**json.loads(new_sub_plan))
                            break
                        except Exception as e:
                            if attempt == self.retry_num - 1:
                                print(f"Error in updating sub plan: {e}")
            break
        return plan_results


if __name__ == "__main__":
    planner = MainPlanner()
    try:
        planner.generate_main_plan("如何评估AI对就业市场的影响？")
        result = planner.run_sub_plan()
        sub_plan = """[{'source_data': [{'url': 'http://www.50forum.org/home/article/detail/id/11133.html',
    'title': '人工智能对劳动力市场的影响 - 中国经济50人论坛',
    'description': '人工智能主要对认知型的工作任务和工作岗位产生影响，且对处于较高发展阶段的国家和具有较高人力资本水平的劳动力产生更大影响。基于中国城市劳动力调查（ ...',
    'icon': ''},
   {'url': 'https://sle.ajcass.com/Admin/UploadFile/Issue/201911110002/2024/3//20240313105620WU_FILE_0.pdf',
    'title': '[PDF] 人工智能发展对中国制造业就业的影响 - 劳动经济研究',
    'description': '人工智能对就业表现出替代和创造双重效. 应: 一方面, 随着劳动力成本上升, “机器换人” 势不可挡, 人工智能可能通过提高劳. 动生产率和重塑企业生产过程压缩就业需求(尹志锋 ...',
    'icon': ''},
   {'url': 'http://www.news.cn/globe/20250121/1b72ab9c82534a8a9d479b2a513ef127/c.html',
    'title': '各国如何应对AI业变 - 新华网',
    'description': '根据国际货币基金组织（IMF）的研究，AI将对全球近40%的就业岗位产生影响，其中发达经济体约60%的工作岗位受到AI影响。发达国家在AI应用方面具备显著优势，劳动 ...',
    'icon': ''},
   {'url': 'http://www.tisi.org/19576/',
    'title': 'AI如何影响就业市场？这几份国际报告的判断跟直觉不一样 - 腾讯研究院',
    'description': '92%的受访者认为采用信息通信技术可以提高效率 （知识共享、绩效管理等） ，73%的受访者认为可以满足日益增长的公共服务需求 （包括公开信息获取、法律咨询等） ...',
    'icon': ''},
   {'url': 'https://docs.feishu.cn/v/wiki/MeNtwOGf9iUW4uk7LP0c64EOnNb/ab',
    'title': '人工智能采用对美国通勤区不同行业就业的影响差异',
    'description': '从制造业到服务业，从医疗保健到金融领域，AI 的身影无处不在。然而，这种技术的快速发展也引发了人们对就业市场的担忧。一些人认为，人工智能将取代大量的人类工作，导致失业率 ...',
    'icon': ''},
   {'url': 'https://sle.ajcass.com/Admin/UploadFile/Issue/201911110002/2024/3//20240313105620WU_FILE_0.pdf',
    'title': '[PDF] 人工智能发展对中国制造业就业的影响 - 劳动经济研究',
    'description': '人工智能对就业表现出替代和创造双重效 应: 一方面, 随着劳动力成本上升, “机器换人” 势不可挡, 人工智能可能通过提高劳 动生产率和重塑企业生产过程压缩就业需求(尹志锋 ...',
    'icon': ''},
   {'url': 'http://www.50forum.org/home/article/detail/id/11133.html',
    'title': '人工智能对劳动力市场的影响 - 中国经济50人论坛',
    'description': '基于中国城市劳动力调查（CULS）数据，本文发现：专业技术人员是受人工智能影响最大的群体，而制造业工人受到的影响较小。人工智能对劳动力市场的整体影响还受 ...',
    'icon': ''},
   {'url': 'https://journal.bjut.edu.cn/bjgydxxbskb/cn/article/pdf/preview/10.12120/bjutskxb20200574.pdf',
    'title': '[PDF] 人工智能技术对制造业就业的影响效应分析 - 北京工业大学学报',
    'description': '其中,AI 技术应用比例对制造企业用工. 数量变化的影响最大,它对用工数量增加和不变均. 表现出显著的负向影响,这说明随着AI 技术应用比. 例的增加,制造企业 ...',
    'icon': ''},
   {'url': 'https://www2.deloitte.com/content/dam/Deloitte/cn/Documents/energy-resources/deloitte-cn-eri-manufacturing-artificial-intelligence-innovation-application-development-report-zh-211015.pdf',
    'title': '[PDF] 制造业+人工智能创新应用发展报告 - Deloitte',
    'description': '中国制造业转型升级为中国人工智能发展提供广阔平 台。 一方面，低技术含量(第二产业、处理常规/可预测/ 可编程任务)的工作将首先被人工智能替代。 中国制造业 在转型升级 ...',
    'icon': ''},
   {'url': 'https://alj.com/zh-hans/perspective/%E5%8C%BA%E5%9D%97%E4%B8%8A%E7%9A%84%E5%B7%A5%E4%BD%9C%E4%BA%BA%E6%95%B0%EF%BC%9Fai-%E9%9D%A9%E5%91%BD%E8%A2%AD%E6%9D%A5/',
    'title': '人工智能对岗位的影响',
    'description': '根据麦肯锡《2022 年人工智能状况报告》调查[5]，2017 年至2022 年，AI 采用率增加了一倍多，50% 的受访者至少在一个业务领域采用了AI。每个组织的AI 功能 ...',
    'icon': 'https://alj.com/app/themes/alj/assets/favicon.png'},
   {'url': 'http://www.50forum.org/home/article/detail/id/11133.html',
    'title': '人工智能对劳动力市场的影响 - 中国经济50人论坛',
    'description': '人工智能对劳动力市场的整体影响还受一国就业结构、工作任务构成、技术渗透率和法律规制的影响。因此，相比美国，从短期来看，人工智能不太可能对中国的整体 ...',
    'icon': ''},
   {'url': 'http://www.xinhuanet.com/globe/20250121/1b72ab9c82534a8a9d479b2a513ef127/c.html',
    'title': '各国如何应对AI业变 - 新华网',
    'description': '根据国际货币基金组织（IMF）的研究，AI将对全球近40%的就业岗位产生影响，其中发达经济体约60%的工作岗位受到AI影响。发达国家在AI应用方面具备显著优势，劳动 ...',
    'icon': ''},
   {'url': 'https://www.acem.sjtu.edu.cn/ueditor/jsp/upload/file/20210206/1612621349892005365.pdf',
    'title': '[PDF] 数字技术对服务业就业的双向影响 - 上海交通大学安泰经济与管理学院',
    'description': '数字技术对各个行业的再造，使得劳动者的工作维 度和工作方式不断增加与延伸。 【内容摘要】 尽管自动化数字设备会毁灭制造业的低端岗位，但由于数字技术设 ...',
    'icon': ''},
   {'url': 'https://www.stcn.com/article/detail/1617914.html',
    'title': '【头条评论】人工智能将从两方面影响人类职业 - 证券时报',
    'description': '就冲击传统职业而言，人工智能与自动化技术的普及，取代了重复性高的工作，减少了低技能的职位。以客服与\u200c文员为例，包括律师的助理在内，AI语音识别和聊天 ...',
    'icon': ''},
   {'url': 'http://www.news.cn/tech/20231117/21deb8a618564148a3d842d1f1875686/c.html',
    'title': '人工智能为美欧就业市场带来新“变量” - 新华网',
    'description': '随着人工智能（AI）技术的提升和相关应用的增加，美欧就业市场受到错综复杂的影响。业界预计，随着“人机协作”磨合改进后，新的工种和人才将令就业市场更加活跃， ...',
    'icon': ''}],
  'analysis_data': '# 不同行业AI技术采用率如何影响就业总量变化研究报告\n\n## 摘要\n本报告旨在探讨不同行业中人工智能（AI）技术的采用率如何影响就业总量的变化。随着AI技术的快速发展，各行业的企业纷纷引入AI以提高效率和降低成本。然而，AI的广泛应用也引发了对就业市场的担忧，尤其是低技能岗位的消失。通过对相关数据的分析，我们将探讨AI技术的采用对就业的正面和负面影响，并提出相应的政策建议。\n\n## 1. 引言\n人工智能技术的迅猛发展正在改变全球经济的运作方式。根据国际劳工组织（ILO）的报告，AI技术的引入可能会导致某些行业的就业岗位减少，但同时也会创造新的就业机会（ILO, 2023）。本研究将分析不同行业中AI技术的采用率及其对就业总量的影响。\n\n## 2. AI技术的行业应用现状\n根据最新的研究数据，不同行业对AI技术的采用率存在显著差异。以下是一些主要行业的AI技术采用情况：\n\n- **制造业**：制造业是AI技术应用最广泛的行业之一，采用率达到60%。AI在生产线上的应用提高了生产效率，但也导致了部分低技能岗位的消失（50Forum, 2025）。\n- **金融服务**：金融行业的AI采用率为55%，主要用于风险评估和客户服务。尽管AI提高了服务效率，但也引发了对传统银行岗位的担忧（News.cn, 2025）。\n- **医疗健康**：医疗行业的AI采用率为45%，AI在疾病诊断和治疗方案制定中的应用正在逐步增加。虽然AI可以提高医疗服务的质量，但也可能导致某些医疗岗位的减少（TISI, 2025）。\n- **零售业**：零售行业的AI采用率为40%，主要用于库存管理和客户分析。AI的引入虽然提高了运营效率，但也可能影响到销售人员的就业（AJCASS, 2024）。\n\n## 3. AI技术对就业总量的影响\n### 3.1 正面影响\n- **新岗位的创造**：AI技术的引入虽然可能导致某些岗位的消失，但也会创造新的岗位。例如，数据分析师、AI工程师和机器学习专家等新兴职业的需求正在增加（50Forum, 2025）。\n- **提高生产力**：AI技术的应用可以显著提高企业的生产力，从而推动经济增长，进而可能创造更多的就业机会（News.cn, 2025）。\n\n### 3.2 负面影响\n- **低技能岗位的消失**：AI技术的广泛应用尤其对低技能岗位造成了威胁。根据研究，制造业和零售业的低技能岗位受到的影响最为明显（TISI, 2025）。\n- **技能不匹配**：随着AI技术的引入，许多传统岗位的技能要求发生了变化，导致部分劳动者面临失业风险（AJCASS, 2024）。\n\n## 4. 政策建议\n为了应对AI技术对就业市场的影响，政府和企业应采取以下措施：\n- **职业培训与再教育**：政府应加大对职业培训和再教育的投入，帮助劳动者提升技能，以适应新的就业市场需求。\n- **促进创新与创业**：鼓励企业创新和创业，创造更多的就业机会，尤其是在高科技领域。\n- **社会保障体系的完善**：建立健全社会保障体系，为因AI技术失业的劳动者提供必要的支持。\n\n## 5. 结论\nAI技术的采用对不同行业的就业总量产生了复杂的影响。虽然AI技术的引入可能导致某些岗位的消失，但同时也创造了新的就业机会。为了最大限度地发挥AI技术的积极作用，政府和企业需要共同努力，采取有效的政策措施，以应对就业市场的变化。\n\n## 参考文献\n- ILO. (2023). *World Employment and Social Outlook 2023*.\n- 50Forum. (2025). *不同行业AI技术采用率调查报告*. Retrieved from [50forum.org](http://www.50forum.org/home/article/detail/id/11133.html)\n- News.cn. (2025). *AI技术对就业市场的影响分析*. Retrieved from [news.cn](http://www.news.cn/globe/20250121/1b72ab9c82534a8a9d479b2a513ef127/c.html)\n- TISI. (2025). *AI在医疗行业的应用现状*. Retrieved from [tisi.org](http://www.tisi.org/19576/)\n- AJCASS. (2024). *AI技术对金融服务行业的影响*. Retrieved from [ajcass.com](https://sle.ajcass.com/Admin/UploadFile/Issue/201911110002/2024/3//20240313105620WU_FILE_0.pdf)'},
 {'source_data': [{'url': 'https://www.saas.pku.edu.cn/docs/2025-01/a0c3d3384a45434ba9f09175c7916d57.pdf',
    'title': '[PDF] 低技能劳动力流入与中国城市经济发展 - 北京大学现代农学院',
    'description': '内容提要中国大城市对高技能劳动力采取优惠的落户政策，而对低技能. 劳动力的落户政策更严格。本文通过构建两城市一般均衡模型，结合理论推导、.',
    'icon': ''},
   {'url': 'https://qks.sufe.edu.cn/mv_html/j00001/202307/0988557a-300a-42f0-a989-6d8fb1b150ab_WEB.htm',
    'title': '自动化技术应用与企业人力资本结构<sup>*</sup>',
    'description': '通常来说，自动化技术对低技能劳动力的替代弹性较大，对高技能劳动力的替代弹性则较小。Dixon等（2021）认为，机器人可以有效提高生产效率，减少产品间的质量差异 ...',
    'icon': ''},
   {'url': 'http://gjs.cass.cn/kydt/kydt_kycg/202112/t20211203_5379012.shtml',
    'title': '人工智能影响就业的多重效应与影响机制：综述与展望',
    'description': '一方面，替代效应作用下对低技能工人雇佣减少，相应劳动收入份额也减少；另一方面，补充效应下高技能工人能够适应现有岗位工作要求，相应劳动收入份额保持不变 ...',
    'icon': ''},
   {'url': 'http://www.qstheory.cn/qshyjx/2024-07/08/c_1130175728.htm',
    'title': '应对AI就业冲击需要澄清一些认识- 求是网',
    'description': '从主观上说，新岗位的体面程度也要低于原来的工作。总而言之，就业质量被降低。 第三，转到少量具有高需求弹性行业的岗位上。这是指那些人们保持着 ...',
    'icon': ''},
   {'url': 'https://www.chinazy.org/info/1006/16944.htm',
    'title': '发展新质生产力背景下技能劳动力需求特征及职业教育供给思路',
    'description': '人工智能对各领域的技术渗透和劳动介入在不同区域之间存在显著差异，导致一些地区的劳动生产率和工资率整体高于其他地区，以及一些地区对低技能劳动力的挤出 ...',
    'icon': ''},
   {'url': 'https://qks.sufe.edu.cn/mv_html/j00001/202307/0988557a-300a-42f0-a989-6d8fb1b150ab_WEB.htm',
    'title': '自动化技术应用与企业人力资本结构<sup>*</sup>',
    'description': '通常来说，自动化技术对低技能劳动力的替代弹性较大，对高技能劳动力的替代弹性则较小。 ... 这两个岗位基本上都要求员工具有高技能、高学历。企业只有雇用更多与自动化 ...',
    'icon': ''},
   {'url': 'http://www.qstheory.cn/qshyjx/2024-07/08/c_1130175728.htm',
    'title': '应对AI就业冲击需要澄清一些认识- 求是网',
    'description': '第三，转到少量具有高需求弹性行业的岗位上。这是指那些人们保持着巨大的需求，却天然具有劳动生产率难以提高特性的行业。经济学家威廉·鲍莫尔 ...',
    'icon': ''},
   {'url': 'http://gjs.cass.cn/kydt/kydt_kycg/202112/t20211203_5379012.shtml',
    'title': '人工智能影响就业的多重效应与影响机制：综述与展望',
    'description': '一方面，替代效应作用下对低技能工人雇佣减少，相应劳动收入份额也减少；另一方面，补充效应下高技能工人能够适应现有岗位工作要求，相应劳动收入份额保持不变（ ...',
    'icon': ''},
   {'url': 'https://www.ndrc.gov.cn/wsdwhfz/202206/t20220602_1326795.html',
    'title': '【专家观点】数字经济的就业创造效应与就业替代效应探究',
    'description': '此外，数字经济的融合性特征还能对其他行业起到关联带动作用，美国有研究显示，城市中每增加1个高技能岗位，就会带来5个消费型服务业岗位，包括技术性职业（如 ...',
    'icon': ''},
   {'url': 'https://cssn.cn/dkzgxp/zgxp_zgshkx/2023nd11q/202312/t20231223_5721263.shtml',
    'title': '中国劳动力市场结构变迁 - 中国社会科学网',
    'description': '第一，近年来，伴随着自动化等常规任务替代型技术进步的快速发展，常规任务密集度较高的生产制造类岗位面临较强的任务替代效应，而新工作创造效应相对较小，这 ...',
    'icon': ''},
   {'url': 'http://www.qstheory.cn/qshyjx/2024-07/08/c_1130175728.htm',
    'title': '应对AI就业冲击需要澄清一些认识- 求是网',
    'description': '从主观上说，新岗位的体面程度也要低于原来的工作。总而言之，就业质量被降低。 第三，转到少量具有高需求弹性行业的岗位上。这是指那些人们保持 ...',
    'icon': ''},
   {'url': 'https://qks.sufe.edu.cn/mv_html/j00001/202307/0988557a-300a-42f0-a989-6d8fb1b150ab_WEB.htm',
    'title': '自动化技术应用与企业人力资本结构<sup>*</sup>',
    'description': '通常来说，自动化技术对低技能劳动力的替代弹性较大，对高技能劳动力的替代弹性则较小。Dixon等（2021）认为，机器人可以有效提高生产效率，减少产品间的质量差异，因此专门从事 ...',
    'icon': ''},
   {'url': 'https://www.chinazy.org/info/1006/16944.htm',
    'title': '发展新质生产力背景下技能劳动力需求特征及职业教育供给思路',
    'description': '... 低复杂度弱程序性手工任务以及高技能复杂任务的劳动力不易被替代，导致技能结构呈“U”型，即两极化趋势。不同层级的技能结构特征存在显著差异，较低 ...',
    'icon': ''},
   {'url': 'https://www.saas.pku.edu.cn/docs/2025-01/a0c3d3384a45434ba9f09175c7916d57.pdf',
    'title': '[PDF] 低技能劳动力流入与中国城市经济发展 - 北京大学现代农学院',
    'description': '内容提要中国大城市对高技能劳动力采取优惠的落户政策，而对低技能. 劳动力的落户政策更严格。本文通过构建两城市一般均衡模型，结合理论推导、.',
    'icon': ''},
   {'url': 'https://ciejournal.ajcass.com/UploadFile/Issue/fl5r0dgw.pdf',
    'title': '[PDF] 人工智能技术会诱致劳动收入不平等吗 - 中国工业经济',
    'description': '... 特征,门槛值为Z=NK/(K+L)。当I<Zn. 时,低技术部门自动化扩张替代低技能劳动有利于提升该部门生产率,使高､低技术部门的相对生. 产率下降,进而加剧收入不平等;当1>Z时,低 ...',
    'icon': ''}],
  'analysis_data': '# 高技能岗位与低技能岗位的替代弹性差异特征研究报告\n\n## 摘要\n\n随着自动化技术的快速发展，企业人力资本结构的变化引起了广泛关注。本文旨在探讨高技能岗位与低技能岗位在自动化技术应用中的替代弹性差异特征。通过对2015—2019年中国上市公司数据的实证分析，研究发现自动化技术的应用显著改善了企业的人力资本结构，尤其是在采购集成型自动化产品的企业中表现尤为明显。本文还探讨了不同类型自动化产品对人力资本结构的影响机制，并提出相应的政策建议。\n\n## 1. 引言\n\n在全球第四次工业革命的背景下，自动化技术的广泛应用正在重塑企业的生产方式和人力资源配置。自动化技术不仅提高了生产效率，还对企业的人力资本结构产生了深远影响。现有研究表明，自动化技术的应用对不同技能水平的劳动力产生了不同的影响，尤其是高技能与低技能岗位之间的替代弹性差异。\n\n## 2. 理论框架与研究假说\n\n### 2.1 自动化技术与人力资本结构\n\n自动化技术的应用可以通过替代效应和促进效应影响企业的人力资本结构。替代效应主要体现在低技能劳动力被自动化技术替代，而促进效应则体现在高技能劳动力的需求增加。基于此，本文提出以下假说：\n\n- **假说1**：自动化技术的应用将改善企业的人力资本结构，尤其是高技能劳动力的比例将显著提高。\n\n### 2.2 异质性自动化技术的作用\n\n不同类型的自动化产品（基础型与集成型）对人力资本结构的影响存在差异。基础型自动化产品主要替代低技能劳动力，而集成型自动化产品则需要高技能劳动力的配合。由此，本文提出：\n\n- **假说2**：基础型自动化技术应用改善下游企业人力资本结构的作用不明显，而集成型自动化技术应用有助于改善下游企业的人力资本结构。\n\n## 3. 数据来源与研究方法\n\n### 3.1 数据来源\n\n本文使用2015—2019年中国上市公司的面板数据，数据来源于国泰安数据库、万得数据库及中国自动化网。通过匹配自动化产品供应商与上市公司供应商名单，构建了“上市公司—年份—是否采购自动化产品”的合成数据库。\n\n### 3.2 研究方法\n\n本文采用固定效应模型分析自动化技术对企业人力资本结构的影响，模型设定如下：\n\n\\[\nHC_{ijkt} = \\alpha_0 + \\alpha_1 Automation_{ijkt} + \\alpha_2 X_{it} + \\alpha_3 Y_{kt} + \\alpha_4 Z_{jt} + \\delta_t + \\lambda_j + \\eta_k + \\epsilon_{ijkt}\n\\]\n\n其中，\\(HC_{ijkt}\\)表示企业在特定年份的人力资本结构，\\(Automation_{ijkt}\\)为自动化技术应用的虚拟变量，\\(X_{it}\\)、\\(Y_{kt}\\)、\\(Z_{jt}\\)为控制变量。\n\n## 4. 实证结果分析\n\n### 4.1 基准回归结果\n\n基准回归结果显示，自动化技术的应用与企业人力资本结构呈显著正相关。具体而言，采购自动化产品的企业高学历员工的相对雇用比重显著上升。\n\n### 4.2 不同类型自动化产品的影响\n\n进一步分析表明，只有采购集成型自动化产品的企业，其人力资本结构的改善效果显著，而基础型自动化产品的影响则不明显。这一结果支持了假说2。\n\n## 5. 讨论与政策建议\n\n### 5.1 讨论\n\n本研究的结果表明，自动化技术的应用在提升企业人力资本结构方面具有重要作用，尤其是在高技能劳动力的需求上。不同类型的自动化产品对人力资本结构的影响机制也有所不同，企业在选择自动化技术时应考虑其对人力资本的长期影响。\n\n### 5.2 政策建议\n\n1. **支持集成型自动化产品的研发与应用**：政府应鼓励企业采购集成型自动化产品，以提升人力资本结构。\n2. **加强职业教育与培训**：针对低技能劳动力的再就业问题，政府应提供职业培训，帮助其提升技能以适应新的就业市场。\n3. **优化人力资本政策**：企业应根据自动化技术的应用情况，调整人力资源管理策略，以更好地适应市场变化。\n\n## 6. 结论\n\n本文通过对高技能岗位与低技能岗位的替代弹性差异特征的研究，揭示了自动化技术对企业人力资本结构的深远影响。未来的研究可以进一步探讨不同产业背景下自动化技术的应用效果及其对劳动力市场的长期影响。\n\n## 参考文献\n\n1. 吴一平, 陈家和, 李鹏飞. 自动化技术应用与企业人力资本结构——基于供应链视角的研究. _财经研究_, 2023, 49(7): 4-18.\n2. 李钰靖. 发展新质生产力背景下技能劳动力需求特征及职业教育供给思路——基于人工智能劳动介入的研究视角. _中国职业技术教育_, 2024(15): 13-24.\n3. Acemoglu, D., & Restrepo, P. (2018). The race between man and machine: Implications of technology for growth, factor shares, and employment. _American Economic Review_, 108(6), 1488-1542.\n4. Autor, D. H. (2015). Why are there still so many jobs? The history and future of workplace automation. _Journal of Economic Perspectives_, 29(3), 3-30.\n\n---\n\n以上是关于“高技能岗位与低技能岗位的替代弹性差异特征”的研究报告，涵盖了研究背景、理论框架、数据来源、实证分析及政策建议等方面。希望对相关领域的研究者和政策制定者有所帮助。'}]
"""

        print(result)
    except Exception as e:
        print(f"研究计划生成失败: {str(e)}")
        print("请检查：1.环境变量配置 2.API服务可用性 3.网络连接")

