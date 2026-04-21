import time
import requests
import json
import os
import re
import sys
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv

# UTF-8 encoding
sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

# CONFIG
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# Produtos para monitorar
PRODUTOS = [
    {"nome": "RTX 5060", "keyword": "rtx 5060", "max_preco": 1900, "url_base": "https://www.olx.com.br/brasil?q=rtx+5060&sp=2&opst=2"},
    {"nome": "RTX 4060", "keyword": "rtx 4060", "max_preco": 1500, "url_base": "https://www.olx.com.br/brasil?q=rtx+4060&sp=2&opst=2"},
    {"nome": "RTX 3070", "keyword": "rtx 3070", "max_preco": 1900, "url_base": "https://www.olx.com.br/brasil?q=rtx+3070&sp=2&opst=2"},
    {"nome": "Mouse Superlight 2", "keyword": "mouse superlight 2", "max_preco": 450, "url_base": "https://www.olx.com.br/brasil?q=mouse+superlight+2&sp=2&opst=2"},
]

SEEN_FILE = "vistos.json"

def extrair_preco(ad):
    try:
        # Debug: mostrar HTML do elemento
        html_text = ad.inner_html()
        print(f"    [DEBUG] HTML do anúncio:\n{html_text[:500]}\n")
        
        preco_elem = ad.query_selector("h3.olx-adcard__price")
        if preco_elem:
            preco_text = preco_elem.inner_text().strip()
            print(f"    [DEBUG] Texto bruto do preço: '{preco_text}'")
            # Tira 'R$' e espaços
            preco_limpo = preco_text.replace('R$', '').strip()
            print(f"    [DEBUG] Preço limpo: '{preco_limpo}'")
            # Substitui . por vazio e , por .
            preco_convertido = preco_limpo.replace('.', '').replace(',', '.')
            print(f"    [DEBUG] Preço convertido: '{preco_convertido}'")
            return float(preco_convertido)
    except Exception as e:
        print(f"    [DEBUG] Erro ao extrair: {e}")
    return None

def debug_bot():
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

        # Testar apenas RTX 5060
        produto = PRODUTOS[0]
        keyword = produto["keyword"].replace(' ', '+')
        url_base = produto.get("url_base", f"https://www.olx.com.br/brasil?q={keyword}&sp=2&opst=2")
        url = f"{url_base}&o=1"
        
        print(f"\n🔍 Testando {produto['nome']} - URL: {url}")
        print(f"Preço máximo permitido: R$ {produto['max_preco']}")
        
        try:
            page.goto(url, timeout=60000, wait_until='domcontentloaded')
            page.wait_for_selector("div.olx-adcard__content", timeout=30000)
            page.wait_for_timeout(2000)

            anuncios = page.query_selector_all("div.olx-adcard__content")
            print(f"\n✅ Encontrados {len(anuncios)} anúncios\n")

            for i, ad in enumerate(anuncios[:10]):  # Testar apenas os 10 primeiros
                print(f"\n{'='*80}")
                print(f"ANÚNCIO #{i+1}")
                print(f"{'='*80}")
                
                # Extrair informações
                link_elem = ad.query_selector("a[data-testid='adcard-link']")
                titulo_elem = ad.query_selector("h2.olx-adcard__title")
                
                link = link_elem.get_attribute("href") if link_elem else "N/A"
                titulo = titulo_elem.inner_text().strip() if titulo_elem else "N/A"
                
                print(f"Título: {titulo}")
                print(f"Link: {link}")
                
                preco = extrair_preco(ad)
                
                print(f"\n    ✅ PREÇO EXTRAÍDO: R$ {preco:.2f}" if preco else f"    ❌ NÃO FOI POSSÍVEL EXTRAIR PREÇO")
                
                if preco is not None:
                    if preco <= produto["max_preco"]:
                        print(f"    🔥 ALERTA! Preço ABAIXO do limite (R$ {preco:.2f} <= R$ {produto['max_preco']:.2f})")
                    else:
                        print(f"    ⚠️  Preço acima do limite (R$ {preco:.2f} > R$ {produto['max_preco']:.2f})")

        except Exception as e:
            print(f"❌ Erro: {e}")

        browser.close()

if __name__ == "__main__":
    debug_bot()
