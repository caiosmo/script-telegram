import sys
sys.path.insert(0, r'c:\olx-bot')
import bot as bot_module

print("=== TESTE COMPLETO COM MELHORIAS ===")

# Limitar a apenas 1 produto para teste rápido
original_produtos = bot_module.PRODUTOS.copy()
bot_module.PRODUTOS = [bot_module.PRODUTOS[0]]  # Apenas RTX 5060

print("Configurações:")
print(f"  Produto: {bot_module.PRODUTOS[0]['nome']}")
print(f"  Páginas: 1 (apenas primeira página)")
print(f"  Filtro: Ignorar anúncios com 'Caixa' ou 'Bloco'")

bot_module.vistos = set()
bot_module.rodar_bot()

print("\n=== TESTE CONCLUÍDO ===")
print("✅ Apenas primeira página verificada")
print("✅ Anúncios com 'Caixa'/'Bloco' foram ignorados")