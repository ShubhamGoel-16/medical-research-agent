# Medical Research Synthesizer Agent

## Overview
This repository contains a goal-driven, multi-step LLM agent designed to automate academic literature reviews. It accepts a natural language research query, converts it into an optimized Boolean search, fetches live academic papers from the ArXiv API, and synthesizes the findings into a structured Markdown report featuring a gap analysis and recommended next steps.

Built entirely from scratch without agentic frameworks (no LangChain, LlamaIndex, etc.), this project demonstrates explicit, traceable state management, strict prompt engineering, and fault-tolerant API integration.

## The Pipeline (Chaining Logic)
The agent uses a standard Python dictionary as a shared state object. It processes the user query through a linear chain of four sequential LLM calls and one external tool call. Each step reads from the shared state and writes its output back to be used by the subsequent step.

- **Step 1: Keyword Extraction (LLM Call 1)**
  - **Input:** Natural language user query.
  - **Output:** An optimized Boolean search string tailored for the ArXiv API.
- **Step 2: Paper Retrieval (External Tool Call)**
  - **Input:** The Boolean string from Step 1.
  - **Action:** Fetches the top recent papers via the ArXiv API using the `requests` library. Note: This tool includes a graceful degradation fallback mechanism. If the ArXiv API times out or rate-limits the request (HTTP 429), the tool safely catches the exception, prints a warning, and injects mock data into the state so the pipeline continues to execute successfully.
  - **Output:** JSON string of raw paper titles, authors, and abstracts.
- **Step 3: Literature Synthesis (LLM Call 2)**
  - **Input:** Original user query + raw abstracts (Step 2).
  - **Output:** A cohesive, objective summary of the methodologies, architectures, and findings.
- **Step 4: Gap Analysis (LLM Call 3)**
  - **Input:** The synthesized summary (Step 3).
  - **Output:** A structured draft report that identifies 2-3 missing areas in the current research.
- **Step 5: Critique and Refine (LLM Call 4)**
  - **Input:** The draft report (Step 4).
  - **Output:** A highly polished, strictly formatted Markdown report with actionable "Next Steps", which is then written to disk.

## Prerequisites & Installation
Ensure you have Python installed. The core logic relies heavily on standard libraries, but you will need a few external packages.

1. Clone the repository:
   ```bash
   git clone https://github.com/ShubhamGoel-16/medical-research-agent.git
   cd medical-research-agent
   ```

2. Install dependencies:
   ```bash
   pip install openai requests python-dotenv
   ```

3. Configure your API keys. Create a `.env` file in the root directory and add your keys:
   ```text
   OPENAI_API_KEY=your_openai_api_key_here
   GROK_API_KEY=your_grok_api_key_here
   ```

## Usage
The agent is executed entirely via the command-line interface.

1. Open `main.py` and modify the `query` variable at the bottom of the script if you wish to test a different research topic.
   - **Expected Input:** A standard natural language string (e.g., "Compare the performance of architectures like ConvNeXt and EfficientNet for the early detection of diabetic retinopathy.").
2. Run the pipeline:
   ```bash
   python main.py
   ```
3. The terminal will trace the execution and data flow of each step live. Once complete, the final structured output will be automatically saved to your directory as `synthesized_research_report.md`.
