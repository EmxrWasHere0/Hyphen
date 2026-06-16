# Hyphen Agent
# Terminal-based Installer
# 
# Original code.
# 
# Hyphen Project is licensed under GPLv3.

import requests
import argparse
import os
import platform

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

print("Creating directories...")
os.makedirs(directory, exist_ok=True)
if args.t:
    os.makedirs(temp_dir, exist_ok=True)

    print("Installing to temp directory: {}".format(temp_dir))
    for i in ["webui.py","engine/HyCore/standalone.py","engine/HyCore/__init__.py"]:
        with open(os.path.join(temp_dir, i), "w") as f:
            f.write(requests.get("https://raw.githubusercontent.com/EmxrWasHere0/Hyphen/main/{}".format(i)).text)
        print("Installed: {}".format(i))

    

print("Done.")
    
