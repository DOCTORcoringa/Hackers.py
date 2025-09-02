import os
import sys
import socket
import subprocess
import threading
import psutil
import time
import requests
import http.client
from urllib.parse import urlparse
from queue import Queue

from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.align import Align
from rich.table import Table

console = Console()

def type_message(message, delay=0.01, max_line_length=70):
    words = message.split()
    line = ""
    for word in words:
        if len(line) + len(word) + 1 > max_line_length:
            console.print(line, style="green")
            line = ""
            Prompt.ask("[green]Pressione ENTER para continuar[/green]", default="", show_default=False)
        line += (word + " ")
        time.sleep(delay)
    if line.strip():
        console.print(line.strip(), style="green")
        Prompt.ask("[green]Pressione ENTER para continuar[/green]", default="", show_default=False)

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def pause():
    Prompt.ask("[green]Pressione ENTER para voltar ao menu[/green]", default="", show_default=False)

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
    return hostname, ip_address, cpu_percent, mem_used, mem_total

def ping(host):
    param = '-n' if os.name == 'nt' else '-c'
    command = ['ping', param, '1', host]
    try:
        result = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return result.returncode == 0
    except Exception:
        return False

def ping_sweep(base_ip):
    type_message("Iniciando Ping Sweep - identificando hosts ativos na rede local /24...")
    responsive_hosts = []
    def ping_ip(ip):
        if ping(ip):
            console.print(f"[green][ATIVO][/green] {ip}")
            responsive_hosts.append(ip)
    threads = []
    for i in range(1, 255):
        ip = f"{base_ip}.{i}"
        t = threading.Thread(target=ping_ip, args=(ip,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    type_message(f"Hosts ativos encontrados: {len(responsive_hosts)}")
    pause()

def port_scan(target, ports):
    type_message(f"Iniciando escaneamento de portas TCP em {target}...")
    open_ports = []
    def scan_port(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.8)
            try:
                if s.connect_ex((target, port)) == 0:
                    console.print(f"[green][ABERTO][/green] Porta {port}")
                    open_ports.append(port)
            except:
                pass
    threads = []
    for port in ports:
        t = threading.Thread(target=scan_port, args=(port,))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    type_message(f"Escaneamento finalizado. Portas abertas: {open_ports}")
    pause()

def dns_lookup():
    domain = Prompt.ask("Digite o domínio para consulta DNS").strip()
    type_message(f"Consultando DNS para o domínio: {domain} ...")
    try:
        ip = socket.gethostbyname(domain)
        type_message(f"Endereço IPv4 encontrado: {ip}")
    except Exception as e:
        type_message(f"Erro na consulta DNS: {e}")
    pause()

def show_processes():
    type_message("Listando os 10 processos com maior uso de CPU no momento:")
    procs = [(p.info['pid'], p.info['name'], p.info['cpu_percent']) 
             for p in psutil.process_iter(['name', 'cpu_percent'])]
    procs = sorted(procs, key=lambda x: x[2], reverse=True)[:10]
    console.print(f"{'PID':>6}  {'CPU %':>6}  Processo", style="green bold")
    for pid, name, cpu in procs:
        console.print(f"{pid:6}  {cpu:6}%  {name}", style="green")
    pause()

def network_info():
    addrs = psutil.net_if_addrs()
    stats = psutil.net_if_stats()
    type_message("Exibindo interfaces de rede e seus status:")
    for iface, snic_list in addrs.items():
        console.print(f"\nInterface: [bold green]{iface}[/bold green]")
        for snic in snic_list:
            console.print(f"  - Endereço: {snic.address} Tipo: {snic.family}")
        status = "Ativo" if stats[iface].isup else "Inativo"
        console.print(f"  Status: {status}")
    pause()

def geoip_lookup():
    ip = Prompt.ask("Digite o IP para GeoIP Lookup").strip()
    type_message(f"Consultando localização geográfica aproximada para o IP: {ip} ...")
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()
        if data["status"] == "success":
            type_message(f"País: {data['country']}, Região: {data['regionName']}, Cidade: {data['city']}")
            type_message(f"Latitude: {data['lat']}, Longitude: {data['lon']}")
            type_message(f"ISP: {data['isp']}")
        else:
            type_message("Não foi possível obter dados para esse IP.")
    except Exception as e:
        type_message(f"Erro na consulta GeoIP: {e}")
    pause()

def http_enum():
    url = Prompt.ask("Digite a URL para enumeração HTTP (ex: http://exemplo.com)").strip()
    type_message(f"Iniciando requisição HTTP para: {url}")
    try:
        parsed = urlparse(url)
        conn = http.client.HTTPConnection(parsed.netloc, timeout=5)
        conn.request("GET", parsed.path or "/")
        res = conn.getresponse()
        title = ""
        if res.status == 200:
            data = res.read().decode(errors='ignore')
            import re
            title_search = re.search(r"<title>(.*?)</title>", data, re.IGNORECASE)
            if title_search:
                title = title_search.group(1)
            type_message(f"Status HTTP: {res.status} {res.reason}")
            type_message(f"Título da página: {title or '(não encontrado)'}")
            type_message("Alguns headers HTTP relevantes:")
            for h in ['server', 'date', 'content-type', 'last-modified']:
                if h in res.headers:
                    type_message(f"  {h}: {res.headers[h]}")
        else:
            type_message(f"Resposta HTTP: {res.status} {res.reason}")
        conn.close()
    except Exception as e:
        type_message(f"Erro ao conectar ou analisar a URL: {e}")
    pause()

def simple_brute_force():
    type_message("=== Brute Force funcional educativo (exemplo local, apenas aprendizado) ===")
    user = Prompt.ask("Usuário alvo (exemplo local)").strip()
    wordlist = Prompt.ask("Arquivo de senhas (wordlist)").strip()

    try:
        with open(wordlist, 'r') as f:
            passwords = [line.strip() for line in f if line.strip()]
    except Exception as e:
        type_message(f"Erro ao abrir arquivo wordlist: {e}")
        pause()
        return

    type_message(f"Iniciando brute force em {user} com {len(passwords)} senhas.")
    for pw in passwords:
        console.print(f"[green]Tentando senha:[/green] {pw}")
        time.sleep(0.3)
        if pw == "senha123":  # Demonstração da senha correta
            type_message(f"Senha CRACKED! Usuário: {user} Senha: {pw}")
            break
    else:
        type_message("Nenhuma senha da lista acertou.")
    pause()

def show_about():
    about_msg = """
[bold green]██████╗ ██████╗  ██████╗ ███╗   ██╗██████╗ ██╗ █████╗ ██████╗ ███████╗[/bold green]
[bold green]██╔══██╗██╔══██╗██╔═══██╗████╗  ██║██╔══██╗██║██╔══██╗██╔══██╗██╔════╝[/bold green]
[bold green]██████╔╝██████╔╝██║   ██║██╔██╗ ██║██████╔╝██║███████║██████╔╝█████╗  [/bold green]
[bold green]██╔═══╝ ██╔══██╗██║   ██║██║╚██╗██║██╔═══╝ ██║██╔══██║██╔══██╗██╔══╝  [/bold green]
[bold green]██║     ██║  ██║╚██████╔╝██║ ╚████║██║     ██║██║  ██║██║  ██║███████╗[/bold green]
[bold green]╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝[/bold green]

[green]Painel desenvolvido por Doctor Coringa Lunático
Uso exclusivo para fins educacionais e aprendizado seguro
Divirta-se explorando conceitos de segurança e hacking ético![/green]
"""
    console.print(Panel(Align.center(about_msg), border_style="green"))
    pause()

def main_menu():
    while True:
        clear_screen()
        hostname, ip, cpu, mem_used, mem_total = system_info()
        banner = (
            "[bold magenta]██████╗ ██████╗  ██████╗ ███╗   ██╗██████╗ ██╗ █████╗ ██████╗ ███████╗[/bold magenta]\n" +
            "[bold magenta]██╔══██╗██╔══██╗██╔═══██╗████╗  ██║██╔══██╗██║██╔══██╗██╔══██╗██╔════╝[/bold magenta]\n" +
            "[bold magenta]██████╔╝██████╔╝██║   ██║██╔██╗ ██║██████╔╝██║███████║██████╔╝█████╗  [/bold magenta]\n" +
            "[bold magenta]██╔═══╝ ██╔══██╗██║   ██║██║╚██╗██║██╔═══╝ ██║██╔══██║██╔══██╗██╔══╝  [/bold magenta]\n" +
            "[bold magenta]██║     ██║  ██║╚██████╔╝██║ ╚████║██║     ██║██║  ██║██║  ██║███████╗[/bold magenta]\n" +
            "[bold magenta]╚═╝     ╚═╝  ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝[/bold magenta]\n"
        )
        header_text = f"Bem-Vindo(a) ao [bold blue]Painel Doctor Coringa Lunático[/bold blue] | Uso Educacional Seguro"
        ip_text = f"Seu Endereço de IP: [bold blue]{ip}[/bold blue]"

        pix_info = "[bold green]PIX:[/bold green] 06acdb...629d"
        contato_info = "Telegram: [bold cyan]@K_iny[/bold cyan] | WhatsApp: [bold cyan]+55 21 7918-0533[/bold cyan]"

        console.print(Panel(Align.center(banner), border_style="magenta"))
        console.print(Panel(header_text, border_style="blue"))
        console.print(Panel(ip_text, border_style="blue"))
        console.print(Panel(pix_info, border_style="green"))
        console.print(Panel(contato_info, border_style="cyan"))

        options = [
            "Ping Sweep - Descoberta de Hosts",
            "Scanner de Portas TCP",
            "Consulta DNS",
            "Brute Force Local",
            "Mostrar Processos CPU",
            "Informações de Rede",
            "GeoIP Lookup",
            "Enumeração HTTP",
            "Sobre e Créditos",
            "Sair"
        ]

        menu_table = Table.grid(padding=(0, 2))
        menu_table.title = "[bold green]Menu Principal - Escolha a Opção[/bold green]"
        menu_table.expand = False
        cols = 2
        for _ in range(cols):
            menu_table.add_column(justify="left")

        rows = [options[i:i + cols] for i in range(0, len(options), cols)]
        for row in rows:
            if len(row) < cols:
                row.append("")
            menu_table.add_row(*row)

        console.print(menu_table)

        choice = Prompt.ask("[green]Digite o número da opção desejada[/green]").strip()

        if choice == "1":
            clear_screen()
            type_message("Ping Sweep: Varredura para identificar hosts ativos na rede local.")
            base_ip = Prompt.ask("Informe o início do bloco IP (ex: 192.168.0)").strip()
            ping_sweep(base_ip)
        elif choice == "2":
            clear_screen()
            type_message("Scanner de Portas TCP: Detecta portas abertas postas a testar.")
            target = Prompt.ask("IP ou Hostname alvo").strip()
            ports_input = Prompt.ask("Portas (ex: 22,80,443 ou 20-1024)").strip()
            try:
                if '-' in ports_input:
                    start, end = ports_input.split('-')
                    ports = list(range(int(start), int(end) + 1))
                else:
                    ports = [int(p.strip()) for p in ports_input.split(',')]
                port_scan(target, ports)
            except Exception as e:
                type_message(f"Entrada inválida para portas: {e}")
                pause()
        elif choice == "3":
            clear_screen()
            type_message("Consulta DNS: Resolve domínio para endereço IP.")
            dns_lookup()
        elif choice == "4":
            clear_screen()
            type_message("Brute Force Educacional: Teste simples e seguro para aprender brute force.")
            simple_brute_force()
        elif choice == "5":
            clear_screen()
            type_message("Mostrando processos que mais usam CPU.")
            show_processes()
        elif choice == "6":
            clear_screen()
            type_message("Informações sobre interfaces de rede e status.")
            network_info()
        elif choice == "7":
            clear_screen()
            type_message("GeoIP Lookup: Localiza geograficamente um IP.")
            geoip_lookup()
        elif choice == "8":
            clear_screen()
            type_message("Enumeração HTTP: Recupera título e cabeçalhos HTTP.")
            http_enum()
        elif choice == "9":
            clear_screen()
            show_about()
        elif choice == "10" or choice.lower() == "q":
            clear_screen()
            type_message("Obrigado por usar o Painel Doctor Coringa Lunático. Fique seguro e continue aprendendo!")
            break
        else:
            type_message("Opção inválida, tente novamente.")

if __name__ == "__main__":
    try:
        main_menu()
    except KeyboardInterrupt:
        clear_screen()
        console.print("[green]\nPrograma encerrado pelo usuário.[/green]")
        
