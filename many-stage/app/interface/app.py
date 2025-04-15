import gradio as gr
from app.interface.pages.multi_llm_readme import create_multi_llm_readme_page
from app.interface.pages.readme_multi_file import create_readme_page
from app.interface.pages.data_quality import data_quality_page

def create_app():
    """Creates and returns the Gradio interface with multiple pages."""
    with gr.Blocks() as iface:
        with gr.Row():
            gr.Markdown("# LLM analysis workflows")
        with gr.Tabs():
            with gr.Tab("Improving data quality"):
                data_quality_page()
            with gr.Tab("Readme from multiple files"):
                create_readme_page()
            with gr.Tab("Multi stage readme creation"):
                create_multi_llm_readme_page()

            # Additional pages can be added here in the future
    return iface
