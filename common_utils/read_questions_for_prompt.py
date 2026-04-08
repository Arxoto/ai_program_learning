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
    for fn, file_path in [
        (each_questions_format_by_jsons, r"./1_Questions_from_mianshiya.json"),
        (each_questions_format_by_markdown_list, r"./1_Questions_from_AngleMAXIN.md"),
    ]:
        for question in fn(file_path):
            print(f"# ========= {num} =========\n")
            num += 1
            print(prompt_prefix, question, sep="", end="\n\n")


if __name__ == "__main__":
    main()
