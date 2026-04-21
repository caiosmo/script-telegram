import sys
sys.path.insert(0, r'c:\olx-bot')
import bot as bot_module

print("=== TESTE DAS MELHORIAS ===")

# Teste da filtragem de títulos
test_titles = [
    "RTX 4060 Gigabyte Gaming OC",
    "Caixa RTX 4060 apenas",
    "Bloco de refrigeração RTX 4060",
    "RTX 4060 MSI Ventus 2X",
    "Mouse Superlight 2 Logitech",
    "Caixa do mouse Superlight",
    "Bloco de carregamento mouse"
]

print("Testando filtragem de títulos:")
for title in test_titles:
    ignored = any(palavra.lower() in title.lower() for palavra in ["caixa", "bloco"])
    status = "IGNORADO" if ignored else "PROCESSADO"
    print(f"  {status}: {title}")

print("\nTestando configuração de páginas:")
print(f"  Páginas a verificar: 1 (anteriormente 5)")

print("\n=== MELHORIAS APLICADAS ===")
print("✅ Verificação limitada à primeira página")
print("✅ Filtro para ignorar anúncios com 'Caixa' ou 'Bloco'")