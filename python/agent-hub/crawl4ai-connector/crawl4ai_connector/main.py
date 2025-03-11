import os
import asyncio
from bs4 import BeautifulSoup
from mofa.agent_build.base.base_agent import MofaAgent, run_agent
from crawl4ai import AsyncWebCrawler
async def load_url_with_crawl4ai(url:str):
    async with AsyncWebCrawler(verbose=True) as crawler:
        wait_for = """() => {
                    return new Promise(resolve => setTimeout(resolve, 3000));
                }"""
        result = await crawler.arun(url=url, magic=True, simulate_user=True, override_navigator=True,wait_fo=wait_for)
        if result.status_code == 200:
            # 如果您需要进一步处理HTML内容，可以在这里进行
            # 例如，使用LLM或其他解析方法
            return result.html
        else:
            raise Exception(f"Error loading URL: {url}")
def clean_html(html_content: str) -> str:
    soup = BeautifulSoup(html_content, 'html.parser')
    for tag in soup(['script', 'style']):
        tag.decompose()
    clean_html = str(soup)
    return clean_html

@run_agent
def run(agent:MofaAgent):
    url = agent.receive_parameter('url')
    html = asyncio.run(load_url_with_crawl4ai(url=url))
    if os.getenv('CLEAN_HTML', None) is not None:
        html = clean_html(html_content = html)
    agent.send_output(agent_output_name='crawl4ai_connector_result',agent_result=html)
def main():
    agent = MofaAgent(agent_name='crawl4ai-connector')
    run(agent=agent)
if __name__ == "__main__":
    main()
