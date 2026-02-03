
# 🤖 My Machine Bot

A local AI chatbot powered by [Ollama](https://ollama.com) that can tell you about your system. Everything runs locally on your machine - no data is sent to the cloud.

## Features

- 💬 Chat with a local LLM (Llama 3.2)
- 💻 Get real-time system information:
  - CPU usage and specs
  - Memory (RAM) usage
  - Disk space and partitions
  - Network interfaces and stats
  - Running processes
  - Battery status (laptops)
  - System uptime
- 🔒 100% local - your data never leaves your machine
- 🎨 Beautiful terminal UI with Rich

## Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/download) installed and running

## Installation

1. **Install Ollama** (if not already installed):
   ```bash
   brew install ollama
   ```

2. **Start Ollama service**:
   ```bash
   brew services start ollama
   ```

3. **Clone this repository**:
   ```bash
   git clone https://github.com/Focus-Key-Exe/my-machine-bot.git
   cd my-machine-bot
   ```

4. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```

5. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the chatbot:

```bash
python chat.py
```

On first run, it will automatically download the Llama 3.2 model (~2GB).

### Example Questions

- "How much RAM am I using?"
- "What's my CPU usage right now?"
- "Show me my disk space"
- "What processes are using the most memory?"
- "What's my IP address?"
- "How long has my computer been running?"
- "Tell me about my system"

## Changing the Model

You can use a different Ollama model by editing the `MODEL` variable in `chat.py`:

```python
MODEL = "llama3.2"  # Change to any model you have
```

Popular alternatives:
- `mistral` - Fast and capable
- `llama3.2:1b` - Smaller/faster variant
- `codellama` - Better for code-related questions

## Project Structure

```
my-machine-bot/
├── chat.py           # Main chatbot application
├── system_tools.py   # System monitoring functions
├── requirements.txt  # Python dependencies
├── .gitignore
└── README.md
```

## Adding New Tools

You can add new system tools by:

1. Creating a new function in `system_tools.py`
2. Adding it to the `TOOLS` dictionary
3. The bot will automatically be able to use it!

## License

MIT License - feel free to use and modify as you like!

## Contributing

Contributions welcome! Feel free to open issues or pull requests.
