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
civitai_regex = re.compile("(?:https?://)?civitai.com/models/(\d+)(?:/.*)?")


def download_mega(url, out_folder):
    if not mega_get:
        return "MEGAcmd not installed, can't download MEGA links. See https://mega.io/cmd for installation. Alternatively, I'll attempt to include an automagical installation soon™"
    result = subprocess.run([mega_get, url, out_folder])
    if result.returncode != 0:
        return "Error while downloading, check console"
    return "Done"


def direct_dl(url, out_file, create_parent_dirs):
    try:
        r = requests.get(url, stream=True, timeout=10000)
        if create_parent_dirs:
            model_dir = os.path.dirname(
                out_file) if '.' in os.path.basename(out_file) else out_file
            if not os.path.exists(model_dir):
                os.makedirs(model_dir)
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


def download_pixeldrain(id, out_file, create_parent_dirs):
    return direct_dl(f'https://pixeldrain.com/api/file/{id}?download', out_file, create_parent_dirs)


def download_file(url, out_file, create_parent_dirs):
    out_file = os.path.join(paths.models_path, out_file)
    if url.startswith('https://mega.nz'):
        return download_mega(url, out_file)
    if m := pixeldrain_regex.match(url):
        return download_pixeldrain(m.group(1), out_file, create_parent_dirs)
    return direct_dl(url, out_file, create_parent_dirs)


def civitai_get_human_model_list(model_versions):
    # Would this be cleaner with a horrific list comprehension?
    models = []
    models_data = []
    for m in model_versions:
        name = m['name']
        models.extend(
            f'{name} | {i["name"]} | {i["type"]} | {i["format"]} | {(i["sizeKB"] / 10**6):.2f}GB' for i in m['files'])
        models_data.extend(m['files'])
    return models, models_data


def civitai_fetch_models(model_list, url):
    m = civitai_regex.match(url)
    if not m:
        return ("Invalid URL or extension bug", None, None, None)
    api = f'https://civitai.com/api/v1/models/{m.group(1)}'
    print(api)
    r = requests.get(api).json()
    choices, state = civitai_get_human_model_list(r['modelVersions'])
    model_list.choices = choices

    return (f'Fetched {r["name"]}', state, gr.update(choices=choices), None)


def on_ui_tabs():
    with gr.Blocks(analytics_enabled=False) as downloader:
        create_parent_dirs = gr.Checkbox(
            True, label="Create parent model directories if they do not exist (this may result in unintended consequences if you mistype something!)", interactive=True)
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
                           url, out_file, create_parent_dirs], outputs=[done])
        with gr.Tab("Civitai"):
            with gr.Row():
                with gr.Column():
                    civitai_url = gr.Textbox(
                        placeholder="Civitai link", label="URL").style(container=False)
                    fetch_info = gr.Button("Fetch models")
                    model_list = gr.Dropdown(
                        label="Available models", type="index", interactive=True).style(container=False)
                    pickle_warning = gr.Text(
                        "️⚠️ Choose a SafeTensor variant if you don't have a good reason not to.", visible=False, label="").style(container=False)
                    civitai_out_file = gr.Textbox(
                        placeholder="Output file name or directory (relative to the models/ directory)", label="Output").style(container=False)
                    civitai_download = gr.Button("Download", variant="primary")
                    saved_resp = gr.State()
                civitai_imgs = gr.Gallery()
            civitai_messages = gr.Text(label="Messages").style(container=False)
            fetch_info.click(lambda *args: civitai_fetch_models(model_list, *args), inputs=[civitai_url], outputs=[
                             civitai_messages, saved_resp, model_list, civitai_imgs])
            model_list.change(lambda choice, state: gr.update(visible=state[choice]['format'] == 'PickleTensor'), inputs=[
                              model_list, saved_resp], outputs=[pickle_warning])
            civitai_download.click(lambda out, choice, state, create_dirs: direct_dl(state[choice]['downloadUrl'], os.path.join(
                paths.models_path, out), create_dirs), inputs=[civitai_out_file, model_list, saved_resp, create_parent_dirs], outputs=[civitai_messages])
    return (downloader, "Downloader", "downloader"),


script_callbacks.on_ui_tabs(on_ui_tabs)
