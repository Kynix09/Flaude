# 🤖 Flaude Code

Flaude Code is an AI-powered coding assistant that helps you build features, fix bugs, and automate development tasks — directly from your terminal.

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
- 🧩 Works with multiple models (Ollama + APIs)

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
pip install requests rich prompt_toolkit rainbowtext
```

### 3. Start Flaude

```bash
python flaude.py
```

---

## ⚙️ Configuration

Flaude settings are stored here:

```
C:\Users\<your-user>\.flaude\settings.flaude
```

You can change settings via commands:

```bash
/model        # choose model
/max 4096     # set max tokens
/live         # toggle live output
/auto         # toggle auto-allow
/connect      # change backend/host
```

---

## 🧠 Supported Backends

- 🦙 Ollama (local models)
- 🌐 API-based models (Anthropic, OpenAI, etc.)

---

## 🛠 Example Commands

```
Create a folder on my desktop
Fix this Python error
Make a calculator script
Read this file and explain it
```

---

## 🔐 Permission System

Flaude will ask before executing actions:

```
Allow
Deny
Allow All
```

You stay in control of your system at all times.

---

## 📁 Project Structure

```
Flaude/
├── flaude.py
├── Images/
├── README.md
└── settings (auto-created)
```

---

## 💡 Roadmap

- [ ] Plugin system
- [ ] GUI version
- [ ] Better multi-model routing
- [ ] File diff viewer
- [ ] Voice input

---

## 🤝 Contributing

Pull requests are welcome!

If you have ideas, improvements, or bug fixes — feel free to contribute.

---

## 📜 License

This project is licensed under the MIT License.

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
