import os
from modules import script_callbacks, paths
import gradio as gr
import requests
import subprocess
import os
import tqdm

def locate_megacmd():
    for i in ["megacmd/usr/bin/mega-get", "/usr/bin/mega-get"]:
        if os.path.exists(i):
            return i
    return None

mega_get = locate_megacmd()

def download_mega(url, out_folder):
    if not mega_get:
        return "MEGAcmd not installed, can't download MEGA links"
    result = subprocess.run([mega_get, url, out_folder])
    if result.returncode != 0:
        return "Error while downloading, check console"
    return "done"

def download_file(url, out_file):
    if url.startswith('https://mega.nz'):
        return download_mega(url, out_file)
    r = requests.get(url, stream=True, timeout=10000)
    with open(os.path.join(paths.models_path, out_file), 'wb') as f:
        for data in tqdm.tqdm(r.iter_content(1024)):
            f.write(data)
    return "done"

def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as downloader:
        url = gr.Textbox("URL")
        out_file = gr.Textbox("Output file/folder if MEGA, based on models directory")
        download = gr.Button("Download")
        done = gr.Text()
        
        download.click(download_file, inputs=[url, out_file], outputs=[done])
    return (downloader, "Downloader", "downloader"),

script_callbacks.on_ui_tabs(on_ui_tabs)