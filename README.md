<div align="center">

![Hyphen](hyphen.png)  

</div>

Hyphen is an AI agent tool wrapper that lets you connect any AI API and use it with tools.

> ![NOTE]
> This project is still in development.  

> ![WARNING]
> This `.md` file is not accurate. Wait until the stable version of Hyphen.

# How it works?  
Hyphen has an engine called HyCore (Hyphen Core Agent Engine) that connects to the base URL of the API provider, and lets the AI use the provided tools.  

## What do I need to run Hyphen?  
You need:
- Python 3.11 or newer
- An API provider (Google, OpenAI, OpenRouter etc.)
- API provider's base URL (not necessary for Google)

to run Hyphen in your computer

# Steps
## Installing
- On Windows, download the right `.exe` file and run it.
- On Linux:
    - Ubuntu/Debian-based OSes:
        - Download the right `.deb` and run it.
    - Arch Linux-based OSes:
        - Download the right `.pkg.tar.zst`.
        - Install it with using `sudo pacman -U /path/to/file.pkg.tar.zst`.
    - Others:
        - You can either wait for the release for your operating systems,
        - Or directly clone this repo and manually configurate it.

## Removing
- On every OS, you can just clear the installation path.

## Updating
- On every OS, you will have to update Hyphen manually. You can update Hyphen with following [Installing](#installing) section.

## Dependencies  
Hyphen needs:
- google-adk
- fastapi
- mss
- uvicorn
- pyautogui

installed via `pip` in a virtual environment to work.  
You can skip this part if you're using n installer.

# Thanks to:
## Used tools
The following tools were used in the development of Hyphen:
- [adk-python](https://github.com/google/adk-python): An open-source, code-first Python toolkit for building, evaluating, and deploying sophisticated AI agents with flexibility and control.
- [FastAPI](https://github.com/fastapi/fastapi): FastAPI framework, high performance, easy to learn, fast to code, ready for production.
## Used services
The following services were used in the development of Hyphen:
- [OpenRouter](https://openrouter.ai): The Unified Interface For LLMs.
- [Groq](https://groq.com): Groq delivers fast, low cost inference that doesn’t flake when things get real.
- [Warp](https://warp.dev): Ship better software with any agent.
