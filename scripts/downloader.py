import os
from modules import script_callbacks, paths
import gradio as gr
import requests
import subprocess
import os
import re
import tqdm
from PIL import Image

def locate_megacmd():
    for i in ["megacmd/usr/bin/mega-get", "/usr/bin/mega-get"]:
        if os.path.exists(i):
            return i
    return None

mega_get = locate_megacmd()
pixeldrain_regex = re.compile("(?:https?://)?pixeldrain.com/u/(\w+)")
cont_disp_regex = re.compile('attachment; filename=(.+)')

def download_mega(url, out_folder):
    if not mega_get:
        return "MEGAcmd not installed, can't download MEGA links. See https://mega.io/cmd for installation. Alternatively, I'll attempt to include an automagical installation soon™"
    result = subprocess.run([mega_get, url, out_folder])
    if result.returncode != 0:
        return "Error while downloading, check console"
    return "Done"

def direct_dl(url, out_file):
    try:
        r = requests.get(url, stream=True, timeout=10000)
        if os.path.isdir(out_file):
            if 'Content-Disposition' in r.headers and (m := cont_disp_regex.match(r.headers['Content-Disposition'])):
                out_file = os.path.join(out_file, m.group(1).strip('"'))
            else:
                out_file = os.path.join(out_file, url.split('/')[-1])
        with open(out_file, 'wb') as f:
            for data in tqdm.tqdm(r.iter_content(1024)):
                f.write(data)
    except Exception as e:
        return "Error. You might want to check console. Original exception: " + e
    return f'Done, downloaded to {out_file}'

def download_pixeldrain(id, out_file):
    return direct_dl(f'https://pixeldrain.com/api/file/{id}?download', out_file)

def download_file(url, out_file):
    out_file = os.path.join(paths.models_path, out_file)
    if url.startswith('https://mega.nz'):
        return download_mega(url, out_file)
    if m := pixeldrain_regex.match(url):
        return download_pixeldrain(m.group(1), out_file)
    return direct_dl(url, out_file)

def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as downloader:
        with gr.Tab("Direct link"):
            with gr.Box():
                url = gr.Textbox(placeholder="Link to the file",
                                 label="URL").style(container=True)
                with gr.Row():
                    download = gr.Button("Download", variant="primary")
                    out_file = gr.Textbox(
                        placeholder="Output file name or directory (only directory supported for MEGA), relative to the models/ directory", label="Output").style(container=False)
            done = gr.Text(label="Messages").style(container=False)

            download.click(download_file, inputs=[
                           url, out_file], outputs=[done])
        with gr.Tab("Civitai"):
            with gr.Row():
                with gr.Column():
                    civitai_url = gr.Textbox(
                        placeholder="Civit.ai link", label="URL").style(container=False)
                    fetch_info = gr.Button("Fetch models")
                    model_list = gr.Dropdown(label="Available models", type="index")
                    download = gr.Button("Download", variant="primary")
                civitai_imgs = gr.Gallery()
    return (downloader, "Downloader", "downloader"),

script_callbacks.on_ui_tabs(on_ui_tabs)
