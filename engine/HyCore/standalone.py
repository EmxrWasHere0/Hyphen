# Hyphen Core Engine (HyCore) Source File
# Standalone version
#
# Google ADK is a product of Google LLC.
#
# Hyphen Project is licensed under GPLv3
#

import os
import time
from typing import Any
from dotenv import load_dotenv
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
import platform
import subprocess as sp
import pyautogui
import mss

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools.mcp_tool import McpToolset
from google.adk.tools.mcp_tool.mcp_session_manager import StdioConnectionParams
from mcp import StdioServerParameters
from google.adk.runners import InMemoryRunner
from google.adk.tools.function_tool import FunctionTool
from google.adk.types import grounding

from litellm import Tool

load_dotenv()

provider = os.getenv("PROVIDER", "google")
model_name = os.getenv("MODEL", "gemini-1.5-flash")
MODEL = f"{provider}/{model_name}" # Model's full name (provider/model-name)

app = FastAPI(title="Hyphen")

STORAGE_PATH = os.getenv("STORAGE_PATH") # Allowed directory

# ---------------------- Tools -----------------------

filesystem = McpToolset(
                connection_params=StdioConnectionParams(
                    server_params=StdioServerParameters(
                        command='npx',
                        args=[
                            '-y',
                            '@modelcontextprotocol/server-filesystem',
                            STORAGE_PATH,
                        ],
                    ),
                ),
            )

def type_text(text: str) -> str:
    pyautogui.write(text)
    return f"Typed: {text}"


def press_key(key: str) -> str:
    pyautogui.press(key)
    return f"Pressed: {key}"


def click(x: int, y: int) -> str:
    pyautogui.click(x, y)
    return f"Clicked at ({x}, {y})"


import mss

def screenshot(path=os.path.join(STORAGE_PATH, "screen.png")):
  if platform.system() == "Windows":
    with mss.mss() as sct:
      sct.shot(output=path)
    return path
  elif platform.system() == "Linux":
    if os.getenv("XDG_SESSION_TYPE") == "wayland":
      return "Wayland is not supported by `mss`. Use `screenshot_wayland` tool."
    else:
      with mss.mss() as sct:
        sct.shot(output=path)
      return path
  elif platform.system() == "Darwin":
    with mss.mss() as sct:
      sct.shot(output=path)
    return path
  else:
    return "Operating system not supported."

import shutil

def screenshot_wayland(path=os.path.join(STORAGE_PATH, "screen.png")):
    try:
        if shutil.which("spectacle"):
            sp.run(["spectacle", "-b", "-n", "-o", path], check=True)
            return path
        elif shutil.which("grim"):
            sp.run(["grim", path], check=True)
            return path
        elif shutil.which("gnome-screenshot"):
            sp.run(["gnome-screenshot", "-f", path], check=True)
            return path
        return "No supported tool installed (spectacle / grim / gnome-screenshot)"
    except Exception as e:
        return str(e)

def execute_cmd(cmd: list):
    try:
        result = sp.run(
            cmd,
            check=True,
            capture_output=True,
            text=True
        )
        return {
            "status": "OK",
            "stdout": result.stdout.strip(),
            "stderr": result.stderr.strip()
        }
    except sp.CalledProcessError as e:
        return {
            "status": "FAIL",
            "stdout": e.stdout.strip() if e.stdout else "",
            "stderr": e.stderr.strip() if e.stderr else "",
            "code": e.returncode
        }

gsearch = Tool.from_google_search_retrieval(grounding.GoogleSearchRetrieval())

# ----------------------- Agent -------------------------
root_agent = Agent(
    name="assistant",
    model=LiteLlm(
        model=MODEL,
        api_key=os.getenv("API_KEY"), # API key's .env variable name
        base_url="" # API provider's base API URL
    ),
    instruction=f"""""", # Given instructions.
    tools=[filesystem,
        FunctionTool(type_text),
        FunctionTool(press_key),
        FunctionTool(click),
        FunctionTool(screenshot),
        FunctionTool(screenshot_wayland),
        FunctionTool(execute_cmd),
        gsearch,
    ],
)

runner = InMemoryRunner(agent=root_agent,app_name="hyphen")

async def run_agent_prompt(prompt: str, session_id: str, user_id: str) -> str:
    response = await runner.run_debug(
        prompt,
        session_id=session_id,
        user_id=user_id
    )
    return normalize_agent_output(response)


def normalize_agent_output(response: Any) -> str:
    if isinstance(response, str):
        return response

    if isinstance(response, list):
        collected_texts: list[str] = []
        for event in response:
            content = getattr(event, "content", None)
            if content is None:
                continue

            parts = getattr(content, "parts", None) or []
            for part in parts:
                text = getattr(part, "text", None)
                is_thought = bool(getattr(part, "thought", False))
                if text and not is_thought:
                    collected_texts.append(text)

        if collected_texts:
            return "\n".join(collected_texts).strip()

    return str(response)



@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/v1/chat/completions")
async def chat_completions(request: Request):
    data = await request.json()
    
    messages = data.get("messages", [])
    last_message = messages[-1]["content"] if messages else ""
    session_id = data.get("session_id", "webui_session")
    user_id = data.get("user", "webui_user")

    try:
        response_text = await run_agent_prompt(
            prompt=last_message,
            session_id=session_id,
            user_id=user_id
        )

        return {
            "id": "chatcmpl-adk",
            "object": "chat.completion",
            "created": int(time.time()),
            "model": "hyphen-assistant",
            "choices": [{
                "index": 0,
                "message": {
                    "role": "assistant",
                    "content": response_text
                },
                "finish_reason": "stop"
            }]
        }
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": {"message": str(e)}}
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)