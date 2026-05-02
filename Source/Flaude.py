#!/usr/bin/env python3
"""
Flaude — AI terminal with computer control.
pip install rich prompt_toolkit anthropic requests

License Notice

This script was created by Kynix09.
Author profile: https://github.com/Kynix09
Repository: https://github.com/Kynix09/Flaude

You may not claim that you created, authored, or own this script.
Any use, modification, redistribution, or reference to this script must include proper credit to Kynix09 on Github.
MIT License

Copyright (c) 2026 Kynix09

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import sys, os, shutil, subprocess, json, time, re, datetime
from pathlib import Path

# ── Auto-install deps ─────────────────────────────────────────────────────────
def _install(*pkgs):
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", *pkgs],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    except Exception:
        pass

try:
    from rich.console import Console
    from rich.text import Text
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    from rich.markup import escape
    from rich.live import Live
except ImportError:
    _install("rich")
    from rich.console import Console
    from rich.text import Text
    from rich.panel import Panel
    from rich.table import Table
    from rich import box
    from rich.markup import escape
    from rich.live import Live

try:
    from prompt_toolkit import prompt as pt_prompt
    from prompt_toolkit.styles import Style as PTStyle
    from prompt_toolkit.formatted_text import HTML
    from prompt_toolkit.completion import Completer, Completion
    from prompt_toolkit.history import InMemoryHistory
    from prompt_toolkit.key_binding import KeyBindings
    from prompt_toolkit.application import Application
    from prompt_toolkit.layout import Layout
    from prompt_toolkit.layout.containers import Window
    from prompt_toolkit.layout.controls import FormattedTextControl
    HAS_PT = True
except ImportError:
    _install("prompt_toolkit")
    HAS_PT = False

try:
    from rainbowtext import rainbow
    HAS_RAINBOW = True
except ImportError:
    HAS_RAINBOW = False
try:
    import anthropic as _anthropic; HAS_ANTHROPIC = True
except ImportError:
    _install("anthropic")
    try:
        import anthropic as _anthropic; HAS_ANTHROPIC = True
    except Exception:
        HAS_ANTHROPIC = False

try:
    import requests as _requests; HAS_REQUESTS = True
except ImportError:
    _install("requests")
    try:
        import requests as _requests; HAS_REQUESTS = True
    except Exception:
        HAS_REQUESTS = False

# ── COLORS ────────────────────────────────────────────────────────────────────
O   = "#E8823A"   
DIM = "#6A6A6A"   
BDR = "#3A3A3A"   
WH  = "bold #FFFFFF"
TXT = "#CFCFCF"   


GRN = "#E8823A"   
RED = "#E8823A"   
BLU = "#A0A0A0"
YLW = "#E8823A"
PUR = "#A0A0A0"

console = Console(highlight=False)

# ── SETTINGS ──────────────────────────────────────────────────────────────────
SETTINGS_DIR  = Path.home() / ".flaude"
SETTINGS_FILE = SETTINGS_DIR / "settings.flaude"

DEFAULTS = {
    "version":    "1.0.4",
    "model":      "claude-sonnet-4-6",
    "host":       "localhost",
    "port":       11434,
    "backend":    "anthropic",
    "api_key":    "",
    "auto_allow": False,
    "theme":      "default",
    "max_tokens": 4096,
    "live":       True,
    "base_url":   "",
    "openai_key": "",
}

def load_settings() -> dict:
    s = dict(DEFAULTS)
    if SETTINGS_FILE.exists():
        try:
            saved = json.loads(SETTINGS_FILE.read_text())
            for k, v in saved.items():
                if k in s:
                    s[k] = v
        except Exception:
            pass
    # env key always wins
    env_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if env_key:
        s["api_key"] = env_key
    return s


def save_settings():
    SETTINGS_DIR.mkdir(parents=True, exist_ok=True)
    data = {k: S[k] for k in
            ("model", "host", "port", "backend", "auto_allow", "theme", "max_tokens", "live", "base_url", "openai_key")}
    if S.get("api_key") and not os.environ.get("ANTHROPIC_API_KEY"):
        data["api_key"] = S["api_key"]
    SETTINGS_FILE.write_text(json.dumps(data, indent=2))

# ── STATE ─────────────────────────────────────────────────────────────────────
S = load_settings()
S["cwd"]           = os.getcwd()
S["history"]       = []
S["last_response"] = ""

# ── LOGO ──────────────────────────────────────────────────────────────────────
LOGO = [
    "   ▄████▄   ",
    "  ███▀▀███  ",
    "  ██  ▄ ██  ",
    "  ██ ▀▀ ██  ",
    "  ███▄▄███  ",
    "   ▀████▀   ",
    "   ▄█  █▄   ",
    "  ▀      ▀  ",
]
# ── HELPERS ───────────────────────────────────────────────────────────────────
def tw():
    return shutil.get_terminal_size((120, 40)).columns

def short_path(p=None):
    p = str(p or S["cwd"])
    home = os.path.expanduser("~")
    if p.startswith(home):
        p = "~" + p[len(home):]
    return p

def sep(char="─", style=BDR):
    console.print(char * tw(), style=style)

def clear():
    if os.name == "nt":
        os.system("cls")
    else:
        sys.stdout.write("\033[2J\033[3J\033[H")
        sys.stdout.flush()

def erase_prompt_line():
    sys.stdout.write("\033[F")
    sys.stdout.write("\033[2K")
    sys.stdout.flush()

def abs_path(p: str) -> str:
    p = os.path.expanduser(p)
    if not os.path.isabs(p):
        p = os.path.join(S["cwd"], p)
    return os.path.normpath(p)

# ── INTERACTIVE PICKER ────────────────────────────────────────────────────────
def interactive_picker(items: list, current=None, title="Select"):
    if not items:
        return None

    if not HAS_PT:
        console.print(f"\n  [{WH}]{title}[/]\n")
        for i, item in enumerate(items):
            mark = f"[{O}]▶[/]" if item == current else " "
            console.print(f"  {mark} [{BLU}]{i+1:2}[/]  {item}")
        try:
            raw = input("\n  Number: ").strip()
            idx = int(raw) - 1
            if 0 <= idx < len(items):
                return items[idx]
        except (ValueError, KeyboardInterrupt):
            pass
        return None

    start  = items.index(current) if current in items else 0
    state  = {"idx": start, "result": None}

    def get_text():
        out = [("", f"\n  {title}\n\n")]
        for i, item in enumerate(items):
            if i == state["idx"]:
                out.append((f"fg:{O} bold", f"  ▶  {item}\n"))
            else:
                out.append((f"fg:{TXT}", f"     {item}\n"))
        out.append(("fg:#555555", "\n  ↑/↓ navigate   Enter select   Esc cancel\n"))
        return out

    kb = KeyBindings()

    @kb.add("up")
    def _(e): state["idx"] = (state["idx"] - 1) % len(items)

    @kb.add("down")
    def _(e): state["idx"] = (state["idx"] + 1) % len(items)

    @kb.add("enter")
    def _(e):
        state["result"] = items[state["idx"]]
        e.app.exit()

    @kb.add("escape")
    @kb.add("c-c")
    def _(e): e.app.exit()

    Application(
        layout=Layout(Window(FormattedTextControl(get_text, focusable=True))),
        key_bindings=kb,
        full_screen=False,
    ).run()
    return state["result"]

def ask_permission(action: str, detail: str, preview: str = "") -> bool:
    if S["auto_allow"]:
        console.print(Panel(
            Text(f"Allowed automatically\n{action}\n{detail}", style=TXT),
            title=Text(" Permission ", style=f"bold {O}"),
            border_style=O,
            box=box.ROUNDED,
            padding=(0, 1),
        ))
        return True

    body = Text()
    body.append("Action: ", style=WH)
    body.append(action + "\n", style=f"bold {O}")
    body.append("Target: ", style=WH)
    body.append(detail + "\n", style=TXT)

    if preview:
        body.append("\nPreview:\n", style=WH)
        for line in preview.splitlines()[:8]:
            body.append(f"  {escape(line)}\n", style=f"dim {TXT}")

    console.print(Panel(
        body,
        title=Text(" 🤖 Permission Required ", style=f"bold {O}"),
        border_style=O,
        box=box.ROUNDED,
        padding=(0, 1),
    ))

    choice = interactive_picker(
        ["Allow", "Deny", "Allow All"],
        current="Allow",
        title="Choose permission"
    )

    if choice == "Allow":
        return True

    if choice == "Deny":
        console.print(Panel(
            Text(f"Denied\n{action}", style=RED),
            title=Text(" Permission ", style=f"bold {RED}"),
            border_style=RED,
            box=box.ROUNDED,
            padding=(0, 1),
        ))
        return False

    if choice == "Allow All":
        S["auto_allow"] = True
        save_settings()
        return True

    return False

def tool_run_command(command: str, explanation: str) -> str:
    if not ask_permission("Run shell command", command, f"$ {command}"):
        return "Permission denied."

    try:
        result = subprocess.run(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=S["cwd"],
            timeout=30,
        )

        stdout = result.stdout.decode("utf-8", errors="replace")
        stderr = result.stderr.decode("utf-8", errors="replace")
        out = (stdout + stderr).strip()

        if command.strip().startswith("cd "):
            nd = abs_path(command.strip()[3:].strip())
            if os.path.isdir(nd):
                S["cwd"] = nd

        status = "Completed" if result.returncode == 0 else f"Failed with exit {result.returncode}"
        message = out or "(no output)"

        console.print(Panel(
            Text(f"{status}\n\n{message}", style=TXT),
            title=Text(" Command Result ", style=f"bold {O}"),
            border_style=O if result.returncode == 0 else RED,
            box=box.ROUNDED,
            padding=(0, 1),
        ))

        return message

    except subprocess.TimeoutExpired:
        return "Timed out after 30 seconds."

    except Exception:
        return "Command failed."
        
def tool_delete_path(path: str) -> str:
    full = abs_path(path)

    if not ask_permission("Delete path", full):
        return "Permission denied."

    try:
        if os.path.isdir(full):
            shutil.rmtree(full)
            return f"Deleted folder: {full}"

        if os.path.isfile(full):
            os.remove(full)
            return f"Deleted file: {full}"

        return f"Not found: {full}"

    except Exception:
        return "Delete failed."


def tool_move_path(src: str, dst: str) -> str:
    src_full = abs_path(src)
    dst_full = abs_path(dst)

    if not ask_permission("Move/Rename path", f"{src_full} → {dst_full}"):
        return "Permission denied."

    try:
        os.makedirs(os.path.dirname(dst_full) or ".", exist_ok=True)
        shutil.move(src_full, dst_full)
        return f"Moved: {src_full} → {dst_full}"

    except Exception:
        return "Move failed."


def tool_append_file(path: str, content: str, explanation: str = "") -> str:
    full = abs_path(path)

    if not ask_permission("Append to file", full, content):
        return "Permission denied."

    try:
        os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
        with open(full, "a", encoding="utf-8", errors="replace") as f:
            f.write(content)

        return f"Appended to file: {full}"

    except Exception:
        return "Append failed."

def tool_write_file(path: str, content: str, explanation: str) -> str:
    full   = abs_path(path)
    action = "Create" if not os.path.exists(full) else "Overwrite"
    console.print(f"\n  [{PUR}]  {action}[/] [{DIM}]{escape(full)}[/]")
    if not ask_permission(f"{action} file", full, content):
        return "Permission denied."
    try:
        os.makedirs(os.path.dirname(full) or ".", exist_ok=True)
        with open(full, "w", encoding="utf-8") as f:
            f.write(content)
        console.print(f"  [{GRN}]✓ Written ({len(content)} bytes)[/]")
        return f"File written: {full}"
    except Exception as e:
        return f"Error: {e}"
        
def tool_make_dir(path: str) -> str:
    full = abs_path(path)

    if not ask_permission("Create folder", full):
        return "Permission denied."

    try:
        os.makedirs(full, exist_ok=True)

        console.print(Panel(
            Text(f"Created folder\n{full}", style=TXT),
            title=Text(" Folder Created ", style=f"bold {O}"),
            border_style=O,
            box=box.ROUNDED,
            padding=(0, 1),
        ))

        return f"Created folder: {full}"

    except Exception as e:
        return f"Error: {e}"

def tool_read_file(path: str) -> str:
    full = abs_path(path)

    console.print(f"  [{BLU}]Read[/] [{DIM}]{escape(full)}[/]")

    try:
        with open(full, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()

        console.print(f"  [{O}]Done[/] [{DIM}]{len(content.splitlines())} lines[/]")
        return content

    except Exception as e:
        return f"Error: {e}"

def tool_list_dir(path: str) -> str:
    full = abs_path(path)

    try:
        items = sorted(os.listdir(full))
        result = []

        for item in items:
            fp = os.path.join(full, item)
            if os.path.isdir(fp):
                result.append(f"DIR   {item}/")
            else:
                size = os.path.getsize(fp)
                result.append(f"FILE  {item}  ({size}b)")

        return "\n".join(result) or "(empty)"

    except Exception as e:
        return f"Error: {e}"

def tool_patch_file(path: str, old_text: str, new_text: str, explanation: str) -> str:
    full = abs_path(path)
    console.print(f"\n  [{PUR}]  Patch[/] [{DIM}]{escape(full)}[/]")
    try:
        with open(full, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception as e:
        return f"Error reading: {e}"
    if old_text not in content:
        return f"Error: search text not found in {full}"
    if not ask_permission("Patch file", full, f"- {old_text[:200]}\n+ {new_text[:200]}"):
        return "Permission denied."
    new_content = content.replace(old_text, new_text, 1)
    try:
        with open(full, "w", encoding="utf-8") as f:
            f.write(new_content)
        console.print(f"  [{GRN}]✓ Patched[/]")
        return f"Patched: {full}"
    except Exception as e:
        return f"Error: {e}"

TOOL_DEFS = [
    {
        "name": "run_command",
        "description": "Execute a shell command on the user's computer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string"},
                "explanation": {"type": "string"},
            },
            "required": ["command", "explanation"],
        },
    },
    {
        "name": "write_file",
        "description": "Create or overwrite a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
                "explanation": {"type": "string"},
            },
            "required": ["path", "content", "explanation"],
        },
    },
    {
        "name": "append_file",
        "description": "Append content to a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"},
                "explanation": {"type": "string"},
            },
            "required": ["path", "content", "explanation"],
        },
    },
    {
        "name": "make_dir",
        "description": "Create a directory or folder.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "delete_path",
        "description": "Delete a file or folder.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "move_path",
        "description": "Move or rename a file or folder.",
        "input_schema": {
            "type": "object",
            "properties": {
                "src": {"type": "string"},
                "dst": {"type": "string"},
            },
            "required": ["src", "dst"],
        },
    },
    {
        "name": "read_file",
        "description": "Read a file's contents.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "list_directory",
        "description": "List files and directories.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
            },
            "required": ["path"],
        },
    },
    {
        "name": "patch_file",
        "description": "Replace an exact string in a file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "old_text": {"type": "string"},
                "new_text": {"type": "string"},
                "explanation": {"type": "string"},
            },
            "required": ["path", "old_text", "new_text", "explanation"],
        },
    },
]

def dispatch_tool(name: str, inp: dict) -> str:
    if name == "run_command":
        return tool_run_command(inp["command"], inp.get("explanation", ""))

    if name == "write_file":
        return tool_write_file(inp["path"], inp["content"], inp.get("explanation", ""))

    if name == "append_file":
        return tool_append_file(inp["path"], inp["content"], inp.get("explanation", ""))

    if name == "read_file":
        return tool_read_file(inp["path"])

    if name == "list_directory":
        return tool_list_dir(inp.get("path", S["cwd"]))

    if name == "make_dir":
        return tool_make_dir(inp["path"])

    if name == "delete_path":
        return tool_delete_path(inp["path"])

    if name == "move_path":
        return tool_move_path(inp["src"], inp["dst"])

    if name == "patch_file":
        return tool_patch_file(
            inp["path"],
            inp["old_text"],
            inp["new_text"],
            inp.get("explanation", "")
        )

    return f"Unknown tool: {name}"

SYSTEM_PROMPT = """\
You are Flaude, an AI coding assistant with full access to the user's computer.

