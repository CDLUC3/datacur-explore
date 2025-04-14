import gradio as gr
from app.interface.pages.multi_readme import create_multi_readme_page

def create_app():
    """Creates and returns the Gradio interface with multiple pages."""
    with gr.Blocks() as iface:
        with gr.Row():
            gr.Markdown("# Multi-stage Analysis Tool")
        with gr.Tabs():
            with gr.Tab("Multi Readme Analysis"):
                create_multi_readme_page()
            # Additional pages can be added here in the future
    return iface
