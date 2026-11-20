"""
M5.1: Gradio Web Chat Interface for Brightpath Media.
Bound to 127.0.0.1, share=False.
Permanent label: "Brightpath Media (demo), fictional".
"""

import os
import sys
import json
from pathlib import Path
from typing import Tuple

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

import gradio as gr
from pipeline import run_pipeline

os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"

HEADER_MD = """# Brightpath Media (demo), fictional
**Internal Knowledge Assistant** | Strictly evidence-based, verified citations.
"""


def chat_respond(user_query: str) -> Tuple[str, str, str, str]:
    """Processes user query through pipeline and formats UI outputs."""
    if not user_query or not user_query.strip():
        return "", "", "", ""

    res = run_pipeline(user_query.strip())

    answer = res.get("answer", "")
    conflict = res.get("conflict", "")
    citations_list = res.get("citations", [])
    citations_str = ", ".join(citations_list) if citations_list else "None"

    conflict_banner = ""
    if conflict:
        conflict_banner = f"⚠️ **POLICY CONFLICT DETECTED**\n\n{conflict}"
        if not answer:
            answer = f"The answer depends on conflicting policy rules:\n{conflict}"

    passages_details = ""
    for idx, p in enumerate(res.get("passages", []), start=1):
        cit = p.get("citation", "")
        title = p.get("section_title", "")
        text = p.get("text", "").strip()
        passages_details += f"### Passage {idx} {cit}: {title}\n{text}\n\n---\n"

    audit_entry = res.get("what_was_sent", {})
    audit_json = json.dumps(audit_entry, indent=2) if audit_entry else "No external prompt was dispatched."

    return answer, conflict_banner, citations_str, passages_details, audit_json


def reset_all() -> Tuple[str, str, str, str, str, str]:
    """Clears all inputs and outputs."""
    return "", "", "", "", "", ""


def create_app() -> gr.Blocks:
    """Creates and configures the Gradio Blocks application."""
    with gr.Blocks(title="Brightpath Media (demo), fictional") as demo:
        gr.Markdown(HEADER_MD)

        with gr.Row():
            with gr.Column(scale=3):
                query_input = gr.Textbox(
                    label="Ask a policy or procedure question:",
                    placeholder="e.g. What are the steps to onboard a new client in ClickUp?",
                    lines=2,
                )
                with gr.Row():
                    submit_btn = gr.Button("Ask Assistant", variant="primary")
                    reset_btn = gr.Button("Reset", variant="secondary")

                conflict_box = gr.Markdown(label="Conflict Alerts")
                answer_box = gr.Textbox(label="Assistant Answer", lines=6, interactive=False)
                citations_box = gr.Textbox(label="Verified Citations", lines=1, interactive=False)

            with gr.Column(scale=2):
                passages_box = gr.Markdown(label="Retrieved Evidence Passages")

        with gr.Accordion("What was sent to model (Privacy & Security Audit Log)", open=False):
            audit_box = gr.Code(label="Exact Prompt and Masked Passages Sent", language="json", interactive=False)

        submit_btn.click(
            fn=chat_respond,
            inputs=[query_input],
            outputs=[answer_box, conflict_box, citations_box, passages_box, audit_box],
        )
        query_input.submit(
            fn=chat_respond,
            inputs=[query_input],
            outputs=[answer_box, conflict_box, citations_box, passages_box, audit_box],
        )
        reset_btn.click(
            fn=reset_all,
            inputs=[],
            outputs=[query_input, answer_box, conflict_box, citations_box, passages_box, audit_box],
        )

    return demo


if __name__ == "__main__":
    demo = create_app()
    demo.launch(server_name="127.0.0.1", server_port=7860, share=False)
