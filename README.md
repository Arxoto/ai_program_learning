# ai_program_learning

1. 切换阅读模式 `read://https://xxxxxx`
1. 打印为 PDF `Ctrl+P`
1. 文件重命名 `git-bash.exe`
1. 压缩（二进制文件）

```shell
# 文件名去空格
ls | while IFS= read -r file; do echo "'${file}' -> '${file// /}'"; done;
ls | while IFS= read -r file; do mv "${file}" "${file// /}"; done;
# 根据时间排序编号
ls -rt | awk '{printf("%02d %s\n", NR, $0)}'| while IFS= read -r line; do array=(${line}); id=${array[0]}; name=${array[1]}; echo "${id}-${name}"; done;
ls -rt | awk '{printf("%02d %s\n", NR, $0)}'| while IFS= read -r line; do array=(${line}); id=${array[0]}; name=${array[1]}; mv "${name}" "${id}-${name}"; done;
```

## SpringAI_RAG_MCP_Agent AI 超级智能体

from <https://www.codefather.cn/course/1915010091721236482/section/1915011053345120257>

see [1_springai_rag_mcp_agent](./1_springai_rag_mcp_agent/)

## LangChain4j 实战

from <https://www.codefather.cn/course/1943267371799080961/section/1943267426392141826>

see [2_langchain4j](./2_langchain4j/)

## LangGraph4j AI 零代码应用生成平台

from <https://www.codefather.cn/course/1948291549923344386/section/1948291654280491010>

see [3_langgraph4j](./3_langgraph4j/)

## AI 大模型容器化项目

from <https://www.codefather.cn/course/1966420016440999938/section/1966420759127527425>

see [4_springboot_docker](./4_springboot_docker/)
