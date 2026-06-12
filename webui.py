# Hyphen Agent
# WebUI
#
# Google ADK is a product of Google LLC.
#
# Hyphen Project is licensed under GPLv3
#

import os

import uvicorn
from fastapi import FastAPI
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

from engine.HyCore.standalone import run_agent_prompt

app = FastAPI(title="Hyphen WebUI")

INDEX_HTML = """
<!doctype html>
<html lang="tr">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Hyphen WebUI</title>
    <link rel="icon" type="image/x-icon" href="/favicon.ico" />
    <style>
      :root {
        color-scheme: dark;
        --bg: #0b0f14;
        --panel: #111827;
        --panel-2: #1f2937;
        --text: #e5e7eb;
        --muted: #9ca3af;
        --accent: #22c55e;
        --assistant: #1d4ed8;
        --user: #065f46;
      }
      * {
        box-sizing: border-box;
      }
      body {
        margin: 0;
        background: var(--bg);
        color: var(--text);
        font-family: Inter, ui-sans-serif, system-ui, -apple-system, "Segoe UI", Roboto, "Helvetica Neue", Arial;
        height: 100vh;
        overflow: hidden;
      }
      .app {
        display: grid;
        grid-template-columns: 290px 1fr;
        height: 100vh;
      }
      .sidebar {
        background: var(--panel);
        border-right: 1px solid #374151;
        display: flex;
        flex-direction: column;
      }
      .sidebar-header {
        padding: 14px;
        border-bottom: 1px solid #374151;
      }
      .sidebar-header button {
        width: 100%;
        border: 0;
        border-radius: 10px;
        background: var(--accent);
        color: #052e16;
        font-weight: 700;
        padding: 10px 12px;
        cursor: pointer;
      }
      .chat-list {
        overflow: auto;
        padding: 10px;
        display: grid;
        gap: 8px;
      }
      .chat-item {
        background: var(--panel-2);
        border: 1px solid #374151;
        border-radius: 10px;
        padding: 10px;
        cursor: pointer;
      }
      .chat-item.active {
        border-color: var(--accent);
      }
      .chat-item-title {
        font-size: 13px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
      }
      .chat-item-meta {
        margin-top: 4px;
        color: var(--muted);
        font-size: 11px;
      }
      .main {
        display: grid;
        grid-template-rows: auto 1fr auto;
        height: 100vh;
      }
      .topbar {
        border-bottom: 1px solid #374151;
        padding: 14px 18px;
        display: flex;
        justify-content: space-between;
        align-items: center;
      }
      .topbar .title {
        font-weight: 700;
      }
      .topbar .subtitle {
        color: var(--muted);
        font-size: 13px;
      }
      .messages {
        overflow: auto;
        padding: 20px;
        display: grid;
        gap: 12px;
        align-content: start;
      }
      .msg {
        max-width: min(900px, 88%);
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 12px 14px;
        white-space: pre-wrap;
        line-height: 1.5;
      }
      .msg.assistant {
        background: color-mix(in oklab, var(--assistant) 25%, transparent);
        justify-self: start;
      }
      .msg.user {
        background: color-mix(in oklab, var(--user) 35%, transparent);
        justify-self: end;
      }
      .composer {
        border-top: 1px solid #374151;
        padding: 14px;
      }
      .composer-inner {
        background: var(--panel);
        border: 1px solid #374151;
        border-radius: 12px;
        display: grid;
        grid-template-columns: 1fr auto;
        gap: 10px;
        align-items: end;
        padding: 10px;
      }
      textarea {
        resize: none;
        border: 0;
        outline: 0;
        background: transparent;
        color: var(--text);
        font-size: 14px;
        min-height: 44px;
        max-height: 190px;
      }
      .send-btn {
        border: 0;
        border-radius: 10px;
        padding: 10px 14px;
        font-weight: 700;
        background: var(--accent);
        color: #052e16;
        cursor: pointer;
      }
      .hint {
        margin-top: 8px;
        color: var(--muted);
        font-size: 12px;
        text-align: right;
      }
      @media (max-width: 900px) {
        .app {
          grid-template-columns: 1fr;
        }
        .sidebar {
          display: none;
        }
      }
    </style>
  </head>
  <body>
    <div class="app">
      <aside class="sidebar">
        <div class="sidebar-header">
          <button id="newChatBtn">+ Yeni Sohbet</button>
        </div>
        <div class="chat-list" id="chatList"></div>
      </aside>
      <main class="main">
        <header class="topbar">
          <div>
            <div class="title">Hyphen WebUI</div>
            <div class="subtitle">Open WebUI benzeri arayüz</div>
          </div>
          <div id="status" class="subtitle">Hazır</div>
        </header>
        <section class="messages" id="messages"></section>
        <footer class="composer">
          <div class="composer-inner">
            <textarea id="promptInput" placeholder="Mesajını yaz..." rows="1"></textarea>
            <button id="sendBtn" class="send-btn">Gönder</button>
          </div>
          <div class="hint">Enter = gönder, Shift+Enter = yeni satır</div>
        </footer>
      </main>
    </div>
    <script>
      const storageKey = "hyphen_webui_chats_v1";
      let chats = {};
      let currentChatId = null;
      let sending = false;

      const messagesEl = document.getElementById("messages");
      const chatListEl = document.getElementById("chatList");
      const promptInputEl = document.getElementById("promptInput");
      const sendBtnEl = document.getElementById("sendBtn");
      const newChatBtnEl = document.getElementById("newChatBtn");
      const statusEl = document.getElementById("status");

      function uid() {
        return "chat_" + Date.now() + "_" + Math.random().toString(36).slice(2, 8);
      }

      function saveChats() {
        localStorage.setItem(storageKey, JSON.stringify({ chats, currentChatId }));
      }

      function loadChats() {
        try {
          const data = JSON.parse(localStorage.getItem(storageKey) || "{}");
          chats = data.chats || {};
          currentChatId = data.currentChatId || null;
        } catch {
          chats = {};
          currentChatId = null;
        }
        if (!currentChatId || !chats[currentChatId]) {
          createChat("Yeni Sohbet");
        }
      }

      function createChat(title = "Yeni Sohbet") {
        const id = uid();
        chats[id] = {
          id,
          title,
          createdAt: Date.now(),
          messages: [],
        };
        currentChatId = id;
        saveChats();
        renderSidebar();
        renderMessages();
      }

      function switchChat(id) {
        if (!chats[id]) return;
        currentChatId = id;
        saveChats();
        renderSidebar();
        renderMessages();
      }

      function currentChat() {
        return chats[currentChatId];
      }

      function setStatus(text) {
        statusEl.textContent = text;
      }

      function renderSidebar() {
        const sorted = Object.values(chats).sort((a, b) => b.createdAt - a.createdAt);
        chatListEl.innerHTML = "";
        sorted.forEach((chat) => {
          const item = document.createElement("button");
          item.className = "chat-item" + (chat.id === currentChatId ? " active" : "");
          item.onclick = () => switchChat(chat.id);
          item.innerHTML = `
            <div class="chat-item-title">${escapeHtml(chat.title || "Yeni Sohbet")}</div>
            <div class="chat-item-meta">${new Date(chat.createdAt).toLocaleString("tr-TR")}</div>
          `;
          chatListEl.appendChild(item);
        });
      }

      function escapeHtml(text) {
        return text
          .replaceAll("&", "&amp;")
          .replaceAll("<", "&lt;")
          .replaceAll(">", "&gt;");
      }

      function renderMessages() {
        const chat = currentChat();
        messagesEl.innerHTML = "";
        if (!chat || chat.messages.length === 0) {
          const welcome = document.createElement("div");
          welcome.className = "msg assistant";
          welcome.textContent = "Merhaba! Ne yapmamı istersin?";
          messagesEl.appendChild(welcome);
          return;
        }
        chat.messages.forEach((m) => appendMessageToDom(m.role, m.content));
        messagesEl.scrollTop = messagesEl.scrollHeight;
      }

      function appendMessage(role, content) {
        const chat = currentChat();
        chat.messages.push({ role, content });
        if (role === "user" && (!chat.title || chat.title === "Yeni Sohbet")) {
          chat.title = content.slice(0, 40) || "Yeni Sohbet";
        }
        saveChats();
        appendMessageToDom(role, content);
      }

      function appendMessageToDom(role, content) {
        const el = document.createElement("div");
        el.className = `msg ${role}`;
        el.textContent = content;
        messagesEl.appendChild(el);
        messagesEl.scrollTop = messagesEl.scrollHeight;
      }

      async function sendMessage() {
        if (sending) return;
        const content = promptInputEl.value.trim();
        if (!content) return;

        appendMessage("user", content);
        renderSidebar();
        promptInputEl.value = "";
        promptInputEl.style.height = "44px";
        sending = true;
        sendBtnEl.disabled = true;
        setStatus("Yanıt üretiliyor...");

        try {
          const chat = currentChat();
          const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              message: content,
              history: chat.messages,
              session_id: chat.id,
              user_id: "webui-user"
            }),
          });
          const data = await res.json();
          if (!res.ok) {
            throw new Error(data?.error?.message || "İstek başarısız oldu.");
          }
          appendMessage("assistant", data.response || "Boş yanıt döndü.");
        } catch (err) {
          appendMessage("assistant", "Hata: " + (err?.message || String(err)));
        } finally {
          sending = false;
          sendBtnEl.disabled = false;
          setStatus("Hazır");
        }
      }

      promptInputEl.addEventListener("input", () => {
        promptInputEl.style.height = "44px";
        promptInputEl.style.height = Math.min(promptInputEl.scrollHeight, 190) + "px";
      });

      promptInputEl.addEventListener("keydown", (e) => {
        if (e.key === "Enter" && !e.shiftKey) {
          e.preventDefault();
          sendMessage();
        }
      });

      sendBtnEl.onclick = sendMessage;
      newChatBtnEl.onclick = () => createChat("Yeni Sohbet");

      loadChats();
      renderSidebar();
      renderMessages();
    </script>
  </body>
</html>
"""


class UiChatRequest(BaseModel):
    message: str = Field(min_length=1)
    history: list[dict] = Field(default_factory=list)
    session_id: str = "openwebui_session"
    user_id: str = "openwebui_user"


@app.get("/", response_class=HTMLResponse)
async def webui_index():
    return HTMLResponse(INDEX_HTML)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse(os.path.join(os.path.dirname(__file__), "favicon.ico"))


@app.post("/api/chat")
async def ui_chat(request: UiChatRequest):
    try:
        response_text = await run_agent_prompt(
            prompt=request.message,
            session_id=request.session_id,
            user_id=request.user_id,
        )
        return {"response": response_text}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": {"message": str(e)}},
        )


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8001)
