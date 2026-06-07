"""Facade of Jade — Space app. Testing minimal gr.HTML first."""
import gradio as gr

HTML_TEST = """<div id="foj" style="background:#b8392a;color:#f5ecd7;padding:40px;font-family:Georgia,serif">
<h1 style="font-size:48px;margin:0 0 12px">FACADE OF JADE — TEST</h1>
<p style="font-size:18px">gr.HTML rendered successfully. This is the custom UI host.</p>
<p style="font-size:14px;opacity:0.8">Modal backend: <code>""" + "https://t-abdullah-rashid--facade-of-jade-backend-serve.modal.run" + """</code></p>
</div>"""

with gr.Blocks(title="Facade of Jade — Test") as demo:
    gr.HTML(value=HTML_TEST, sanitize_html=False)
