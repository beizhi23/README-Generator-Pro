---
name: readme-generator-pro
description: Generate, modify, and render professional README.md files and project introduction HTML pages using the bundled README Generator Pro FastAPI application. Use when the user asks Codex to generate README documentation from a GitHub repository, uploaded or local project files, modify an existing generated README, create a project_page.html, or run the README Generator Pro web UI or REST API without changing its behavior.
---

# README Generator Pro

Use the bundled FastAPI project in `assets/readme-generator-pro` without changing its core behavior.

## Workflow

1. Locate the bundled project at this skill directory under `assets/readme-generator-pro`.
2. Run commands from the bundled project directory unless the user asks for code changes.
3. Check whether dependencies are installed. If needed, install with `pip install -r requirements.txt`.
4. Use the included `.env` as the local configuration source. Do not print secrets from `.env` in chat or logs.
5. Start the app with `python run.py` or `scripts/start_server.ps1`.
6. Use the web UI at `http://localhost:8000` or call the FastAPI endpoints directly.
7. Preserve the existing application behavior. Do not rewrite generation logic unless the user explicitly asks to modify the project.

## Main Capabilities

- Generate README.md from a GitHub repository URL.
- Generate README.md from uploaded project files or a ZIP archive.
- Modify a generated README using natural language.
- Generate a project introduction HTML page with Mermaid diagrams.
- Use REST API endpoints for automated workflows.

## API Notes

Use these endpoints when interacting programmatically:

- `POST /api/generate`
- `POST /api/modify`
- `POST /api/generate_html_page`
- `POST /api/chat`
- `POST /api/understanding`
- `GET /api/file_content`

For local usage, prefer the existing `run.py` entry point.
