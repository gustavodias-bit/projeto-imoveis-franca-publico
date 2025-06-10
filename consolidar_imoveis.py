import json
from pathlib import Path

# Carregar arquivo original
with open('data/processed/IMOVEIS_UNICOS_FINAL.json', 'r') as f:
    imoveis_antigos = json.load(f)

# Carregar novos imóveis
with open('data/processed/completo_20250610_170209.json', 'r') as f:
    imoveis_novos = json.load(f)

print(f"📊 Imóveis antigos: {len(imoveis_antigos)}")
print(f"📊 Imóveis novos: {len(imoveis_novos)}")

# Criar set de URLs para evitar duplicatas
urls_existentes = {im.get('url', '') for im in imoveis_antigos}

# Adicionar apenas imóveis novos
adicionados = 0
for imovel in imoveis_novos:
    if imovel.get('url') not in urls_existentes:
        imoveis_antigos.append(imovel)
        adicionados += 1

print(f"✅ Adicionados: {adicionados}")
print(f"🏠 TOTAL FINAL: {len(imoveis_antigos)} imóveis únicos!")

# Salvar arquivo consolidado
with open('data/processed/IMOVEIS_COMPLETOS_FINAL.json', 'w') as f:
    json.dump(imoveis_antigos, f, ensure_ascii=False, indent=2)

print("✅ Arquivo salvo: data/processed/IMOVEIS_COMPLETOS_FINAL.json")
