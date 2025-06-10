# Sistema de Scraping de Imóveis - Franca/SP

## Arquivos Principais

### Scrapers
- `mega_scraper_delay.py` - Scraper principal que coletou 799 imóveis
- `coletar_fotos_correto.py` - Coleta URLs das fotos dos imóveis
- `continuar_coleta.py` - Para continuar coletas interrompidas

### Processamento
- `image_processing/logo_removal.py` - Remove logos com YOLO
- `data_processing/pipeline.py` - Limpa e padroniza dados

### Dados
- `data/processed/IMOVEIS_COMPLETOS_FINAL.json` - 799 imóveis com dados completos

## Como Usar
1. Instalar dependências: `pip install -r requirements.txt`
2. Configurar `.env` baseado no `.env.example`
3. Rodar scrapers conforme necessário

## Observações
- Projeto em desenvolvimento
- Dados reais de Franca/SP
- Sistema modular e expansível
