# Hyphen Agent
# Terminal-based Installer
# 
# Original code.
# 
# Hyphen Project is licensed under GPLv3.

import subprocess

import requests
import argparse
import os
import platform
import shutil

def change_string(file: str, old: str, new: str):
    with open(file, "r") as f:
        content = f.read()
    with open(file, "w") as f:
        f.write(content.replace(old, new))    

parser = argparse.ArgumentParser()

parser.add_argument("-d", help="Directory to download.")
parser.add_argument("-a", help="API key.")
parser.add_argument("-p", help="Provider name.")
parser.add_argument("-m", help="Model name.")
parser.add_argument("-t", help="Use temp directory in installing.")

args = parser.parse_args()

directory = args.d
api_key = args.a
provider = args.p
model = args.m

for i in [directory, api_key, provider, model]:
    if i is None:
        raise ValueError("Missing required argument.")

print("""
*-- Installation Credentials --*
Directory: {}
API Key: ********
Provider: {}
Model: {}
    """.format(directory, provider, model))

if platform.system() == "Windows":
    temp_dir = "C:\\Windows\\Temp"
elif platform.system() == "Linux":
    temp_dir = "/tmp"
else:
    temp_dir = str(os.getenv("HOME"))

try:
    print("Creating directories...")
    os.makedirs(directory, exist_ok=True)
    if args.t:
        os.makedirs(temp_dir, exist_ok=True)
    
        print("Installing to temp directory: {}".format(temp_dir))
        for i in ["webui.py","engine/HyCore/standalone.py","engine/HyCore/__init__.py"]:
            with open(os.path.join(temp_dir, i), "w") as f:
                f.write(requests.get("https://raw.githubusercontent.com/EmxrWasHere0/Hyphen/main/{}".format(i)).text)
            print("Installed: {}".format(i))
    
        print("Copying to the installation directory...")
        for i in ["webui.py","engine/HyCore/standalone.py","engine/HyCore/__init__.py"]:
            shutil.copy(os.path.join(temp_dir, i), os.path.join(directory, i))
            print("Copied: {}".format(i))
    
        print("Cleaning up...")
        shutil.rmtree(temp_dir)
    else:
        print("Installing to directory: {}".format(directory))
        for i in ["webui.py","engine/HyCore/standalone.py","engine/HyCore/__init__.py"]:
            with open(os.path.join(directory, i), "w") as f:
                f.write(requests.get("https://raw.githubusercontent.com/EmxrWasHere0/Hyphen/main/{}".format(i)).text)
            print("Installed: {}".format(i))
    
    print("Setting up virtual environment...")
    subprocess.run(["python", "-m", "venv", os.path.join(directory, "engine",".venv")])
    print("Installed: virtual environment")
    
    print("Installing required libraries...")
    with open(os.path.join(directory, "requirements.txt"), "w") as f:
        f.write(requests.get("https://raw.githubusercontent.com/EmxrWasHere0/Hyphen/main/requirements.txt").text)
    print("Installed: requirements.txt")
    
    print("Installing...")
    if platform.system() == "Windows":
        subprocess.run([os.path.join(directory, "engine", ".venv", "Scripts", "pip.exe"), "install", "-r", os.path.join(directory, "requirements.txt")])
    else:
        subprocess.run([os.path.join(directory, "engine", ".venv", "bin", "pip3"), "install", "-r", os.path.join(directory, "requirements.txt")])
    print("Installed: libraries")
    
    os.remove(os.path.join(directory, "requirements.txt"))
    print("Removed: requirements.txt")
    
    print("Creating Hyphen-allowed default directory...")
    if platform.system() == "Windows":
        subprocess.run(["mkdir", os.path.join(directory, "engine", "HyCore", "Hyphen")])
    else:
        subprocess.run(["mkdir", os.path.join(directory, "engine", "HyCore", "hyphen")])
    
    print("Configuring environment...")
    with open(os.path.join(directory, "engine", "HyCore", "config.env"), "w") as f:
        f.write("API_KEY={}\nPROVIDER={}\nMODEL={}\nSTORAGE_PATH={}".format(args.a, args.p, args.m, os.path.join(directory, "engine", "HyCore", "Hyphen")))
    print("Configured: environment")
    
    if platform.system() == "Linux":
        print("Checking if system uses systemd...")
        if os.path.exists("/etc/systemd/system"):
            print("System uses systemd")
            print("Setting up services...")
            for s in ["standalone", "webui"]:
                subprocess.run(["curl", "-o", f"/etc/systemd/system/hyphen-{s}.service", f"https://raw.githubusercontent.com/EmxrWasHere0/Hyphen/refs/heads/main/{s}.service"])
                change_string(f"/etc/systemd/system/hyphen-{s}.service", "PLACEHOLDER_USER", "root")
                change_string(f"/etc/systemd/system/hyphen-{s}.service", "PLACEHOLDER_WD", directory)
                if s == "standalone":
                    change_string(f"/etc/systemd/system/hyphen-{s}.service", "PLACEHOLDER_EXEC", f"{os.path.join(directory, 'engine', 'HyCore', '.venv', 'bin', 'python3')} {os.path.join(directory, 'engine', 'HyCore', f'{s}.py')}")
                else:
                    change_string(f"/etc/systemd/system/hyphen-{s}.service", "PLACEHOLDER_EXEC", f"{os.path.join(directory, 'engine', 'HyCore', '.venv', 'bin', 'python3')} {os.path.join(directory, f'{s}.py')}")
    
                subprocess.run(["systemctl", "daemon-reload"])
                subprocess.run(["systemctl", "enable", f"hyphen-{s}.service"])
                subprocess.run(["systemctl", "start", f"hyphen-{s}.service"])
        else:
            print("Couldn't detect systemd.")
    
        print("Services set up successfully")
        
    else:
        print("Unsupported platform for systemd")
except Exception as e:
    print(f"CRITIC: {e}")

print("Done.")
