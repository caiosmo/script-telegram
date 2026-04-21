import time
import requests
import json
import os
import re
import sys
import threading
from datetime import datetime, timedelta
import tkinter as tk
from tkinter import scrolledtext
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

load_dotenv()

# CONFIG
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")  # Defina no arquivo .env
CHAT_ID = os.getenv("CHAT_ID")  # Defina no arquivo .env

# Produtos para monitorar
PRODUTOS = [
    {"nome": "RTX 5060", "keyword": "rtx 5060", "max_preco": 1900, "url_base": "https://www.olx.com.br/brasil?q=rtx+5060&sp=2&opst=2"},
    {"nome": "RTX 4060", "keyword": "rtx 4060", "max_preco": 1500, "url_base": "https://www.olx.com.br/brasil?q=rtx+4060&sp=2&opst=2"},
    {"nome": "RTX 3070", "keyword": "rtx 3070", "max_preco": 1550, "url_base": "https://www.olx.com.br/brasil?q=rtx+3070&sp=2&opst=2"},
    {"nome": "RTX 3060", "keyword": "rtx 3060", "max_preco": 1200, "url_base": "https://www.olx.com.br/brasil?q=rtx%203060&sp=2&opst=2"},
    {"nome": "RTX 3060 Ti", "keyword": "rtx 3060 ti", "max_preco": 1400, "url_base": "https://www.olx.com.br/brasil?q=rtx%203060%20ti&sp=2&opst=2"},
    {"nome": "RTX 3070 Ti", "keyword": "3070 ti", "max_preco": 1700, "url_base": "https://www.olx.com.br/brasil?q=3070%20ti&sp=2&opst=2"},
    {"nome": "RTX 3080", "keyword": "rtx 3080", "max_preco": 2200, "url_base": "https://www.olx.com.br/brasil?q=rtx%203080&sp=2&opst=2"},
    {"nome": "RTX 3080 Ti", "keyword": "rtx 3080 ti", "max_preco": 2500, "url_base": "https://www.olx.com.br/brasil?q=rtx%203080%20ti&sp=2&opst=2"},
    {"nome": "RTX 4060 Ti", "keyword": "rtx 4060 ti", "max_preco": 1700, "url_base": "https://www.olx.com.br/brasil?q=rtx%204060%20ti&sp=2&opst=2"},
    {"nome": "RTX 4070", "keyword": "rtx 4070", "max_preco": 2900, "url_base": "https://www.olx.com.br/brasil?q=rtx%204070&sp=2&opst=2"},
    {"nome": "RTX 4070 Ti", "keyword": "rtx 4070 ti", "max_preco": 3500, "url_base": "https://www.olx.com.br/brasil?q=rtx%204070%20ti&sp=2&opst=2"},
    {"nome": "RTX 5060 Ti", "keyword": "rtx 5060 ti", "max_preco": 2550, "url_base": "https://www.olx.com.br/brasil?q=rtx%205060%20ti&sp=2&opst=2"},
    {"nome": "RTX 5070", "keyword": "rtx 5070", "max_preco": 3500, "url_base": "https://www.olx.com.br/brasil?q=rtx%205070&sp=2&opst=2"},
    {"nome": "Mouse Maya", "keyword": "lamzu maya x", "max_preco": 500, "url_base": "https://www.olx.com.br/informatica/perifericos-e-acessorios-de-computador?q=lamzu%20maya%20x&sp=2&opst=2"},
    {"nome": "Mouse Superlight 2", "keyword": "mouse superlight 2", "max_preco": 450, "url_base": "https://www.olx.com.br/brasil?q=mouse+superlight+2&sp=2&opst=2"},
    # Adicione mais produtos aqui
]

SEEN_FILE = "vistos.json"

# Inicializa vistos
vistos = set()

def carregar_vistos():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, 'r') as f:
            data = json.load(f)
            return {tuple(item) for item in data}
    return set()

def salvar_vistos(vistos):
    with open(SEEN_FILE, 'w') as f:
        json.dump([list(item) for item in vistos], f)

def enviar_telegram(msg):
    if not TELEGRAM_TOKEN or TELEGRAM_TOKEN == "SEU_TOKEN_AQUI":
        print("❌ Token do Telegram não configurado. Configure TELEGRAM_TOKEN.")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    data = {
        "chat_id": CHAT_ID,
        "text": msg
    }
    try:
        response = requests.post(url, data=data)
        if response.status_code == 200:
            print(f"✅ Mensagem enviada ao Telegram com sucesso!")
        else:
            print(f"❌ Erro ao enviar Telegram: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Erro de conexão ao enviar Telegram: {e}")

