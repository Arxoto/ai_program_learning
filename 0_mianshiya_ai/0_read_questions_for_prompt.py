

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
    with open(file_path, mode='r', encoding='utf-8') as f:
        is_qustion = False
        for line in f:
            if line == '### begin\n':
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
    with open(file_path, mode='r', encoding='utf-8') as f:
        for line in f:
            if line.startswith('- '):
                yield line[2:]
                

def main():
    prompt_prefix = ''
    with open(r'./0_prompt.md', mode='r', encoding='utf-8') as f:
        prompt_prefix = f.read()
    
    for question in each_questions_format_by_begin_end(r'./0_list_full.md'):
        print(prompt_prefix, question, sep='')
    for question in each_questions_format_by_markdown_list(r'./1_QA.md'):
        print(prompt_prefix, question, sep='')



if __name__ == "__main__":
    main()
