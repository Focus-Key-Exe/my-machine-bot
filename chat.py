
#!/usr/bin/env python3
"""
My Machine Bot - A local chatbot that knows about your system.
Uses Ollama for LLM and has access to system monitoring tools.
"""

import json
import ollama
from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt
from system_tools import TOOLS

console = Console()

# The model to use - llama3.2 is good for tool use, but you can change this
MODEL = "llama3.2"

# System prompt that tells the bot what tools it has
SYSTEM_PROMPT = """You are a helpful assistant that runs locally on the user's machine. 
You have access to tools that can retrieve information about the system you're running on.

Available tools:
{tools}

When the user asks about system information, use the appropriate tool by responding with:
[TOOL: tool_name]

For example:
- If asked about CPU usage, respond with [TOOL: get_cpu_info]
- If asked about memory/RAM, respond with [TOOL: get_memory_info]
- If asked about disk space, respond with [TOOL: get_disk_info]
- If asked about network, respond with [TOOL: get_network_info]
- If asked about running processes, respond with [TOOL: get_process_info]
- If asked about battery, respond with [TOOL: get_battery_info]
- If asked about uptime or boot time, respond with [TOOL: get_uptime]
- If asked about general system info (OS, hostname), respond with [TOOL: get_system_info]

After receiving tool results, explain them to the user in a friendly, clear way.
You can use multiple tools if needed to answer complex questions.
"""


def format_tool_descriptions() -> str:
    """Format tool descriptions for the system prompt."""
    lines = []
    for name, info in TOOLS.items():
        lines.append(f"- {name}: {info['description']}")
    return "\n".join(lines)


def extract_tool_calls(response: str) -> list[str]:
    """Extract tool calls from the response."""
    import re
    pattern = r'\[TOOL:\s*(\w+)\]'
    return re.findall(pattern, response)


def execute_tool(tool_name: str) -> str:
    """Execute a tool and return the result."""
    if tool_name in TOOLS:
        try:
            result = TOOLS[tool_name]["function"]()
            return json.dumps(result, indent=2)
        except Exception as e:
            return f"Error executing {tool_name}: {str(e)}"
    return f"Unknown tool: {tool_name}"


def chat(user_message: str, history: list) -> str:
    """Send a message and get a response, handling tool calls."""
    
    # Add user message to history
    history.append({"role": "user", "content": user_message})
    
    # Get initial response
    response = ollama.chat(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT.format(tools=format_tool_descriptions())},
            *history
        ]
    )
    
    assistant_message = response["message"]["content"]
    
    # Check for tool calls
    tool_calls = extract_tool_calls(assistant_message)
    
    if tool_calls:
        # Execute tools and gather results
        tool_results = []
        for tool_name in tool_calls:
            console.print(f"[dim]🔧 Running {tool_name}...[/dim]")
            result = execute_tool(tool_name)
            tool_results.append(f"Results from {tool_name}:\n{result}")
        
        # Add tool results to context and get final response
        tool_context = "\n\n".join(tool_results)
        history.append({"role": "assistant", "content": assistant_message})
        history.append({"role": "user", "content": f"Here are the tool results:\n\n{tool_context}\n\nPlease explain these results to me in a friendly, easy-to-understand way."})
        
        final_response = ollama.chat(
            model=MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT.format(tools=format_tool_descriptions())},
                *history
            ]
        )
        
        assistant_message = final_response["message"]["content"]
    
    history.append({"role": "assistant", "content": assistant_message})
    return assistant_message


def main():
    """Main chat loop."""
    console.print(Panel.fit(
        "[bold blue]🤖 My Machine Bot[/bold blue]\n"
        "[dim]A local AI assistant that knows about your system[/dim]\n\n"
        "Ask me about your CPU, memory, disk, network, processes, and more!\n"
        "Type [bold]'quit'[/bold] or [bold]'exit'[/bold] to leave.",
        border_style="blue"
    ))
    
    # Check if model is available
    try:
        models = ollama.list()
        model_names = [m["name"].split(":")[0] for m in models.get("models", [])]
        if MODEL not in model_names and f"{MODEL}:latest" not in [m["name"] for m in models.get("models", [])]:
            console.print(f"\n[yellow]⚠️  Model '{MODEL}' not found. Pulling it now...[/yellow]")
            console.print("[dim]This may take a few minutes on first run.[/dim]\n")
            ollama.pull(MODEL)
            console.print(f"[green]✓ Model '{MODEL}' ready![/green]\n")
    except Exception as e:
        console.print(f"\n[red]❌ Error connecting to Ollama: {e}[/red]")
        console.print("[yellow]Make sure Ollama is running: brew services start ollama[/yellow]")
        return
    
    history = []
    
    while True:
        try:
            user_input = Prompt.ask("\n[bold green]You[/bold green]")
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                console.print("\n[blue]👋 Goodbye![/blue]")
                break
            
            if not user_input.strip():
                continue
            
            with console.status("[bold blue]Thinking...[/bold blue]"):
                response = chat(user_input, history)
            
            console.print("\n[bold blue]Bot[/bold blue]")
            console.print(Markdown(response))
            
        except KeyboardInterrupt:
            console.print("\n\n[blue]👋 Goodbye![/blue]")
            break
        except Exception as e:
            console.print(f"\n[red]Error: {e}[/red]")


if __name__ == "__main__":
    main()
