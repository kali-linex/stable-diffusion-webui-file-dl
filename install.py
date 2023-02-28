import launch

if not launch.is_installed("requests"):
    launch.run_pip("install requests", "requirements for downloading files")

if not launch.is_installed("tqdm"):
    launch.run_pip("install tqdm", "requirements for downloading files")

launch.run("bash mega_load.bash", "download MEGAcmd")