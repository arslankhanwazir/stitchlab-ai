"""
M5.1 / M6A.4: Gradio Web Chat Interface for Brightpath Media.
Bound to 127.0.0.1, share=False.
Permanent label: "Brightpath Media (demo), fictional".
Supports:
- Local Ollama (default, offline, private)
- Google Gemini (your own API key via OpenAI-compatible endpoint)
"""

import os
import sys
import json
from pathlib import Path
from typing import Tuple, Any

# Paths
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import paths

import gradio as gr
from pipeline import run_pipeline
from connection_test import test_provider_connection

os.environ["GRADIO_ANALYTICS_ENABLED"] = "False"

HEADER_MD = """# Brightpath Media (demo), fictional
**Internal Knowledge Assistant** | Strictly evidence-based, verified citations.
"""

GEMINI_PROVIDER_NAME = "Google Gemini (your own API key)"
OLLAMA_PROVIDER_NAME = "Local Ollama (default)"

GEMINI_WARNING = (
    "⚠️ **Data Privacy Notice**: Free-tier keys may let Google use submitted content to "
    "improve its products, and people may read it. Use fictional or non-sensitive text on the free tier."
)


def chat_respond(
    user_query: str,
    provider: str = OLLAMA_PROVIDER_NAME,
    model_name: str = "",
) -> Tuple[str, str, str, str, str]:
    """Processes user query through pipeline and formats UI outputs."""
    if not user_query or not user_query.strip():
        return "", "", "", "", ""

    provider_clean = "gemini" if "gemini" in provider.lower() else "ollama"
    model_clean = model_name.strip() if model_name and model_name.strip() else None

    res = run_pipeline(
        user_query.strip(),
        provider=provider_clean,
        model=model_clean,
    )

    answer = res.get("answer", "")
    conflict = res.get("conflict", "")
    citations_list = res.get("citations", [])
    citations_str = ", ".join(citations_list) if citations_list else "None"

    conflict_banner = ""
    if conflict:
        conflict_banner = f"⚠️ **POLICY CONFLICT DETECTED**\n\n{conflict}"
        answer = "The answer depends on the conflicting policy rules shown above. Review both documents before acting."

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


def on_provider_change(provider_choice: str) -> Tuple[Any, Any, str]:
    """Updates UI visibility and warning when model provider changes."""
    if provider_choice == GEMINI_PROVIDER_NAME:
        return (
            gr.update(visible=True),
            gr.update(visible=True, value=GEMINI_WARNING),
            "Not tested",
        )
    else:
        return (
            gr.update(visible=False),
            gr.update(visible=False, value=""),
            "Connected (Local Ollama)",
        )


def on_test_connection(provider_choice: str, model_name: str) -> str:
    """Executes live provider connection health test."""
    if provider_choice == GEMINI_PROVIDER_NAME:
        key = os.environ.get("GEMINI_API_KEY")
        target_model = model_name.strip() if model_name else None
        res = test_provider_connection(
            provider="gemini",
            api_key=key,
            model=target_model,
        )
        if res["success"]:
            return "Connected"
        return res["message"]
    else:
        res = test_provider_connection("ollama")
        if res["success"]:
            return "Connected"
        return res["message"]


def create_app() -> gr.Blocks:
    """Creates and configures the Gradio Blocks application."""
    with gr.Blocks(title="Brightpath Media (demo), fictional") as demo:
        gr.Markdown(HEADER_MD)

        with gr.Accordion("Model Provider & Connection Settings", open=True):
            with gr.Row():
                provider_dropdown = gr.Dropdown(
                    label="Model Provider",
                    choices=[OLLAMA_PROVIDER_NAME, GEMINI_PROVIDER_NAME],
                    value=OLLAMA_PROVIDER_NAME,
                )
                model_input = gr.Textbox(
                    label="Model Name",
                    placeholder="e.g. gemini-1.5-flash",
                    value="",
                    info="use a model your key can access.",
                    visible=False,
                )
                test_conn_btn = gr.Button("Test Connection", variant="secondary")
                conn_status = gr.Textbox(
                    label="Connection Status",
                    value="Connected (Local Ollama)",
                    interactive=False,
                )

            gemini_warning_box = gr.Markdown(
                value="",
                visible=False,
            )

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

        # Wire Provider change & connection test
        provider_dropdown.change(
            fn=on_provider_change,
            inputs=[provider_dropdown],
            outputs=[model_input, gemini_warning_box, conn_status],
        )
        test_conn_btn.click(
            fn=on_test_connection,
            inputs=[provider_dropdown, model_input],
            outputs=[conn_status],
        )

        # Wire Chat submission
        submit_btn.click(
            fn=chat_respond,
            inputs=[query_input, provider_dropdown, model_input],
            outputs=[answer_box, conflict_box, citations_box, passages_box, audit_box],
        )
        query_input.submit(
            fn=chat_respond,
            inputs=[query_input, provider_dropdown, model_input],
            outputs=[answer_box, conflict_box, citations_box, passages_box, audit_box],
        )
        reset_btn.click(
            fn=reset_all,
            inputs=[],
            outputs=[query_input, answer_box, conflict_box, citations_box, passages_box, audit_box],
        )

    return demo


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "7860"))
    demo = create_app()
    try:
        demo.launch(server_name="127.0.0.1", server_port=port, share=False)
    except OSError:
        demo.launch(server_name="127.0.0.1", server_port=7861, share=False)
