# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a personal AI programming learning repository tracking courses from codefather.cn. It contains multiple git submodules for Java/Spring AI projects and Python tooling for managing interview question data (scraped from mianshiya.com).

## Common Commands

```bash
# Python — uv package manager (Python 3.14)
uv run main.py                      # Run main entry point (currently runs the question fetcher)
uv run mianshiya_scripts/fetch_question.py  # Scrape interview questions from mianshiya.com
uv run common_utils/read_questions_for_prompt.py > output.md  # Combine questions with AI prompt template

# Git submodules — each numbered directory contains a Java project submodule
git submodule update --init --recursive  # Initialize all submodules after fresh clone
```

## Architecture

### Directory Layout

- **`0_aaa/`** — Learning notes in Markdown (Spring, Java concurrency, data structures)
- **`0_mianshiya_*/`** — Categorized interview question banks. Each subdirectory holds JSON question files (`1_*.json`), prompt templates (`0_*_prompt.md`), and reference PDFs
- **`mianshiya_scripts/`** — Playwright-based web scraper. Uses a bundled Chrome (`chrome-win64/`) to automate fetching questions from mianshiya.com. The script paginates through `/bank/` pages, extracts question/difficulty/keywords from Ant Design tables, and saves as JSON
- **`common_utils/`** — Utility to merge scraped questions with an AI prompt prefix (`0_prompt.md`), producing formatted output ready for LLM answer generation. Supports multiple JSON and Markdown input formats

### Key Files

- **`main.py`** — Top-level entry point, currently wired to run the question fetcher
- **`pyproject.toml`** — Python project config; sole dependency is `playwright`. Uses USTC PyPI mirror

### Submodule Projects (Java/Spring)

Each `{1-5}_*` directory contains a git submodule pointing to a course project:
1. **SpringAI + RAG + MCP + Agent** — Enterprise AI agent
2. **LangChain4j** — AI coding assistant
3. **LangGraph4j** — Zero-code app generation platform with workflow engine
4. **SpringBoot + Docker** — Containerized AI auto-reply tool
5. **SpringBoot + DDD** — Vue3 + SpringBoot + AI intelligent cloud gallery

### Question Data Pipeline

1. **Fetch**: `mianshiya_scripts/fetch_question.py` opens mianshiya.com in a browser, waits for the user to navigate to a question bank, then scrapes all pages into `1.output.json`
2. **Format**: `common_utils/read_questions_for_prompt.py` reads JSON question files and prepends `0_prompt.md` (a Chinese-language prompt instructing the LLM to answer professionally with analysis and real-world context). Output is piped to markdown for LLM consumption
3. **Answer**: The formatted prompt+question markdown is fed to an LLM (typically via a web UI — the course teaches using AI IDEs for this step)