def extrair_preco(ad):
    try:
        preco_elem = ad.query_selector("h3.olx-adcard__price")
        if preco_elem:
            preco_text = preco_elem.inner_text().strip()
            # Tira 'R$' e espaços
            preco_limpo = preco_text.replace('R$', '').strip()
            # Substitui . por vazio e , por .
            preco_convertido = preco_limpo.replace('.', '').replace(',', '.')
            return float(preco_convertido)
    except Exception as e:
        pass
    return None

def rodar_bot():
    global vistos
    if not vistos:
        vistos = carregar_vistos()
    novos = []
    ja_vistos_bons = []
    
    inicio = datetime.now()
    print(f"\n🕐 Iniciando verificação em {inicio.strftime('%d/%m/%Y %H:%M:%S')}")
    # Debug: mostrar quantos anúncios já foram marcados como vistos
    print(f"📊 Total de anúncios já marcados como vistos: {len(vistos)}\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=False,
            args=["--disable-blink-features=AutomationControlled"],
        )
        context = browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            locale='pt-BR',
            timezone_id='America/Sao_Paulo',
        )
        page = context.new_page()
        page.set_extra_http_headers({
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'pt-BR,pt;q=0.8,en-US;q=0.5,en;q=0.3',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })

        for produto in PRODUTOS:
            keyword = produto["keyword"].replace(' ', '+')
            url_base = produto.get("url_base", f"https://www.olx.com.br/brasil?q={keyword}&sp=2&opst=2")
            page_num = 1
            while page_num <= 1:  # Verificar apenas a primeira página (ordenado por menor preço)
                url = f"{url_base}&o={page_num}"
                print(f"Verificando {produto['nome']} - Página {page_num}...")

                try:
                    page.goto(url, timeout=60000, wait_until='domcontentloaded')
                    page.wait_for_selector("div.olx-adcard__content", timeout=30000)
                    page.wait_for_timeout(2000)

                    anuncios = page.query_selector_all("div.olx-adcard__content")

                    print(f"Encontrados {len(anuncios)} anúncios para {produto['nome']} página {page_num}")

                    if not anuncios:
                        break  # Não há mais anúncios

                    for ad in anuncios:
                        link_elem = ad.query_selector("a[data-testid='adcard-link']")
                        titulo_elem = ad.query_selector("h2.olx-adcard__title")
                        link = link_elem.get_attribute("href") if link_elem else None
                        titulo = titulo_elem.inner_text().strip() if titulo_elem else ad.inner_text().split('\n')[0]
                        preco = extrair_preco(ad)

                        # Debug: mostrar cada anúncio processado
                        print(f"  - {titulo} | Preço: {preco}")

                        # Ignorar anúncios que contenham palavras indesejadas no título
                        if titulo and any(palavra.lower() in titulo.lower() for palavra in ["caixa", "bloco", "troco", "cooler", "adaptador", "espelho"]):
                            print(f"    ❌ IGNORADO: Contém título indesejado")
                            continue

                        if link:
                            # Verificar se o preço está dentro do limite
                            if preco is not None and preco <= produto["max_preco"]:
                                print(f"    ✅ PREÇO BOM ENCONTRADO! R$ {preco:.2f} <= R$ {produto['max_preco']:.2f}")
                                
                                # Marcar como visto e adicionar aos novos
                                if (produto["nome"], link) not in vistos:
                                    vistos.add((produto["nome"], link))
                                    novos.append((produto["nome"], titulo, preco, link))
                                    print(f"    🔥 ADICIONADO À FILA DE ENVIO TELEGRAM!")
                                else:
                                    print(f"    ⚠️  Já foi visto antes, mas preço é bom!")
                                    ja_vistos_bons.append((produto["nome"], titulo, preco, link))
                            elif preco is not None and preco > produto["max_preco"]:
                                print(f"    ⚠️ Preço acima do limite (R$ {preco:.2f} > R$ {produto['max_preco']:.2f})")
                            elif preco is None:
                                print(f"    ⚠️ Preço não extraído")
                        else:
                            print(f"    ⚠️ Sem link disponível")

                    page_num += 1

                except Exception as e:
                    print(f"Erro ao verificar {produto['nome']} página {page_num}: {e}")
                    break

        browser.close()

    for nome_produto, titulo, preco, link in novos:
        msg = f"🔥 NOVO ANÚNCIO - {nome_produto}!\n\n{titulo}\nPreço: R$ {preco:.2f}\n{link}"
        print(f"\n🔥 NOVO ANÚNCIO - {nome_produto} | {titulo} | R$ {preco:.2f} | {link}")
        enviar_telegram(msg)

    print(f"\n📊 RESUMO: {len(novos)} novos anúncios encontrados")

    if ja_vistos_bons:
        print(f"\n🔁 ANÚNCIOS COM BOM PREÇO JÁ VISTOS ANTERIORMENTE ({len(ja_vistos_bons)}):")
        for nome_p, titulo_p, preco_p, link_p in ja_vistos_bons:
            print(f"  • [{nome_p}] {titulo_p} | R$ {preco_p:.2f} | {link_p}")
    else:
        print("\n🔁 Nenhum anúncio repetido com bom preço neste ciclo.")

    salvar_vistos(vistos)

