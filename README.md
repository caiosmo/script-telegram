# OLX Bot - Monitor de Anúncios

Bot que monitora anúncios de GPUs e periféricos na OLX e envia alertas via Telegram quando encontra ofertas abaixo do preço configurado.

## Funcionalidades

- Monitora múltiplos produtos simultaneamente
- Filtra por preço máximo
- Envia notificações via Telegram com link direto para o anúncio
- Interface gráfica (Tkinter) para acompanhamento em tempo real
- Evita notificações duplicadas

## Requisitos

- Python 3.10+
- Conta no Telegram com um bot criado via [@BotFather](https://t.me/BotFather)

## Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/olx-bot.git
cd olx-bot

# Crie e ative o ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows

# Instale as dependências
pip install -r requirements.txt

# Instale os navegadores do Playwright
playwright install chromium
```

## Configuração

Crie um arquivo `.env` na raiz do projeto com suas credenciais:

```env
TELEGRAM_TOKEN=seu_token_aqui
CHAT_ID=seu_chat_id_aqui
```

Para obter o `CHAT_ID`, envie uma mensagem para o seu bot e acesse:
`https://api.telegram.org/bot<SEU_TOKEN>/getUpdates`

## Uso

```bash
python bot.py
```

## Produtos Monitorados

Configure os produtos no array `PRODUTOS` dentro de `bot.py`, definindo:
- `nome`: Nome do produto
- `keyword`: Palavra-chave para filtrar anúncios
- `max_preco`: Preço máximo aceitável (R$)
- `url_base`: URL de busca na OLX
