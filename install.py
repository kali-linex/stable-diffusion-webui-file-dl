import launch
import os

if not launch.is_installed("requests"):
    launch.run_pip("install requests", "requirements for downloading files")

if not launch.is_installed("tqdm"):
    launch.run_pip("install tqdm", "requirements for downloading files")

launch.run(f"bash {os.path.dirname(os.path.realpath(__file__))}/mega_load.bash", "download MEGAcmd")