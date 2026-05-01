# 🤖 Flaude Code

Flaude Code is an AI-powered coding assistant that helps you build features, fix bugs, and automate development tasks — directly from your terminal.

I built Flaude because many other “free Claude Code” alternatives felt too complicated, unstable, or difficult to set up. Flaude aims to be simpler, cleaner, and easier to use.

---

## 📸 Showcase

![Flaude Showcase](https://github.com/Kynix09/Flaude/blob/77be6513b94d1987cf55537c48b2b5148ed78613/Images/Showcase_1.png)

---

## ✨ Features

- 🧠 AI-powered coding assistant
- 📁 Create, edit, and manage files & folders
- ⚡ Run shell commands safely with permission prompts
- 🔍 Read and analyze files instantly
- 🛠 Multi-step task execution (chain actions automatically)
- 🎛 Live output + thinking animation
- 🔐 Permission system (Allow / Deny / Auto-allow)
- 🎨 Clean Claude-style terminal UI
- 🧩 Works with multiple models and providers
- 🌐 Supports Ollama, Anthropic, OpenRouter, NVIDIA NIM, LM Studio, llama.cpp, DeepSeek, Groq, Together, and more
- ⚙️ Persistent settings saved automatically
- 🧪 Experimental developer workflow assistant

---

## ⚠️ Safety Notice

Flaude can run shell commands and modify files on your computer.

Always review permission prompts carefully before allowing actions.  
Use Auto-allow only if you fully trust the current task and model.

This project is experimental software. Use it at your own risk.

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Kynix09/Flaude.git
cd Flaude
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

If you don’t have a requirements file yet:

```bash
pip install requests rich prompt_toolkit rainbowtext anthropic
```

### 3. Start Flaude

```bash
python flaude.py
```

---

## ⚙️ Configuration

Flaude settings are stored here:

```text
C:\Users\<your-user>\.flaude\settings.flaude
```

You can change settings via commands:

```text
/model        # choose model
/max 4096     # set max tokens
/live         # toggle live output
/auto         # toggle auto-allow
/backend      # choose backend
/connect      # change Ollama host/port
/baseurl      # set OpenAI-compatible base URL
/key          # set Anthropic API key
/openai_key   # set OpenAI-compatible API key
```

---

## 🔑 API Keys

Flaude has two API key commands:

```text
/key YOUR_ANTHROPIC_KEY
```

Use `/key` for Anthropic / Claude models.

```text
/openai_key YOUR_PROVIDER_KEY
```

Use `/openai_key` for OpenAI-compatible backends.

OpenAI-compatible does **not** mean OpenAI only. It means the provider uses an OpenAI-style API format.

---

## 🧠 Supported Backends

Flaude supports local and API-based models.

- 🦙 Ollama
- 🧠 Anthropic
- 🌐 OpenRouter
- 🚀 NVIDIA NIM
- 🖥 LM Studio
- 🧩 llama.cpp server
- 🔎 DeepSeek
- ⚡ Groq
- 🌍 Together AI
- 🔌 Other OpenAI-compatible APIs

---

<details>
<summary>🦙 Ollama Setup</summary>

Ollama runs models locally on your computer.

### 1. Start Ollama

```bash
ollama serve
```

### 2. Pull a model

```bash
ollama pull llama3.1
```

or:

```bash
ollama pull qwen2.5-coder
```

### 3. Configure Flaude

```text
/backend ollama
/connect localhost:11434
/model llama3.1
```

If your Ollama model has a different name, use that model name:

```text
/model qwen2.5-coder
```

</details>

---

<details>
<summary>🧠 Anthropic / Claude Setup</summary>

Use Anthropic if you want Claude models.

```text
/backend anthropic
/key YOUR_ANTHROPIC_KEY
/model claude-sonnet-4-5
```

Example:

```text
/backend anthropic
/key sk-ant-...
/model claude-sonnet-4-5
```

</details>

---

<details>
<summary>🌐 OpenRouter Setup</summary>

OpenRouter lets you use many different models through one API.

```text
/backend openrouter
/openai_key YOUR_OPENROUTER_KEY
/model openai/gpt-4o-mini
```

Other model examples:

```text
/model anthropic/claude-3.5-sonnet
/model google/gemini-2.0-flash-001
/model meta-llama/llama-3.1-8b-instruct
```

</details>

---

<details>
<summary>🚀 NVIDIA NIM Setup</summary>

NVIDIA NIM uses an OpenAI-compatible API format.

```text
/backend nvidia_nim
/openai_key YOUR_NVIDIA_NIM_KEY
/model meta/llama-3.1-70b-instruct
```

</details>

---

<details>
<summary>🔎 DeepSeek Setup</summary>

DeepSeek uses an OpenAI-compatible API format.

```text
/backend deepseek
/openai_key YOUR_DEEPSEEK_KEY
/model deepseek-chat
```

</details>

---

<details>
<summary>⚡ Groq Setup</summary>

Groq uses an OpenAI-compatible API format.

```text
/backend groq
/openai_key YOUR_GROQ_KEY
/model llama-3.1-8b-instant
```

</details>

---

<details>
<summary>🌍 Together AI Setup</summary>

Together AI uses an OpenAI-compatible API format.

```text
/backend together
/openai_key YOUR_TOGETHER_KEY
/model meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo
```

</details>

---

<details>
<summary>🖥 LM Studio Setup</summary>

LM Studio runs local models on your computer and exposes an OpenAI-compatible local server.

Start the LM Studio local server.

Default base URL is usually:

```text
http://localhost:1234/v1
```

Then configure Flaude:

```text
/backend lmstudio
/baseurl http://localhost:1234/v1
/model local-model
```

No API key is usually required.

</details>

---

<details>
<summary>🧩 llama.cpp Server Setup</summary>

llama.cpp can expose an OpenAI-compatible local server.

Example:

```bash
llama-server -m model.gguf --port 8080
```

Default base URL:

```text
http://localhost:8080/v1
```

Then configure Flaude:

```text
/backend llamacpp
/baseurl http://localhost:8080/v1
/model local-model
```

No API key is usually required.

</details>

---

<details>
<summary>🔌 Custom OpenAI-Compatible API Setup</summary>

You can connect Flaude to any OpenAI-compatible API.

```text
/backend openrouter
/baseurl YOUR_BASE_URL
/openai_key YOUR_API_KEY
/model YOUR_MODEL_NAME
```

Example:

```text
/baseurl https://api.example.com/v1
/openai_key YOUR_API_KEY
/model provider/model-name
```

If the provider does not need an API key, you can skip `/openai_key`.

</details>

---

## 🛠 Example Commands

```text
Create a folder on my desktop
Fix this Python error
Make a calculator script
Read this file and explain it
Delete this file
Rename this folder
Create a Python project for me
```

---

## 🔐 Permission System

Flaude will ask before executing actions:

```text
Allow
Deny
Allow All
```

You stay in control of your system at all times.

Auto-allow can be toggled with:

```text
/auto
```

---

## 🧪 Live Output

Enable live output with:

```text
/live
```

Live mode shows model output while it is being generated.

---

## 📁 Project Structure

```text
Flaude/
├── flaude.py
├── Images/
├── README.md
├── LICENSE
└── settings (auto-created)
```

---

## 💡 Roadmap

- [ ] Plugin system
- [ ] GUI version
- [ ] Better multi-model routing
- [ ] File diff viewer
- [ ] Voice input
- [ ] Better tool execution logs
- [ ] More backend integrations
- [ ] Safer sandbox mode

---

## 🤝 Contributing

Pull requests are welcome!

If you have ideas, improvements, bug fixes, or backend integrations — feel free to contribute.

Before opening a pull request:

```text
1. Keep the code readable
2. Do not commit API keys or personal settings
3. Test your changes
4. Explain what your change does
```

---

## 📜 License

Flaude Code is licensed under the MIT License.

You are free to use, modify, and share it, but please keep the copyright notice:

```text
Copyright (c) 2026 Kynix09
```

See the `LICENSE` file for details.

---

## ❤️ Acknowledgements

Inspired by tools like Claude Code and modern AI developer workflows.

---

## ⭐ Support

If you like this project:

⭐ Star the repo  
🍴 Fork it  
🧠 Build something awesome  

---

*Flaude Code was built by a real human. But a lot of bugs were fixed with the help of AI.  
This README was also written by AI… because the developer was feeling a bit lazy.
(And you can't say something, if you’re reading this, you’re literally using or looking to find an AI tool right now.)*

> Flaude Code — Your AI developer companion in the terminal.
