import gradio as gr
from app.interface.pages.multi_llm_readme import create_multi_llm_readme_page
from app.interface.pages.readme_multi_file import create_readme_page
from app.interface.pages.data_quality import data_quality_page

from app.common.path_utils import get_app_path
import pdb

def create_app():
    """Creates and returns the Gradio interface with multiple pages."""

    with open(get_app_path("interface", "pages", "styles.css"), "r") as css_file:
        css_content = css_file.read()

    with open(get_app_path("interface", "pages", "js_inject.js"), "r") as js_file:
        js_inject_content = js_file.read()

    with gr.Blocks() as iface:
        gr.HTML(f"""
        <style>
            {css_content}
        </style>
        """)
        with gr.Row():
            gr.Markdown("# LLM workflows")
        with gr.Tabs():
            with gr.Tab("Improving data quality"):
                data_quality_page()
            with gr.Tab("Readme from multiple files"):
                create_readme_page()
            with gr.Tab("Multi stage readme creation"):
                create_multi_llm_readme_page()

            # 1) Run on initial load in case the Readme-tab is default-active
            iface.load(fn=None, inputs=None, outputs=None, _js=js_inject_content)

            # 2) Re-run every time you switch _to_ that tab
            readme_tab.select(fn=None, inputs=None, outputs=None, _js=js_inject_content)

            # Additional pages can be added here in the future
    return iface
