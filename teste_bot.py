import sys
sys.path.insert(0, r'c:\olx-bot')
import bot as bot_module

print("=== TESTE DO BOT COM TODOS OS PRODUTOS ===")
print("Produtos configurados:")
for i, p in enumerate(bot_module.PRODUTOS, 1):
    print(f"{i}. {p['nome']} - URL: {p.get('url_base', 'padrão')} - Máx: R$ {p['max_preco']}")

print("\nIniciando verificação única...")
bot_module.vistos = bot_module.carregar_vistos()
print(f"Anúncios já vistos carregados: {len(bot_module.vistos)}")

# Executar uma verificação
bot_module.rodar_bot()

print("\n=== TESTE CONCLUÍDO ===")
print(f"Total de anúncios vistos agora: {len(bot_module.vistos)}")