CRITICAL RULES:
- NEVER just show code for actions that affect the system.
- ALWAYS use tools when performing actions.
- Creating folders → use make_dir
- Creating files → use write_file
- Running commands → use run_command

Do not simulate actions. Actually execute them using tools.

CWD: {cwd}  OS: {os}  Python: {py}
""".strip()

def _sys_prompt():
    return SYSTEM_PROMPT.format(
        cwd=S["cwd"], os=sys.platform, py=sys.version.split()[0]
    )

# ── AI BACKENDS ───────────────────────────────────────────────────────────────
def ai_anthropic(user_msg: str) -> str:
    if not HAS_ANTHROPIC:
        console.print(f"  [{RED}]anthropic SDK missing. Run: pip install anthropic[/]\n")
        return ""
    if not S["api_key"]:
        console.print(
            f"  [{RED}]No API key.[/]  Use [{O}]/key sk-ant-…[/] or set the "
            f"[{O}]ANTHROPIC_API_KEY[/] environment variable.\n"
            f"  [{DIM}]Anthropic is optional — you can switch backend with /backend or /connect.[/]\n"
        )
        return ""

    client = _anthropic.Anthropic(api_key=S["api_key"])
    msgs   = list(S["history"]) + [{"role": "user", "content": user_msg}]
    console.print(f"  [{DIM}]⟳ Thinking…[/]", end="\r")

    while True:
        try:
            resp = client.messages.create(
                model=S["model"],
                max_tokens=S.get("max_tokens", 4096),
                system=_sys_prompt(),
                tools=TOOL_DEFS,
                messages=msgs,
            )
        except Exception as e:
            console.print(f"  [{RED}]Anthropic error: {escape(str(e))}[/]\n")
            return ""

        text_parts, tool_calls = [], []
        for block in resp.content:
            if block.type == "text":       text_parts.append(block.text)
            elif block.type == "tool_use": tool_calls.append(block)

        if text_parts:
            console.print(" " * 30, end="\r")
            _render_ai_text("\n".join(text_parts))

        if resp.stop_reason == "end_turn" or not tool_calls:
            final = "\n".join(text_parts)
            S["history"].append({"role": "user",      "content": user_msg})
            S["history"].append({"role": "assistant",  "content": resp.content})
            S["last_response"] = final
            if len(S["history"]) > 40:
                S["history"] = S["history"][-40:]
            return final

        msgs.append({"role": "assistant", "content": resp.content})
        tool_results = []
        for tc in tool_calls:
            result = dispatch_tool(tc.name, tc.input)
            tool_results.append({"type": "tool_result", "tool_use_id": tc.id, "content": str(result)})
            console.print(f"  [{DIM}]⟳ Thinking…[/]", end="\r")
        msgs.append({"role": "user", "content": tool_results})


def ai_ollama(user_msg: str) -> str:
    if not HAS_REQUESTS:
        console.print(f"  [{O}]requests missing. Run: pip install requests[/]\n")
        return ""

    tool_instructions = """