stop_event = threading.Event()


def loop_bot(intervalo_minutos):
    while not stop_event.is_set():
        rodar_bot()
        proxima = datetime.now() + timedelta(minutes=intervalo_minutos)
        print(f"\n⏱️ ({proxima.strftime('%d/%m/%Y %H:%M:%S')}) Próxima verificação em {intervalo_minutos} minuto(s)...")
        stop_event.wait(timeout=intervalo_minutos * 60)
    print("\n🛑 Bot parado.")


class TextRedirector:
    """Redireciona stdout para o widget de log do tkinter de forma thread-safe."""
    def __init__(self, widget):
        self.widget = widget

    def write(self, text):
        def _insert():
            self.widget.configure(state='normal')
            self.widget.insert(tk.END, text)
            self.widget.see(tk.END)
            self.widget.configure(state='disabled')
        self.widget.after(0, _insert)

    def flush(self):
        pass


def criar_gui():
    global vistos
    vistos = carregar_vistos()

    root = tk.Tk()
    root.title("OLX Bot Monitor")
    root.geometry("950x620")
    root.minsize(700, 450)
    root.configure(bg='#2b2b2b')

    # ── Barra de controles ──────────────────────────────────────────────────
    frame_top = tk.Frame(root, bg='#3c3c3c', pady=10, padx=12)
    frame_top.pack(fill='x')

    tk.Label(
        frame_top, text="Intervalo (minutos):",
        bg='#3c3c3c', fg='#cccccc', font=('Segoe UI', 10)
    ).pack(side='left')

    entry_intervalo = tk.Entry(frame_top, width=6, font=('Segoe UI', 10), justify='center')
    entry_intervalo.insert(0, "30")
    entry_intervalo.pack(side='left', padx=(5, 15))

    lbl_status = tk.Label(
        frame_top, text="● Parado",
        bg='#3c3c3c', fg='#e74c3c', font=('Segoe UI', 10, 'bold')
    )
    lbl_status.pack(side='right', padx=10)

    def iniciar():
        try:
            intervalo = int(entry_intervalo.get())
            if intervalo < 1:
                intervalo = 1
        except ValueError:
            intervalo = 30
            entry_intervalo.delete(0, tk.END)
            entry_intervalo.insert(0, "30")

        stop_event.clear()
        btn_iniciar.config(state='disabled')
        btn_parar.config(state='normal')
        entry_intervalo.config(state='disabled')
        lbl_status.config(text="● Rodando", fg='#27ae60')

        t = threading.Thread(target=loop_bot, args=(intervalo,), daemon=True)
        t.start()

    def parar():
        stop_event.set()
        btn_iniciar.config(state='normal')
        btn_parar.config(state='disabled')
        entry_intervalo.config(state='normal')
        lbl_status.config(text="● Parando...", fg='#f39c12')

        def resetar_status():
            if stop_event.is_set():
                lbl_status.config(text="● Parado", fg='#e74c3c')
        root.after(2000, resetar_status)

    btn_iniciar = tk.Button(
        frame_top, text="▶  Iniciar", bg='#27ae60', fg='white',
        font=('Segoe UI', 10, 'bold'), width=10, relief='flat',
        activebackground='#2ecc71', activeforeground='white', command=iniciar
    )
    btn_parar = tk.Button(
        frame_top, text="⏹  Parar", bg='#e74c3c', fg='white',
        font=('Segoe UI', 10, 'bold'), width=10, relief='flat',
        activebackground='#c0392b', activeforeground='white',
        state='disabled', command=parar
    )
    btn_iniciar.pack(side='left', padx=(0, 5))
    btn_parar.pack(side='left')

    # ── Área de log ─────────────────────────────────────────────────────────
    frame_log = tk.Frame(root, bg='#2b2b2b', padx=10, pady=8)
    frame_log.pack(fill='both', expand=True)

    tk.Label(
        frame_log, text="Log de execução:",
        bg='#2b2b2b', fg='#aaaaaa', font=('Segoe UI', 9)
    ).pack(anchor='w')

    log_text = scrolledtext.ScrolledText(
        frame_log, state='disabled', wrap='word',
        font=('Consolas', 9), bg='#1e1e1e', fg='#d4d4d4',
        insertbackground='white', relief='flat', borderwidth=0
    )
    log_text.pack(fill='both', expand=True)

    # Redireciona stdout para o widget de log
    sys.stdout = TextRedirector(log_text)

    root.mainloop()


if __name__ == "__main__":
    criar_gui()