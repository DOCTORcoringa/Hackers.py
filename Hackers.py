import os
import socket
import psutil
import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.align import Align
from rich.text import Text

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def type_message(message, delay=0.01, max_line_length=70):
    words = message.split()
    line = ""
    for word in words:
        if len(line) + len(word) + 1 > max_line_length:
            console.print(line, style="bold green")
            line = ""
            Prompt.ask("[bold green]Pressione ENTER para continuar[/bold green]", default="", show_default=False)
        line += (word + " ")
        time.sleep(delay)
    if line.strip():
        console.print(line.strip(), style="bold green")
        Prompt.ask("[bold green]Pressione ENTER para continuar[/bold green]", default="", show_default=False)

def system_info():
    hostname = socket.gethostname()
    try:
        ip_address = socket.gethostbyname(hostname)
    except:
        ip_address = 'N/A'
    cpu_percent = psutil.cpu_percent(interval=1)
    mem = psutil.virtual_memory()
    mem_used = mem.used / (1024 ** 2)
    mem_total = mem.total / (1024 ** 2)
    return (hostname, ip_address, cpu_percent, mem_used, mem_total)

def show_banner():
    banner_lines = [
        "██████╗ ██████╗  ██████╗ ███╗   ██╗██████╗ ██╗ █████╗ ██████╗ ███████╗",
        "██╔══██╗██╔══██╗██╔═══██╗████╗  ██║██╔══██╗██║██╔══██╗██╔══██╗██╔════╝",
        "██████╔╝██████╔╝██║   ██║██╔██╗ ██║██████╔╝██║███████║██████╔╝█████╗  ",
        "██╔═══╝ ██╔══██╗██║   ██║██║╚██╗██║██╔═══╝ ██║██╔══██║██╔══██╗██╔══╝  ",
        "██║     ██║  ██║╚██████╔╝██║ ╚████║██║     ██║██║  ██║██║  ██║███████╗",
        "╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝",
    ]
    banner_text = Text()
    colors = ["magenta", "red"]
    for idx, line in enumerate(banner_lines):
        color = colors[idx % 2]
        banner_text.append(line + "\n", style=f"bold {color}")
    slogan = Text(
        "\n[ Doctor Coringa Lunático ]\n"
        "[ Sistema para Fins Educacionais - Estude, Aprenda e Respeite a Ética ]\n",
        style="bold magenta"
    )
    banner_panel = Panel(Align.center(banner_text + slogan), border_style="magenta", padding=(1,2))
    console.print(banner_panel)

def main_menu():
    while True:
        clear_screen()
        show_banner()

        hostname, ip, cpu, mem_used, mem_total = system_info()
        status_text = (f"[bold cyan]Host:[/bold cyan] {hostname}   "
                       f"[bold cyan]IP Local:[/bold cyan] {ip}   "
                       f"[bold cyan]CPU:[/bold cyan] {cpu}%   "
                       f"[bold cyan]Memória:[/bold cyan] {mem_used:.1f}MB / {mem_total:.1f}MB")
        console.print(Panel(status_text, border_style="cyan", padding=(0,2)))

        menu = (
            "┌───────────────────────────────────────────┐\n"
            "│ { 1 } Consulta de DDD                      │\n"
            "│ { 2 } Consulta de CNPJ                     │\n"
            "│ { 3 } Consulta de CEP                      │\n"
            "│ { 4 } Consulta de IP                       │\n"
            "│ { 5 } Consulta Bancária                    │\n"
            "│ { 6 } Covid-19                            │\n"
            "│ { 7 } Consulta de Placa                    │\n"
            "│ { 8 } Consulta de BIN                      │\n"
            "│ { 9 } Consulta de CPF                      │\n"
            "│ {10 } Consulta de Nome                     │\n"
            "├───────────────────────────────────────────┤\n"
            "│ {99 } APIs                               │\n"
            "│ {98 } Redes Sociais                      │\n"
            "│ {00 } Sair                              │\n"
            "└───────────────────────────────────────────┘"
        )

        console.print(Panel(menu, title="[bold magenta]Menu Principal[/bold magenta]", border_style="magenta", padding=(1,2)))
        choice = Prompt.ask("[bold magenta]Escolha uma opção[/bold magenta]").strip()

        if choice == "00":
            console.print("[bold red]Saindo do sistema... Até logo![/bold red]")
            break
        else:
            console.print(f"[bold green]Você escolheu a opção {choice} - Funcionalidade ainda não implementada.[/bold green]")
            Prompt.ask("[bold green]Pressione ENTER para voltar[/bold green]", default="", show_default=False)

if __name__ == "__main__":
    main_menu()
