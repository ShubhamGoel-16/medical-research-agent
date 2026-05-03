import os
import json
from utils import call_llm, fetch_semantic_scholar
import prompts

def run_agent(user_query, provider="openai"):
    print(f"\n🚀 Starting Agent Pipeline for query: '{user_query}'\n")
    
    # The Shared State Object - Mandatory Requirement
    agent_state = {
        "user_query": user_query
    }

    # ==========================================
    # STEP 1: Keyword Extraction (LLM Call 1)
    # ==========================================
    print("[Step 1] Extracting Boolean Search Query...")
    user_prompt_1 = prompts.EXTRACT_USER.format(user_query=agent_state["user_query"])
    
    search_query = call_llm(prompts.EXTRACT_SYSTEM, user_prompt_1, provider)
    agent_state["search_query"] = search_query.strip()
    print(f"         Output: {agent_state['search_query']}\n")

    # ==========================================
    # STEP 2: Paper Retrieval (Tool Call)
    # ==========================================
    print("[Step 2] Executing Tool Call to Semantic Scholar API...")
    
    # Call the new function!
    raw_abstracts = fetch_semantic_scholar(agent_state["search_query"])
    
    agent_state["raw_abstracts"] = raw_abstracts
    print(f"         Output: {agent_state['raw_abstracts'][:100]}...\n")

    # ==========================================
    # STEP 3: Literature Synthesis (LLM Call 2)
    # ==========================================
    print("[Step 3] Synthesizing Literature...")
    user_prompt_3 = prompts.SYNTHESIS_USER.format(
        user_query=agent_state["user_query"],
        raw_abstracts=agent_state["raw_abstracts"]
    )
    
    synthesis = call_llm(prompts.SYNTHESIS_SYSTEM, user_prompt_3, provider)
    agent_state["synthesized_summary"] = synthesis
    print("         Output: Synthesis complete.\n")

    # ==========================================
    # STEP 4: Gap Analysis (LLM Call 3)
    # ==========================================
    print("[Step 4] Performing Gap Analysis and Formatting Report...")
    user_prompt_4 = prompts.GAP_USER.format(
        synthesized_summary=agent_state["synthesized_summary"]
    )
    
    draft_report = call_llm(prompts.GAP_SYSTEM, user_prompt_4, provider)
    agent_state["final_markdown_report"] = draft_report
    print("         Output: Draft report generated.\n")

    # ==========================================
    # STEP 5: Critique and Refine (LLM Call 4)
    # ==========================================
    print("[Step 5] Polishing Final Report...")
    user_prompt_5 = prompts.REFINE_USER.format(
        final_markdown_report=agent_state["final_markdown_report"]
    )
    
    polished_report = call_llm(prompts.REFINE_SYSTEM, user_prompt_5, provider)
    agent_state["polished_final_report"] = polished_report
    print("         Output: Final polish complete.\n")

    # ==========================================
    # FINAL OUTPUT
    # ==========================================
    output_filename = "synthesized_research_report.md"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(agent_state["polished_final_report"])
        
    print(f"✅ Pipeline complete! Final output saved to {output_filename}")
    
    return agent_state

if __name__ == "__main__":
    
    # Example Query 
    query = "Compare the performance of architectures like ConvNeXt and EfficientNet for the early detection of diabetic retinopathy."
    
    # Run the pipeline. Change 'openai' to 'grok' when testing with the xAI key.
    final_state = run_agent(query, provider="openai")