"""
Minimal Gradio UI for AI Research Agent (with PNGs)
"""

import os
import re
from datetime import datetime
import gradio as gr
from dotenv import load_dotenv
from src.orchestrator import ResearchOrchestrator

load_dotenv()

def run_research(query: str):
    if not query or not query.strip():
        return "Please enter a research query.", None, []

    orchestrator = ResearchOrchestrator()
    report = orchestrator.conduct_research(query.strip())

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"outputs/research_report_{timestamp}.md"
    os.makedirs("outputs", exist_ok=True)

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(report)

    # Extract PNG paths from markdown: ![alt](path)
    image_paths = re.findall(r"!\[.*?\]\((outputs/.*?\.png)\)", report)
    images = [path for path in image_paths if os.path.exists(path)]

    # Remove image references from markdown for display (images go to gallery)
    display_report = re.sub(r"!\[.*?\]\(outputs/.*?\.png\)\n?", "", report)

    return display_report, output_file, images

with gr.Blocks(title="AI Research Agent") as demo:
    gr.Markdown("# AI Research Agent")
    gr.Markdown("Enter a research query and generate a report + charts.")

    query = gr.Textbox(
        label="Research Query",
        placeholder="e.g., How have decoder-only models evolved and where are they used?",
        lines=3,
    )

    run_btn = gr.Button("Run Research")

    report_md = gr.Markdown(label="Report Preview")
    report_file = gr.File(label="Download Report")
    chart_gallery = gr.Gallery(label="Charts", columns=2, height=300)

    run_btn.click(
        fn=run_research,
        inputs=query,
        outputs=[report_md, report_file, chart_gallery]
    )

if __name__ == "__main__":
    demo.launch(share=True)