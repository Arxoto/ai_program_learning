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

《SpringAI + RAG + MCP + Agent AI 超级智能体企业级实战（26年必学）》

from <https://www.codefather.cn/course/1915010091721236482>

see [1_springai_rag_mcp_agent](./1_springai_rag_mcp_agent/)

## LangChain4j 实战

《LangChain4j 实战教程 | AI 编程助手项目》

from <https://www.codefather.cn/course/1943267371799080961>

see [2_langchain4j](./2_langchain4j/)

## LangGraph4j AI 零代码应用生成平台

《【大厂必备】LangChain4j + 工作流 + 微服务 AI 零代码应用生成平台》

from <https://www.codefather.cn/course/1948291549923344386>

see [3_langgraph4j](./3_langgraph4j/)

## AI 大模型容器化项目

《SpringBoot + AI 大模型容器化项目部署实战：AI 自动回复工具》

from <https://www.codefather.cn/course/1966420016440999938>

see [4_springboot_docker](./4_springboot_docker/)

## DDD 实践

《Vue3 + SpringBoot + AI + DDD 企业级智能协同云图库项目（25 年最新）》

from <https://www.codefather.cn/course/1864210260732116994>

see [5_springboot_ddd](./5_springboot_ddd/)
