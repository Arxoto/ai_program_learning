import io
import json
from pathlib import Path
import sys
from typing import cast


def each_questions_format_by_jsons(file_path: str):
    """
    文件格式：
    ```
    {
        "questions": [
            {"question":"xxx"},
        ]
    }
    ```
    """
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
        for q in data["questions"]:
            yield q["question"]


def each_questions_format_by_begin_end(file_path: str):
    """
    文件格式：
    ```
    ### begin
    question
    tags
    ### end
    ```
    """
    with open(file_path, "r", encoding="utf-8") as f:
        is_qustion = False
        for line in f:
            if line == "### begin\n":
                is_qustion = True
                continue
            if is_qustion:
                yield line
                is_qustion = False


def each_questions_format_by_markdown_list(file_path: str):
    """
    文件格式：
    ```
    - Q1
    - Q2
    ```
    """
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("- "):
                yield line[2:-1]


def main():
    prompt_prefix = ""
    this_folder = Path(__file__).parent.absolute()
    with open(this_folder / "0_prompt.md", "r", encoding="utf-8") as f:
        prompt_prefix = f.read()

    cast(io.TextIOWrapper, sys.stdout).reconfigure(encoding="utf-8")
    num = 1
    for topic, fn, file_path in [
        # ("大模型应用开发，", each_questions_format_by_jsons, r"./1_Questions_from_mianshiya.json"),
        # ("大模型应用开发，", each_questions_format_by_markdown_list, r"./1_Questions_from_AngleMAXIN.md"),

        # ("后端网络 ", each_questions_format_by_jsons, r"./1_network.json"),
        # ("后端操作系统OS ", each_questions_format_by_jsons, r"./1_os.json"),

        # ("java后端开发 ", each_questions_format_by_jsons, r"./1_java_200.json"),

        # ("java后端开发 ", each_questions_format_by_jsons, r"./1_java_basic.json"),
        # ("java后端开发 ", each_questions_format_by_jsons, r"./1_java_collection.json"),
        # ("java后端开发 ", each_questions_format_by_jsons, r"./1_java_concurrent.json"),
        # ("java后端开发 ", each_questions_format_by_jsons, r"./1_java_jvm.json"),

        # ("java后端开发 ", each_questions_format_by_jsons, r"./1_spring.json"),
        # ("java后端开发 ", each_questions_format_by_jsons, r"./1_springboot.json"),
        # ("java后端开发 ", each_questions_format_by_jsons, r"./1_springcloud.json"),

        # ("java后端开发 消息队列 MQ ", each_questions_format_by_jsons, r"./1.MQ.json"),
        # ("java后端开发 数据库SQL框架 MyBatis ", each_questions_format_by_jsons, r"./1.MyBatis.json"),
        # ("java后端开发 数据库 MySQL ", each_questions_format_by_jsons, r"./1.MySQL.json"),
        # ("java后端开发 缓存 NoSQL Redis ", each_questions_format_by_jsons, r"./1.Redis.json"),
    ]:
        for question in fn(file_path):
            print(f"# ========= {num} =========\n")
            num += 1
            print(topic, prompt_prefix, question, sep="", end="\n\n")


if __name__ == "__main__":
    # uv run ..\common_utils\read_questions_for_prompt.py > ./0_prompt.md
    main()
