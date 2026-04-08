
from dataclasses import asdict, dataclass, field
import json
import logging
import sys
from pathlib import Path
from typing import Awaitable, Callable

from playwright.async_api import BrowserContext, Page, async_playwright


log = logging.getLogger(__name__)


def get_chrome_path() -> str:
    """
    执行 `uv run playwright install --dry-run` 手动安装
    要求目录结构：
    ```
    project/
    ├── this-file.py
    └── chrome-win64/
        └── chrome.exe (Windows)
    ```
    """
    # 获取当前脚本所在目录
    script_dir = Path(__file__).parent.absolute()
    
    # 根据操作系统选择 Chrome 路径
    if sys.platform == "win32":
        chrome_path = script_dir / "chrome-win64" / "chrome.exe"
    else:
        raise Exception("os not supported")
    
    if not chrome_path.exists():
        raise Exception(f"chrome path {chrome_path} not found, run 'uv run playwright install --dry-run' to install")
    
    return str(chrome_path)


async def run_page_stateless(fn: Callable[[BrowserContext], Awaitable[None]]):
    """无状态 每次需登录"""
    chrome_path = get_chrome_path()

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            executable_path=chrome_path,
            headless=False,
        )
        context = await browser.new_context()

        await fn(context)

        await context.close()
        await browser.close()


async def run_page_stateful(fn: Callable[[BrowserContext], Awaitable[None]], user_data_name: str | None = None):
    """有状态 涉及持久化"""
    chrome_path = get_chrome_path()

    if user_data_name is None:
        user_data_name = "default_profile"
    user_data_dir = Path(__file__).parent.absolute() / "chrome-profile" / user_data_name

    async with async_playwright() as p:
        context = await p.chromium.launch_persistent_context(
            user_data_dir,
            executable_path=chrome_path,
            headless=False,
        )

        await fn(context)

        await context.close()


async def wait_for_loading_complete(page: Page):
    """
    等待页面加载完成
    监听 ant-spin 相关的加载指示器
    """
    container_class: str
    for _ in range(100):
        await page.wait_for_timeout(100)
        spin_container = await page.query_selector("div.ant-spin-container")
        if not spin_container:
            continue
        tmp_class = await spin_container.get_attribute("class")
        if tmp_class:
            container_class = tmp_class
            break
    else:
        raise Exception("wait for table load complete timeout")
    
    if "ant-spin-blur" in container_class:
        print("检测到 blur 遮罩，等待 table 加载完成...")
        await page.wait_for_function(
            """() => {
                const container = document.querySelector('div.ant-spin-container');
                return container && !container.classList.contains('ant-spin-blur');
            }""",
            timeout=30000
        )
    print("table 加载完成")


async def get_page_num(page: Page) -> int | None:
    current_page_indicator = await page.query_selector("li.ant-pagination-item-active")
    if not current_page_indicator:
        return
    page_num_str = await current_page_indicator.inner_text()
    return int(page_num_str)


@dataclass
class Question:
    """面试题数据类"""
    question: str
    difficulty: str
    keywords: list[str]


@dataclass
class QuestionBank:
    """面试题库"""
    bank_name: str
    questions: list[Question] = field(default_factory=list)


async def main():
    async def fn(context: BrowserContext):
        page = await context.new_page()

        await page.goto("https://www.mianshiya.com/")
        print("已打开网页，等待用户点击进入某个板块，请在 5 分钟内进行操作...")

        await page.wait_for_function(
            "() => window.location.pathname.includes('/bank/')",
            timeout=5 * 60 * 1000
        )
        print("检测到进入 /bank/ 页面，开始抓取数据...")
        
        await page.wait_for_load_state()


        # 获取网页标签名称作为文件名
        page_title = await page.title()
        question_bank = QuestionBank(page_title)

        all_questions: set[str] = set() # 用于去重
        page_duplication: bool # 所有行的问题都在集合中，认为整个页还未刷新
        
        page_num_refresh_count = 0
        page_refresh_count = 0
        current_page_num = 1
        
        while True:
            # 获取当前页数
            page_num = await get_page_num(page)
            if current_page_num != page_num:
                page_num_refresh_count += 1
                if page_num_refresh_count > 10:
                    raise Exception("wait for page_num_refresh timeout")
                await page.wait_for_timeout(100)
                continue
            page_num_refresh_count = 0
            print(f"\n========== 正在处理第 {current_page_num} 页 ==========")
            
            page_duplication = True
            
            # 等待加载完成
            await wait_for_loading_complete(page)

            # 等待表格数据稳定
            await page.wait_for_timeout(1000)

            # 获取所有行
            rows = await page.query_selector_all("tr.ant-table-row")
            
            for row in rows:
                cells = await row.query_selector_all("td.ant-table-cell")
                if len(cells) != 3:
                    raise Exception("表格列数不符合预期")

                # 第一个 cell 作为问题
                question = await cells[0].inner_text()
                question = question.strip()
                # 第二个 cell 作为难度标签
                difficulty = await cells[1].inner_text()
                difficulty = difficulty.strip()
                # 第三个 cell 下多个关键字标签
                keyword_items = await cells[2].query_selector_all("div.ant-space-item")
                keywords: list[str] = []
                for kw in keyword_items:
                    kw_text = await kw.inner_text()
                    kw_text = kw_text.strip()
                    if kw_text:
                        keywords.append(kw_text)
                
                # 去重检查
                if question in all_questions:
                    continue
                all_questions.add(question)
                page_duplication = False

                question_data = Question(question, difficulty, keywords)
                question_bank.questions.append(question_data)
            
            if page_duplication:
                print("等待页刷新...")
                page_refresh_count += 1
                if page_refresh_count > 10:
                    raise Exception("wait for page_refresh timeout")
                await page.wait_for_timeout(300)
                continue
            page_refresh_count = 0

            print(f"第 {current_page_num} 页抓取完成，累计 {len(question_bank.questions)} 条")

            # 检查下一页按钮
            next_button = await page.query_selector("li.ant-pagination-next")
            if next_button:
                is_disabled = await next_button.get_attribute("aria-disabled")
                if is_disabled == "true":
                    print("已到达最后一页，抓取完成！")
                    break
                
                # 点击下一页
                button_inside = await next_button.query_selector("button")
                if button_inside:
                    print(f"点击下一页...")
                    await button_inside.click()
                    await page.wait_for_load_state("networkidle")
                    current_page_num += 1
                    continue
                else:
                    print("未找到下一页按钮，退出循环")
                    break
            else:
                print("未找到下一页按钮，退出循环")
                break
        
        # 输出结果
        print(f"\n\n========== 抓取完成 ==========")
        print(f"总共抓取 {len(question_bank.questions)} 条题目（已去重）")
        
        # 保存为 JSON 文件
        output_file = Path(__file__).parent / "output.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(asdict(question_bank), f, ensure_ascii=False, indent=4)
        print(f"已保存到 {output_file}")
    
    await run_page_stateful(fn)

