# Medical Research Synthesizer Agent

## Overview
This repository contains a goal-driven, multi-step LLM agent designed to automate academic literature reviews. It accepts a natural language research query, converts it into a compact keyword search, fetches live academic papers from the Semantic Scholar API, and synthesizes the findings into a structured Markdown report featuring a gap analysis and recommended next steps.

Built entirely from scratch without agentic frameworks (no LangChain, LlamaIndex, etc.), this project demonstrates explicit, traceable state management, strict prompt engineering, and fault-tolerant API integration with a local JSON fallback.

## The Pipeline (Chaining Logic)
The agent uses a standard Python dictionary as a shared state object. It processes the user query through a linear chain of four sequential LLM calls and one external tool call. Each step reads from the shared state and writes its output back to be used by the subsequent step.

- **Step 1: Keyword Extraction (LLM Call 1)**
  - **Input:** Natural language user query.
  - **Output:** A compact keyword search string (3-5 core terms) tailored for the Semantic Scholar API.
- **Step 2: Paper Retrieval (External Tool Call)**
  - **Input:** The keyword string from Step 1.
  - **Action:** Fetches the top papers via the Semantic Scholar Graph API using the `requests` library. If the live API fails or returns no results, the tool switches to `fallback_papers.json` to keep the pipeline running.
  - **Output:** JSON string of paper titles, authors, DOIs, and abstracts.
- **Step 3: Literature Synthesis (LLM Call 2)**
  - **Input:** Original user query + raw abstracts (Step 2).
  - **Output:** A cohesive, objective summary of the methodologies, architectures, and findings.
- **Step 4: Gap Analysis (LLM Call 3)**
  - **Input:** The synthesized summary (Step 3).
  - **Output:** A structured draft report with "Current Landscape" and "Gap Analysis" sections.
- **Step 5: Critique and Refine (LLM Call 4)**
  - **Input:** The draft report (Step 4).
  - **Output:** A polished Markdown report with a "Recommended Next Steps" section, written to disk.

## Prerequisites & Installation
Ensure you have Python installed. The core logic relies heavily on standard libraries, but you will need a few external packages.

1. Install dependencies:
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
2. (Optional) Switch the `provider` argument in `run_agent` to `grok` if you want to use the xAI key.
3. Run the pipeline:
   ```bash
   python main.py
   ```
4. The terminal will trace the execution and data flow of each step live. Once complete, the final structured output will be saved to `synthesized_research_report.md`.
