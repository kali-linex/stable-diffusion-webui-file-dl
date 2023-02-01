import os
from modules import script_callbacks, paths
import gradio as gr
import requests

def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as downloader:
        url = gr.Textbox("URL")
        out_file = gr.Textbox("Output file/folder if MEGA, based on models directory")
        download = gr.Button("Download")
        done = gr.Text()
        def download_file(url, out_file, progress=gr.Progress()):
            progress(0, "Starting download")
            r = requests.get(url, stream=True, timeout=10000)
            with open(os.path.join(paths.models_path, out_file), 'wb') as f:
                for data in progress.tqdm(r.iter_content(1024)):
                    f.write(data)
            return "done"
        download.click(download_file, inputs=[url, out_file], outputs=[done])
    return (downloader, "Downloader", "downloader"),

script_callbacks.on_ui_tabs(on_ui_tabs)