You can use tools by replying ONLY with JSON when action is needed.

Available tools:
- make_dir: {"tool":"make_dir","path":"..."}
- run_command: {"tool":"run_command","command":"...","explanation":"..."}
- write_file: {"tool":"write_file","path":"...","content":"...","explanation":"..."}
- append_file: {"tool":"append_file","path":"...","content":"...","explanation":"..."}
- read_file: {"tool":"read_file","path":"..."}
- list_directory: {"tool":"list_directory","path":"..."}
- delete_path: {"tool":"delete_path","path":"..."}
- move_path: {"tool":"move_path","src":"...","dst":"..."}
- patch_file: {"tool":"patch_file","path":"...","old_text":"...","new_text":"...","explanation":"..."}

For multiple tasks, reply with a JSON array.

Important:
- If you say you will read/list/write/delete/create/run something, you MUST use a tool.
- Do NOT only say "I'll read it" or "I'll check it". Actually use the tool.
- If a tool returns an error, do NOT repeat the same failing command.
- If finished, briefly summarize.
- When using tools, reply ONLY with JSON. No markdown.
"""

    messages = [{"role": "system", "content": _sys_prompt() + "\n\n" + tool_instructions}]

    for m in S["history"]:
        if isinstance(m.get("content"), str):
            messages.append({"role": m["role"], "content": m["content"]})

    messages.append({"role": "user", "content": user_msg})

    url = f"http://{S['host']}:{S['port']}/api/chat"

    final_text = ""
    total_text = ""
    total_start = time.time()
    max_rounds = 4
    printed_cancel = False
    seen_tool_calls = set()

    for round_idx in range(max_rounds):
        payload = {
            "model": S["model"],
            "messages": messages,
            "stream": True,
            "options": {
                "num_predict": S.get("max_tokens", 4096),
            },
        }

        text = ""
        live_text = ""
        frames = ["Thinking", "Thinking.", "Thinking..", "Thinking..."]
        i = 0

        def make_live_panel(label: str):
            body = Text()
            body.append(label + "\n\n", style=f"bold {O}")
            body.append(live_text[-2500:] if live_text else "Waiting for Ollama...", style=DIM)

            return Panel(
                body,
                title=Text(" Live output ", style=f"bold {O}"),
                border_style=O,
                box=box.ROUNDED,
                padding=(0, 1),
            )

        live_ctx = None

        try:
            if not printed_cancel:
                console.print(f"  [{DIM}]ESC to cancel[/]")
                printed_cancel = True

            if S.get("live", False):
                live_ctx = Live(
                    make_live_panel("⟳ Connecting  [0 tokens]"),
                    console=console,
                    refresh_per_second=8,
                    transient=True,
                )
                live_ctx.start()
            else:
                console.print(f"  [{O}]⟳ Connecting  [0 tokens][/] ", end="\r")

            with _requests.post(url, json=payload, stream=True, timeout=(5, None)) as r:
                r.raise_for_status()

                last_draw = 0

                for line in r.iter_lines(decode_unicode=True):
                    now = time.time()

                    if not line:
                        continue

                    try:
                        data = json.loads(line)
                    except Exception:
                        continue

                    msg = data.get("message")
                    chunk = msg.get("content", "") if isinstance(msg, dict) else ""

                    if chunk:
                        text += chunk
                        live_text += chunk

                    if now - last_draw > 0.12:
                        elapsed = int(now - total_start)
                        seconds = f" · {elapsed}s" if elapsed > 30 else ""
                        approx_tokens = max(1, len(total_text + text) // 4)
                        frame = frames[i % len(frames)]
                        label = f"⟳ {frame}  [{approx_tokens} tokens]{seconds}"

                        if live_ctx:
                            live_ctx.update(make_live_panel(label))
                        else:
                            sys.stdout.write("\r" + " " * 160 + "\r")
                            console.print(f"  [{O}]{label}[/]", end="\r")
                            sys.stdout.flush()

                        last_draw = now
                        i += 1

                    if data.get("done"):
                        break

            if live_ctx:
                live_ctx.stop()
                live_ctx = None
            else:
                sys.stdout.write("\r\033[2K")
                sys.stdout.flush()

            text = text.strip()
            final_text = text
            total_text += text

            tool_calls = []

            try:
                cleaned = text.strip()

                fenced = re.search(
                    r"```(?:json)?\s*(\[.*?\]|\{.*?\})\s*```",
                    cleaned,
                    re.DOTALL,
                )

                if fenced:
                    cleaned = fenced.group(1)
                else:
                    loose_array = re.search(r"(\[\s*\{.*?\}\s*\])", cleaned, re.DOTALL)
                    loose_object = re.search(r"(\{\s*\"tool\"\s*:\s*\".*?\".*?\})", cleaned, re.DOTALL)

                    if loose_array:
                        cleaned = loose_array.group(1)
                    elif loose_object:
                        cleaned = loose_object.group(1)

                data = json.loads(cleaned)

                if isinstance(data, dict) and "tool" in data:
                    tool_calls = [data]
                elif isinstance(data, list):
                    tool_calls = [
                        x for x in data
                        if isinstance(x, dict) and "tool" in x
                    ]

            except Exception:
                tool_calls = []

            if not tool_calls:
                final_display = text if text.strip() else "Model returned empty response."

                token_count = max(1, len(final_display) // 4)
                elapsed_total = int(time.time() - total_start)

                console.print(Panel(
                    Text(final_display, style=TXT),
                    title=Text(
                        f" Flaude • {token_count} tokens • {elapsed_total}s ",
                        style=f"bold {O}",
                    ),
                    border_style=O,
                    box=box.ROUNDED,
                    padding=(0, 1),
                ))

                S["history"].append({"role": "user", "content": user_msg})
                S["history"].append({"role": "assistant", "content": final_display})
                S["last_response"] = final_display

                if len(S["history"]) > 40:
                    S["history"] = S["history"][-40:]

                return final_display

            tool_results = []

            for call in tool_calls:
                call_key = json.dumps(call, sort_keys=True)

                if call_key in seen_tool_calls:
                    tool_results.append("Skipped repeated tool call.")
                    continue

                seen_tool_calls.add(call_key)

                tool_name = call.pop("tool")
                result = dispatch_tool(tool_name, call)
                tool_results.append(f"{tool_name}: {result}")

            result_text = "\n".join(tool_results)

            messages.append({"role": "assistant", "content": text})
            messages.append({
                "role": "user",
                "content": (
                    "Tool results:\n"
                    + result_text
                    + "\n\nContinue the user's request. "
                      "If a tool failed, do not repeat the same exact command. "
                      "If more action is needed, reply ONLY with tool JSON. "
                      "If finished, briefly summarize what you did."
                ),
            })

        except KeyboardInterrupt:
            if live_ctx:
                live_ctx.stop()
            sys.stdout.write("\r\033[2K")
            sys.stdout.flush()
            console.print(f"\n  [{O}]Cancelled.[/]\n")
            return ""

        except _requests.exceptions.ConnectionError:
            if live_ctx:
                live_ctx.stop()
            console.print(Panel(
                Text("Could not connect to Ollama.", style=TXT),
                title=Text(" Flaude ", style=f"bold {O}"),
                border_style=O,
                box=box.ROUNDED,
                padding=(0, 1),
            ))
            return ""

        except Exception:
            if live_ctx:
                live_ctx.stop()
            console.print(Panel(
                Text("Something went wrong while talking to the model.", style=TXT),
                title=Text(" Flaude ", style=f"bold {O}"),
                border_style=O,
                box=box.ROUNDED,
                padding=(0, 1),
            ))
            return ""

    console.print(Panel(
        Text("Stopped after too many tool steps. The model may be stuck repeating an action.", style=TXT),
        title=Text(" Flaude ", style=f"bold {O}"),
        border_style=O,
        box=box.ROUNDED,
        padding=(0, 1),
    ))

    return final_text
        
        
        # end of ai_ollama
        
OPENAI_COMPAT_BACKENDS = {
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1",
        "model": "openai/gpt-4o-mini",
        "key_env": "OPENROUTER_API_KEY",
    },
    "nvidia_nim": {
        "base_url": "https://integrate.api.nvidia.com/v1",
        "model": "meta/llama-3.1-70b-instruct",
        "key_env": "NVIDIA_API_KEY",
    },
    "lmstudio": {
        "base_url": "http://localhost:1234/v1",
        "model": "local-model",
        "key_env": "",
    },
    "llamacpp": {
        "base_url": "http://localhost:8080/v1",
        "model": "local-model",
        "key_env": "",
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/v1",
        "model": "deepseek-chat",
        "key_env": "DEEPSEEK_API_KEY",
    },
    "groq": {
        "base_url": "https://api.groq.com/openai/v1",
        "model": "llama-3.1-8b-instant",
        "key_env": "GROQ_API_KEY",
    },
    "together": {
        "base_url": "https://api.together.xyz/v1",
        "model": "meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo",
        "key_env": "TOGETHER_API_KEY",
    },
}

def ai_openai_compat(user_msg: str) -> str:
    if not HAS_REQUESTS:
        console.print(f"  [{O}]requests missing. Run: pip install requests[/]\n")
        return ""

    base_url = S.get("base_url", "").rstrip("/")
    api_key = S.get("openai_key", "")

    if not base_url:
        console.print(Panel(
            Text("No base URL set. Use /backend openrouter, /backend lmstudio, etc.", style=TXT),
            title=Text(" Flaude ", style=f"bold {O}"),
            border_style=O,
            box=box.ROUNDED,
            padding=(0, 1),
        ))
        return ""

    headers = {
        "Content-Type": "application/json",
    }

    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"

    messages = [{"role": "system", "content": _sys_prompt()}]

    for m in S["history"]:
        if isinstance(m.get("content"), str):
            messages.append({"role": m["role"], "content": m["content"]})

    messages.append({"role": "user", "content": user_msg})

    payload = {
        "model": S["model"],
        "messages": messages,
        "max_tokens": S.get("max_tokens", 4096),
        "stream": True,
    }

    url = f"{base_url}/chat/completions"

    text = ""
    start = time.time()
    frames = ["Thinking", "Thinking.", "Thinking..", "Thinking..."]
    last_draw = 0
    i = 0

    try:
        console.print(f"  [{DIM}]ESC to cancel[/]")

        with _requests.post(url, headers=headers, json=payload, stream=True, timeout=(5, None)) as r:
            r.raise_for_status()

            for line in r.iter_lines(decode_unicode=True):
                now = time.time()

                if not line:
                    continue

                line = line.strip()

                if line.startswith("data:"):
                    line = line[5:].strip()

                if line == "[DONE]":
                    break

                try:
                    data = json.loads(line)
                except Exception:
                    continue

                choices = data.get("choices", [])
                if not choices:
                    continue

                delta = choices[0].get("delta", {})
                chunk = delta.get("content", "")

                if chunk:
                    text += chunk

                if now - last_draw > 0.12:
                    elapsed = int(now - start)
                    seconds = f" · {elapsed}s" if elapsed > 30 else ""
                    approx_tokens = max(1, len(text) // 4)
                    frame = frames[i % len(frames)]
                    label = f"⟳ {frame}  [{approx_tokens} tokens]{seconds}"

                    sys.stdout.write("\r" + " " * 160 + "\r")
                    console.print(f"  [{O}]{label}[/]", end="\r")
                    sys.stdout.flush()

                    last_draw = now
                    i += 1

        sys.stdout.write("\r\033[2K")
        sys.stdout.flush()

        final_display = text.strip() or "Model returned empty response."
        token_count = max(1, len(final_display) // 4)
        elapsed_total = int(time.time() - start)

        console.print(Panel(
            Text(final_display, style=TXT),
            title=Text(
                f" Flaude • {token_count} tokens • {elapsed_total}s ",
                style=f"bold {O}",
            ),
            border_style=O,
            box=box.ROUNDED,
            padding=(0, 1),
        ))

        S["history"].append({"role": "user", "content": user_msg})
        S["history"].append({"role": "assistant", "content": final_display})
        S["last_response"] = final_display

        if len(S["history"]) > 40:
            S["history"] = S["history"][-40:]

        return final_display

    except KeyboardInterrupt:
        sys.stdout.write("\r\033[2K")
        sys.stdout.flush()
        console.print(f"\n  [{O}]Cancelled.[/]\n")
        return ""

    except Exception:
        console.print(Panel(
            Text("Something went wrong while talking to the selected backend.", style=TXT),
            title=Text(" Flaude ", style=f"bold {O}"),
            border_style=O,
            box=box.ROUNDED,
            padding=(0, 1),
        ))
        return ""

def ai_respond(user_msg: str) -> str:
    if S["backend"] == "ollama":
        return ai_ollama(user_msg)

    if S["backend"] == "anthropic":
        return ai_anthropic(user_msg)

    if S["backend"] in OPENAI_COMPAT_BACKENDS or S.get("base_url"):
        return ai_openai_compat(user_msg)

    return ai_anthropic(user_msg)


def _render_ai_text(text: str):
    if not text.strip():
        return
    parts  = re.split(r"(```(?:\w+)?\n.*?```)", text, flags=re.DOTALL)
    result = Text()
    for part in parts:
        if part.startswith("```"):
            m = re.match(r"```(\w+)?\n(.*?)```", part, re.DOTALL)
            if m:
                lang  = m.group(1) or ""
                code  = m.group(2)
                label = f" {lang} " if lang else " code "
                result.append(f"\n  ┌─{label}{'─'*(38-len(label))}┐\n", style=BDR)
                for ln in code.splitlines():
                    result.append(f"  │ {ln}\n", style=f"bold {GRN}")
                result.append(f"  └{'─'*40}┘\n", style=BDR)
        else:
            for line in part.splitlines():
                if line.strip():
                    result.append(f"  {line}\n", style=TXT)
                else:
                    result.append("\n")
    console.print(
        Panel(result, border_style=BDR, box=box.ROUNDED,
              title=Text(" Flaude ", style=f"bold {O}"),
              title_align="left", padding=(0, 1))
    )

def build_welcome():
    w  = tw()
    lw = min(max(w // 3, 30), 44)
    rw = max(w - lw - 6, 40)

    left = Text(no_wrap=False, overflow="fold")
    left.append("\n")
    for line in LOGO:
        pad = (lw - len(line)) // 2
        left.append(" " * max(pad, 0) + line + "\n", style=f"bold {O}")
    left.append("\n")

    title_str = "Flaude Code"
    pad = (lw - len(title_str)) // 2
    left.append(" " * max(pad, 0) + title_str + "\n", style=WH)
    left.append("\n")

    for info in [S["model"], f"{S['backend'].upper()} · {S['host']}:{S['port']}",
                 short_path(), f"settings → {SETTINGS_FILE}"]:
        pad = (lw - len(info)) // 2
        left.append(" " * max(pad, 0) + info + "\n", style=DIM)
    left.append("\n")

    right = Text(no_wrap=False, overflow="fold")
    right.append("\n")
    right.append(" Who Made Flaude?\n", style=WH)
    right.append(" " + "─" * (rw - 2) + "\n", style=BDR)
    for n in [
        "https://github.com/Kynix09/Flaude",
    ]:
        right.append(f"  • {n}\n", style=TXT)

    right.append("\n")
    right.append(" Quick start\n", style=WH)
    right.append(" " + "─" * (rw - 2) + "\n", style=BDR)
    for tip in [
        "Type / and Tab to browse all commands.",
        "/connect localhost:11434  — switch backend (/backend or /connect)",
        "/key sk-ant-…            — set your Anthropic API key.",
        "/model                   — pick a model with arrow keys.",
        "/doctor                  — diagnose your setup.",
        "/help                    — full command list.",
    ]:
        right.append(f"  · {tip}\n", style=TXT)

    grid = Table.grid(padding=0)
    grid.add_column(width=lw)
    grid.add_column(width=1)
    grid.add_column(width=rw)
    div = Text("".join("│\n" for _ in range(22)), style=BDR)
    grid.add_row(left, div, right)

    title = Text()
    title.append(" Flaude Code ", style=f"bold {O}")
    title.append(f"v{S['version']} ", style=DIM)
    return Panel(grid, title=title, title_align="left",
                 border_style=BDR, box=box.ROUNDED, padding=(0, 1))


def compact_header():
    t = Text()
    t.append(" Flaude ", style=f"bold {O}")
    t.append("─", style=BDR)
    t.append(f" {S['model']} ", style=DIM)
    t.append("─", style=BDR)
    t.append(f" {S['backend']} ", style=DIM)
    t.append("─", style=BDR)
    t.append(f" {short_path()} ", style=f"dim {TXT}")
    console.print(t)


def print_footer():
    return


def draw_full_ui():
    clear()
    console.print(build_welcome())
    sep()
    console.print()  # blank — footer drawn by main loop

CMDS: dict      = {}
CMD_HELP: dict  = {}
CMD_GROUP: dict = {}

def cmd(name, help_text="", group="misc"):
    def dec(fn):
        CMDS[name]      = fn
        CMD_HELP[name]  = help_text
        CMD_GROUP[name] = group
        return fn
    return dec


@cmd("/help", "Show all commands", "session")
def c_help(_):
    draw_full_ui()
    console.print()
    groups = {}
    for name in sorted(CMDS):
        g = CMD_GROUP.get(name, "misc")
        groups.setdefault(g, []).append(name)
    order = ["session", "model", "context", "config", "files", "ollama", "misc"]
    for g in order:
        names = groups.get(g, [])
        if not names:
            continue
        console.print(f"  [{O}]{g.upper()}[/]")
        t = Table(show_header=False, border_style=BDR, box=box.SIMPLE, padding=(0, 1))
        t.add_column(style=BLU, width=20, no_wrap=True)
        t.add_column(style=TXT)
        for name in names:
            t.add_row(name, CMD_HELP.get(name, ""))
        console.print(t)
    console.print()
    
@cmd("/max", "Set max tokens", "config")
def c_max(args):
    if not args:
        console.print(f"  [{O}]Current max tokens:[/] [{TXT}]{S.get('max_tokens', 4096)}[/]\n")
        return

    try:
        value = int(args[0])

        if value < 1:
            raise ValueError

        S["max_tokens"] = value
        save_settings()

        console.print(f"  [{O}]✓ Max tokens set to[/] [{TXT}]{value}[/]\n")

    except ValueError:
        console.print(f"  [{O}]Invalid number. Example:[/] /max 8192\n")

@cmd("/clear", "Clear screen and reset conversation", "session")
def c_clear(_):
    S["history"].clear(); S["last_response"] = ""
    draw_full_ui()

@cmd("/reset", "Alias for /clear", "session")
def c_reset(a): c_clear(a)

@cmd("/new", "New conversation (keep settings)", "session")
def c_new(_):
    S["history"].clear(); S["last_response"] = ""
    clear(); compact_header()
    console.print(f"\n  [{GRN}]✓ New conversation started.[/]\n")

@cmd("/exit", "Exit Flaude", "session")
def c_exit(_):
    console.print(f"\n  [{DIM}]Goodbye.[/]\n")
    sys.exit(0)

@cmd("/quit", "Exit Flaude", "session")
def c_quit(a): c_exit(a)

@cmd("/export", "Save conversation to file  /export [filename]", "session")
def c_export(args):
    if not S["history"]:
        console.print(f"\n  [{YLW}]No conversation to export.[/]\n"); return
    ts    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = args[0] if args else f"flaude_{ts}.json"
    fpath = abs_path(fname)
    data  = {
        "exported": ts, "model": S["model"], "backend": S["backend"],
        "history": [
            {"role": m["role"], "content": m["content"]}
            for m in S["history"] if isinstance(m.get("content"), str)
        ],
    }
    with open(fpath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    console.print(f"\n  [{GRN}]✓ Exported → {fpath}[/]\n")

@cmd("/save", "Alias for /export", "session")
def c_save(a): c_export(a)

@cmd("/copy", "Copy last AI response to clipboard", "session")
def c_copy(_):
    if not S["last_response"]:
        console.print(f"\n  [{YLW}]Nothing to copy yet.[/]\n"); return
    text = S["last_response"].encode()
    try:
        if os.name == "nt":
            subprocess.run("clip",                           input=text, check=True)
        elif shutil.which("pbcopy"):
            subprocess.run("pbcopy",                         input=text, check=True)
        elif shutil.which("xclip"):
            subprocess.run(["xclip","-selection","clipboard"],input=text, check=True)
        elif shutil.which("xsel"):
            subprocess.run(["xsel","--clipboard","--input"],  input=text, check=True)
        else:
            console.print(f"\n  [{YLW}]No clipboard tool found (xclip/xsel/pbcopy).[/]\n"); return
        console.print(f"\n  [{GRN}]✓ Copied to clipboard.[/]\n")
    except Exception as e:
        console.print(f"\n  [{RED}]Copy failed: {e}[/]\n")

# ── Model ──────────────────────────────────────────────────────────────────────
@cmd("/model", "Pick model interactively or /model <name|provider/name>", "model")
def c_model(args):
    if args:
        raw = args[0]
        _apply_model(raw)
        console.print(f"\n  [{GRN}]✓ Model → {S['model']}  backend={S['backend']}[/]\n")
        save_settings(); return

    # Interactive ──────────────────────────────────────────────────────────
    anthropic_models = [
        "claude-opus-4-6", "claude-sonnet-4-6", "claude-haiku-4-5",
        "claude-opus-4-5", "claude-sonnet-4-5",
    ]
    ollama_models = [
        "llama3", "llama3.1", "llama3.2", "mistral", "codestral",
        "deepseek-coder", "phi3", "phi4", "gemma2", "qwen2.5-coder",
    ]
    if HAS_REQUESTS:
        try:
            r = _requests.get(f"http://{S['host']}:{S['port']}/api/tags", timeout=3)
            fetched = [m["name"] for m in r.json().get("models", [])]
            if fetched:
                ollama_models = fetched
        except Exception:
            pass

    CUSTOM_OPT = "[ type custom model… ]"
    items = (["── Anthropic ──"] + anthropic_models +
             ["── Ollama ──"]    + ollama_models +
             [CUSTOM_OPT])
    HEADERS = {"── Anthropic ──", "── Ollama ──"}

    console.print()
    selected = interactive_picker(items, current=S["model"],
                                  title="Select model  (↑↓ navigate, Enter select)")
    console.print()

    if selected is None or selected in HEADERS:
        return

    if selected == CUSTOM_OPT:
        console.print(f"  [{O}]Model (e.g. ollama/phi4 or claude-opus-4-6): [/]", end="")
        selected = input().strip()
        if not selected:
            return

    _apply_model(selected, ollama_models)
    console.print(f"  [{GRN}]✓ Model → {S['model']}  backend={S['backend']}[/]\n")
    save_settings()


def _apply_model(raw: str, known_ollama=()):
    """Parse optional provider/model prefix and update S."""
    if "/" in raw:
        provider, _, mname = raw.partition("/")
        p = provider.lower()

        if p in ("anthropic", "claude"):
            S["backend"] = "anthropic"
            S["model"] = mname or raw
            return

        if p in ("ollama", "local"):
            S["backend"] = "ollama"
            S["model"] = mname or raw
            return

        if p in OPENAI_COMPAT_BACKENDS:
            S["backend"] = p
            cfg = OPENAI_COMPAT_BACKENDS[p]
            S["base_url"] = cfg["base_url"]
            S["model"] = mname or cfg["model"]

            env_name = cfg.get("key_env", "")
            if env_name:
                S["openai_key"] = os.environ.get(env_name, S.get("openai_key", ""))
            else:
                S["openai_key"] = ""
            return

        S["model"] = raw
        return

    S["model"] = raw

    if any(raw.startswith(p) for p in ("claude-", "claude_")):
        S["backend"] = "anthropic"
    elif raw in known_ollama:
        S["backend"] = "ollama"


@cmd("/models", "List models available in Ollama", "model")
def c_models(_):
    if not HAS_REQUESTS:
        console.print(f"\n  [{RED}]requests not installed.[/]\n"); return
    try:
        r      = _requests.get(f"http://{S['host']}:{S['port']}/api/tags", timeout=5)
        models = r.json().get("models", [])
        if not models:
            console.print(f"\n  [{YLW}]No models found in Ollama.[/]\n"); return
        t = Table(show_header=True, header_style=f"bold {O}",
                  border_style=BDR, box=box.SIMPLE_HEAD)
        t.add_column("Model",    style=BLU)
        t.add_column("Size",     style=TXT)
        t.add_column("Modified", style=DIM)
        for m in models:
            sz  = m.get("size", 0)
            t.add_row(m["name"],
                      f"{sz/1e9:.1f}GB" if sz > 1e9 else f"{sz/1e6:.0f}MB",
                      m.get("modified_at", "")[:10])
        console.print()
        console.print(t)
        console.print()
    except Exception as e:
        console.print(f"\n  [{RED}]Could not reach Ollama: {e}[/]\n")


@cmd("/backend", "Switch backend", "model")
def c_backend(args):
    choices = [
        "anthropic",
        "ollama",
        "openrouter",
        "nvidia_nim",
        "lmstudio",
        "llamacpp",
        "deepseek",
        "groq",
        "together",
    ]

    if args:
        selected = args[0].lower()
    else:
        selected = interactive_picker(
            choices,
            current=S["backend"],
            title="Select backend"
        )

    if not selected:
        return

    if selected not in choices:
        console.print(f"\n  [{O}]Unknown backend:[/] [{TXT}]{selected}[/]\n")
        return

    S["backend"] = selected

    if selected in OPENAI_COMPAT_BACKENDS:
        cfg = OPENAI_COMPAT_BACKENDS[selected]
        S["base_url"] = cfg["base_url"]
        S["model"] = cfg["model"]

        env_name = cfg.get("key_env", "")
        if env_name:
            S["openai_key"] = os.environ.get(env_name, S.get("openai_key", ""))
        else:
            S["openai_key"] = ""

    save_settings()

    console.print(Panel(
        Text(
            f"Backend: {S['backend']}\n"
            f"Model: {S['model']}\n"
            f"Base URL: {S.get('base_url', '') or '(not needed)'}",
            style=TXT,
        ),
        title=Text(" Backend ", style=f"bold {O}"),
        border_style=O,
        box=box.ROUNDED,
        padding=(0, 1),
    ))
    
@cmd("/baseurl", "Set OpenAI-compatible base URL", "config")
def c_baseurl(args):
    if not args:
        console.print(f"  [{O}]Base URL:[/] [{TXT}]{S.get('base_url', '') or '(not set)'}[/]\n")
        return

    S["base_url"] = args[0].rstrip("/")
    save_settings()

    console.print(f"  [{O}]✓ Base URL set to[/] [{TXT}]{S['base_url']}[/]\n")


@cmd("/openai_key", "Set API key for OpenAI-compatible backends", "config")
def c_openai_key(args):
    if not args:
        masked = ("*" * 8 + S["openai_key"][-4:]) if S.get("openai_key") else "(not set)"
        console.print(f"  [{O}]OpenAI-compatible key:[/] [{TXT}]{masked}[/]\n")
        return

    S["openai_key"] = args[0]
    save_settings()

    console.print(f"  [{O}]✓ API key saved[/]\n")


@cmd("/effort", "Set response length: /effort low|medium|high|max", "model")
def c_effort(args):
    MAP = {"low": 1024, "medium": 2048, "high": 4096, "max": 8192}
    if args and args[0].lower() in MAP:
        lvl = args[0].lower()
    else:
        lvl = interactive_picker(list(MAP), title="Select effort level",
                                 current=next((k for k,v in MAP.items() if v==S.get("max_tokens",4096)), "high"))
    if lvl:
        S["max_tokens"] = MAP[lvl]; save_settings()
        console.print(f"\n  [{GRN}]✓ Effort → {lvl} ({MAP[lvl]} tokens)[/]\n")

@cmd("/context", "Show conversation context usage", "context")
def c_context(_):
    msgs  = len(S["history"])
    chars = sum(len(str(m.get("content", ""))) for m in S["history"])
    console.print(f"\n  [{WH}]Context[/]  [{TXT}]{msgs} messages · ~{chars:,} chars "
                  f"· ~{chars//4:,} tokens[/]\n"
                  f"  [{DIM}]Anthropic window: ~200k tokens[/]\n")

@cmd("/compact", "Summarize history to free context", "context")
def c_compact(_):
    if not S["history"]:
        console.print(f"\n  [{YLW}]No history to compact.[/]\n"); return
    console.print(f"\n  [{DIM}]Compacting {len(S['history'])} messages…[/]")
    transcript = "\n".join(
        f"{m['role'].upper()}: {m['content']}"
        for m in S["history"] if isinstance(m.get("content"), str)
    )
    old = S["history"]
    S["history"] = []
    result = ai_respond(
        "Summarize the following conversation in ≤150 words, "
        "preserving key decisions, filenames, and code changes.\n\n" + transcript
    )
    if result:
        S["history"] = [
            {"role": "user",      "content": "[Previous conversation summary]"},
            {"role": "assistant",  "content": result},
        ]
        console.print(f"\n  [{GRN}]✓ Compacted to 2 messages.[/]\n")
    else:
        S["history"] = old

@cmd("/history", "Show conversation history stats", "context")
def c_history(_):
    if not S["history"]:
        console.print(f"\n  [{TXT}]No history yet.[/]\n"); return
    console.print(f"\n  [{TXT}]{len(S['history'])} messages:[/]")
    for m in S["history"][-8:]:
        role    = m["role"]
        snippet = str(m.get("content",""))[:70].replace("\n"," ")
        color   = O if role == "user" else GRN
        console.print(f"  [{color}]{role:12}[/] [{DIM}]{snippet}…[/]")
    console.print()

@cmd("/memory", "Edit CLAUDE.md project instructions", "context")
def c_memory(_):
    p = os.path.join(S["cwd"], "CLAUDE.md")
    if not os.path.exists(p):
        with open(p, "w") as f:
            f.write("# CLAUDE.md\n\n## Project Instructions\n\nAdd context here.\n")
        console.print(f"\n  [{GRN}]✓ Created {p}[/]")
    editor = os.environ.get("EDITOR", "notepad" if os.name == "nt" else "nano")
    os.system(f'{editor} "{p}"')

# ── Config ────────────────────────────────────────────────────────────────────
@cmd("/config", "Show current configuration", "config")
def c_config(_):
    rows = [
        ("Backend",    S["backend"]),
        ("Model",      S["model"]),
        ("Host",       S["host"]),
        ("Port",       str(S["port"])),
        ("API Key",    "set ✓" if S["api_key"] else "not set ✗"),
        ("Auto-allow", "ON"    if S["auto_allow"] else "OFF"),
        ("Max tokens", str(S.get("max_tokens", 4096))),
        ("CWD",        short_path()),
        ("Settings",   str(SETTINGS_FILE)),
        ("History",    f"{len(S['history'])} messages"),
    ]
    t = Table(show_header=False, border_style=BDR, box=box.SIMPLE)
    t.add_column(style=f"bold {O}", width=14, no_wrap=True)
    t.add_column(style=TXT)
    for k, v in rows:
        t.add_row(k, v)
    console.print()
    console.print(t)
    console.print()

@cmd("/status",   "Alias for /config",         "config")
def c_status(a):  c_config(a)

@cmd("/settings", "Show config or /settings open to edit file", "config")
def c_settings(args):
    if args and args[0] == "open":
        editor = os.environ.get("EDITOR", "notepad" if os.name == "nt" else "nano")
        os.system(f'{editor} "{SETTINGS_FILE}"')
        return
    c_config(args)
    console.print(f"  [{DIM}]/settings open — edit {SETTINGS_FILE}[/]\n")

@cmd("/key", "Set Anthropic API key  /key sk-ant-…", "config")
def c_key(args):
    if args:
        S["api_key"] = args[0]; S["backend"] = "anthropic"
        os.environ["ANTHROPIC_API_KEY"] = args[0]
        save_settings()
        console.print(f"\n  [{GRN}]✓ API key set. Backend → anthropic[/]\n")
    else:
        masked = ("*"*8 + S["api_key"][-4:]) if len(S["api_key"]) > 4 else "(not set)"
        console.print(f"\n  [{TXT}]Key: {masked}[/]\n"
                      f"  [{DIM}]Or export ANTHROPIC_API_KEY in your shell.[/]\n"
                      f"  [{DIM}]Anthropic is optional — use /connect for Ollama.[/]\n")

@cmd("/auto", "Toggle auto-allow for all permission prompts", "config")
def c_auto(_):
    S["auto_allow"] = not S["auto_allow"]
    state = f"[{GRN}]ON[/]" if S["auto_allow"] else f"[{RED}]OFF[/]"
    console.print(f"\n  [{WH}]Auto-allow: {state}[/]\n")
    save_settings()

@cmd("/permissions", "Show permission settings", "config")
def c_permissions(_):
    console.print(
        f"\n  [{WH}]Permissions[/]\n"
        f"  Auto-allow: [{'bold ' + GRN if S['auto_allow'] else RED}]"
        f"{'ON' if S['auto_allow'] else 'OFF'}[/]  (toggle: /auto)\n"
        f"  [{TXT}]Tools: run_command  write_file  read_file  list_directory  patch_file[/]\n"
    )

@cmd("/theme", "Change color theme  /theme [default|ocean|mono]", "config")
def c_theme(args):
    global O, DIM, BDR, TXT, GRN, RED, BLU, YLW, PUR
    themes = {
        "default": dict(O="#E8823A",DIM="#666666",BDR="#4A4A4A",TXT="#AAAAAA",
                        GRN="#4EC9B0",RED="#F44747",BLU="#569CD6",YLW="#DCDCAA",PUR="#C586C0"),
        "ocean":   dict(O="#61AFEF",DIM="#5C6370",BDR="#3E4451",TXT="#ABB2BF",
                        GRN="#98C379",RED="#E06C75",BLU="#56B6C2",YLW="#E5C07B",PUR="#C678DD"),
        "mono":    dict(O="#FFFFFF",DIM="#666666",BDR="#444444",TXT="#BBBBBB",
                        GRN="#AAAAAA",RED="#888888",BLU="#CCCCCC",YLW="#DDDDDD",PUR="#999999"),
    }
    chosen = args[0].lower() if (args and args[0].lower() in themes) else None
    if not chosen:
        chosen = interactive_picker(list(themes), current=S.get("theme","default"),
                                    title="Select theme")
    if chosen and chosen in themes:
        for k, v in themes[chosen].items():
            globals()[k] = v
        S["theme"] = chosen; save_settings()
        console.print(f"\n  [{GRN}]✓ Theme → {chosen}[/]\n")

@cmd("/doctor", "Diagnose your Flaude installation", "config")
def c_doctor(_):
    clear(); compact_header()
    console.print(f"\n  [{WH}]Flaude Doctor[/]\n")
    checks = []
    v = sys.version_info
    checks.append(("Python",       f"{v.major}.{v.minor}.{v.micro}", v >= (3,10), "Need 3.10+"))
    try:
        import rich as _r
        checks.append(("rich",       _r.__version__, True, ""))
    except ImportError:
        checks.append(("rich",       "missing", False, "pip install rich"))
    checks.append(("prompt_toolkit","installed" if HAS_PT        else "missing", HAS_PT,        "" if HAS_PT        else "pip install prompt_toolkit"))
    checks.append(("anthropic SDK", "installed" if HAS_ANTHROPIC else "missing", HAS_ANTHROPIC, "" if HAS_ANTHROPIC else "pip install anthropic  (optional)"))
    checks.append(("requests",      "installed" if HAS_REQUESTS  else "missing", HAS_REQUESTS,  "" if HAS_REQUESTS  else "pip install requests  (for Ollama)"))
    has_key = bool(S["api_key"])
    checks.append(("Anthropic key", "set ✓" if has_key else "not set",
                   has_key or S["backend"]=="ollama",
                   "" if has_key else "optional — /key or ANTHROPIC_API_KEY"))
    if HAS_REQUESTS:
        try:
            r = _requests.get(f"http://{S['host']}:{S['port']}/api/tags", timeout=3)
            ms = [m["name"] for m in r.json().get("models", [])]
            checks.append(("Ollama", f"reachable ({len(ms)} models)", True, ""))
        except Exception:
            checks.append(("Ollama", "not reachable", S["backend"]!="ollama", "ollama serve"))
    checks.append(("Settings file", str(SETTINGS_FILE), SETTINGS_FILE.exists(), ""))

    for name, value, ok, hint in checks:
        icon  = f"[{GRN}]✓[/]" if ok else f"[{RED}]✗[/]"
        color = GRN if ok else RED
        line  = f"  {icon}  [{color}]{name:18}[/]  [{TXT}]{value}[/]"
        if hint: line += f"  [{DIM}]→ {hint}[/]"
        console.print(line)
    console.print()

@cmd("/version", "Show version", "config")
def c_version(_):
    console.print(f"\n  [{WH}]Flaude Code[/] [{DIM}]v{S['version']}[/]  "
                  f"[{TXT}]Python {sys.version.split()[0]} · {sys.platform}[/]\n")

@cmd("/cost", "Estimate token usage this session", "config")
def c_cost(_):
    chars = sum(len(str(m.get("content",""))) for m in S["history"])
    tok   = chars // 4
    console.print(f"\n  [{WH}]Usage estimate[/]  [{TXT}]~{tok:,} tokens · ~${tok*3/1_000_000:.4f} input[/]\n"
                  f"  [{DIM}]Actual cost depends on model and output tokens.[/]\n")

# ── Files ──────────────────────────────────────────────────────────────────────
@cmd("/cd",  "Change directory   /cd ~/projects",    "files")
def c_cd(args):
    if not args:
        console.print(f"\n  [{TXT}]{S['cwd']}[/]\n"); return
    target = abs_path(" ".join(args))
    if os.path.isdir(target):
        S["cwd"] = target; os.chdir(target)
        console.print(f"\n  [{GRN}]→ {target}[/]\n")
    else:
        console.print(f"\n  [{RED}]✗ Not a directory: {target}[/]\n")

@cmd("/pwd",  "Print working directory",             "files")
def c_pwd(_): console.print(f"\n  [{BLU}]{S['cwd']}[/]\n")

@cmd("/ls",  "List directory  /ls [path]",           "files")
def c_ls(args):
    path = abs_path(args[0]) if args else S["cwd"]
    console.print(f"\n[{TXT}]{escape(tool_list_dir(path))}[/]\n")

@cmd("/run",  "Run a shell command  /run ls -la",    "files")
def c_run(args):
    if not args:
        console.print(f"\n  [{RED}]Usage: /run <command>[/]\n"); return
    console.print(f"\n[{TXT}]{escape(tool_run_command(' '.join(args), 'user command'))}[/]\n")

@cmd("/read", "Read a file  /read main.py",          "files")
def c_read(args):
    if not args:
        console.print(f"\n  [{RED}]Usage: /read <file>[/]\n"); return
    console.print(f"\n[{GRN}]{escape(tool_read_file(args[0]))}[/]\n")

@cmd("/diff", "Git diff  /diff [args]",              "files")
def c_diff(args):
    console.print(f"\n[{TXT}]{escape(tool_run_command('git diff '+' '.join(args), 'diff'))}[/]\n")

@cmd("/init", "Create FLAUDE.md in current directory", "files")
def c_init(_):
    p = os.path.join(S["cwd"], "FLAUDE.md")
    if not os.path.exists(p):
        tool_write_file(p, "# FLAUDE.md\n\n## Project Instructions\n\nAdd context here.\n", "init")
    else:
        console.print(f"\n  [{O}]Already exists: {p}[/]\n")

@cmd("/plan", "Toggle plan mode (AI explains before acting)", "files")
def c_plan(_):
    S["plan_mode"] = not S.get("plan_mode", False)
    state = f"[{GRN}]ON[/]" if S["plan_mode"] else f"[{RED}]OFF[/]"
    console.print(f"\n  [{WH}]Plan mode: {state}[/]\n")

@cmd("/connect", "Connect to Local  /connect localhost:11434", "ollama")
def c_connect(args):
    if not args:
        console.print(f"\n  [{TXT}]Usage: /connect host:port[/]\n"); return
    parts = args[0].split(":")
    S["host"] = parts[0]; S["port"] = int(parts[1]) if len(parts) > 1 else 11434
    S["backend"] = "ollama"
    try:
        r      = _requests.get(f"http://{S['host']}:{S['port']}/api/tags", timeout=5)
        models = [m["name"] for m in r.json().get("models", [])]
        console.print(f"\n  [{GRN}]✓ Connected to Ollama {S['host']}:{S['port']}[/]")
        if models:
            console.print(f"  [{TXT}]Models: {', '.join(models[:8])}[/]")
            if S["model"] not in models:
                S["model"] = models[0]
                console.print(f"  [{O}]→ Auto-switched to {models[0]}[/]")
        console.print()
        save_settings()
    except Exception as e:
        console.print(f"\n  [{RED}]✗ Cannot connect: {e}[/]\n"
                      f"  [{DIM}]Is Ollama running?  Try: ollama serve[/]\n")

@cmd("/host", "Set Ollama host  /host 192.168.1.10", "ollama")
def c_host(args):
    if args:
        S["host"] = args[0]; S["backend"] = "ollama"; save_settings()
        console.print(f"\n  [{GRN}]✓ Host → {args[0]}[/]\n")
    else:
        console.print(f"\n  [{TXT}]Host: {S['host']}[/]\n")
        
@cmd("/live", "Toggle live output", "config")
def c_live(_):
    S["live"] = not S.get("live", False)
    save_settings()

    draw_full_ui()

    state = "ON" if S["live"] else "OFF"
    color = GRN if S["live"] else RED

    console.print(Panel(
        Text(f"Live output is now {state}", style=TXT),
        title=Text(" Live ", style=f"bold {color}"),
        border_style=color,
        box=box.ROUNDED,
        padding=(0, 1),
    ))

@cmd("/port", "Set Ollama port  /port 11434", "ollama")
def c_port(args):
    if args:
        try:
            S["port"] = int(args[0]); S["backend"] = "ollama"; save_settings()
            console.print(f"\n  [{GRN}]✓ Port → {args[0]}[/]\n")
        except ValueError:
            console.print(f"\n  [{RED}]Invalid port.[/]\n")
    else:
        console.print(f"\n  [{TXT}]Port: {S['port']}[/]\n")
        
        

class FlatCompleter(Completer):
    def get_completions(self, doc, complete_event):
        txt = doc.text_before_cursor
        if txt == "/" or (txt.startswith("/") and " " not in txt):
            for name in sorted(CMDS.keys()):
                if name.startswith(txt):
                    yield Completion(name[len(txt):], display_meta=CMD_HELP.get(name,""),
                                     display=name)
        elif " " in txt:
            parts = txt.split()
            partial = parts[-1] if not txt.endswith(" ") else ""
            base    = abs_path(partial) if partial else S["cwd"]
            if partial and not partial.endswith(("/", "\\")):
                dir_part, prefix = os.path.dirname(base), os.path.basename(base)
            else:
                dir_part, prefix = base, ""
            try:
                for item in sorted(os.listdir(dir_part)):
                    if item.startswith(prefix):
                        suf = "/" if os.path.isdir(os.path.join(dir_part, item)) else ""
                        yield Completion(item[len(prefix):]+suf, display=item+suf)
            except Exception:
                pass

def process(raw: str):
    raw = raw.strip()
    if not raw:
        return

    if raw.startswith("/"):
        parts = raw.split()
        name = parts[0].lower()
        handler = CMDS.get(name)

        if handler:
            handler(parts[1:])
        else:
            console.print(f"\n  [{RED}]Unknown command: {name}[/]  Type /help\n")

    else:
        line_count = len(raw.splitlines())

        looks_pasted = (
            line_count > 1
            or len(raw) > 55
            or ":\\" in raw
            or "\\Users\\" in raw
            or raw.count("\\") >= 2
        )

        if looks_pasted:
            shown = f"[Pasted {line_count} line{'s' if line_count != 1 else ''}]"
        else:
            shown = raw

        console.print()
        console.print(Panel(
            Text(shown, style=TXT),
            title=Text(" You ", style=f"bold {O}"),
            border_style=O,
            box=box.ROUNDED,
            padding=(0, 1),
        ))

        sep()
        console.print()
        ai_respond(raw)
        console.print()

def main():
    draw_full_ui()

    history   = InMemoryHistory() if HAS_PT else None
    completer = FlatCompleter()   if HAS_PT else None
    pt_style  = PTStyle.from_dict({"prompt": f"bold fg:{O}"}) if HAS_PT else None

    while True:
        try:
            print_footer()

            if HAS_PT:
                raw = pt_prompt(
                    HTML(f'<b><style fg="{O}">&gt; </style></b>'),
                    style=pt_style,
                    completer=completer,
                    complete_while_typing=True,
                    history=history,
                )
            else:
                console.print("> ", style=f"bold {O}", end="")
                raw = input()

            erase_prompt_line()
            process(raw)

        except (KeyboardInterrupt, EOFError):
            console.print(f"\n\n  [{DIM}]Ctrl+C — use /exit to quit.[/]\n")

if __name__ == "__main__":
    main()