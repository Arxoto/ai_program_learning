# Repository Guidelines

## Project Structure & Module Organization

```
.
├── main.py                    # Entry point (currently runs the interview-question fetcher)
├── pyproject.toml             # Python project config (uv, Python >=3.14)
├── common_utils/              # Shared Python utilities (e.g. prompt formatter)
├── mianshiya_scripts/         # Playwright-based web scraper for mianshiya.com
├── 0_aaa/                     # Learning notes (Markdown: Spring, Java, AI, etc.)
├── 0_mianshiya_*/             # Categorized interview question banks (JSON + prompts + PDFs)
├── {1-5}_*/                   # Course project directories, each containing a git submodule
└── script/                    # Auxiliary shell scripts
```

Each numbered directory (`1_springai_rag_mcp_agent`, `2_langchain4j`, etc.) holds exactly one git submodule for a Java/Spring course project. Course PDFs and supporting materials live alongside the submodule, not inside it.

## Build, Test, and Development Commands

```bash
# Python — managed by uv (Python 3.14+)
uv run main.py                          # Run the default entry point
uv run mianshiya_scripts/fetch_question.py   # Scrape interview questions
uv run common_utils/read_questions_for_prompt.py > output.md  # Format questions for LLM

# Git submodules
git submodule update --init --recursive # Initialize all submodules after cloning
```

Each Java submodule follows its own build system (Maven/Gradle). Consult the submodule's own README for project-specific commands.

## Coding Style & Naming Conventions

- **Python**: Follow standard PEP 8. Use `uv` for dependency management. Keep scripts self-contained and single-purpose.
- **Java (submodules)**: Each submodule follows its own style guidelines. Do not mix Java source into the root repository.
- **Directories**: Lowercase with underscores (`common_utils`, `mianshiya_scripts`). Private directories are prefixed with `0_` and git-ignored where appropriate.
- **Files**: Markdown notes and prompts use snake_case names describing their domain (e.g. `java_concurrent.md`, `0_os_prompt.md`).

## Testing Guidelines

There is no shared test suite at the repository root. Each Java submodule contains its own tests; run them from within the submodule directory using that project's build tool. Python scripts are small utilities — validate output manually before committing.

## Commit & Pull Request Guidelines

Commit messages are bilingual (Chinese/English), short, and descriptive. Observe the repo's established patterns:

- `add <topic>` — introducing new content or tools
- `update <topic>` — modifying existing content
- `优化 <script or workflow>` — improvements and refinements

Since this is a personal learning repository, there is no formal PR process. When making changes, keep submodule updates intentional: always verify which commit the submodule points to before staging it.

## Agent-Specific Notes

The root `CLAUDE.md` provides detailed guidance for AI coding agents. This file complements it with contributor-facing conventions. When introducing new submodules, register them in `.gitmodules` and keep course materials in the parent directory, not inside the submodule itself.
