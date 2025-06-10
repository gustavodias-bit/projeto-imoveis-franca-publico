import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import logging
from datetime import datetime
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def setup_driver():
    """Configura Firefox headless"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--width=1920')
    options.add_argument('--height=1080')
    
    driver = webdriver.Firefox(options=options)
    driver.implicitly_wait(10)
    return driver

def coletar_fotos_imovel(driver, imovel):
    """Coleta URLs das fotos usando data-src"""
    try:
        driver.get(imovel['url'])
        time.sleep(3)
        
        # JavaScript para pegar TODAS as imagens com data-src
        js_code = """
        var imgs = [];
        document.querySelectorAll('img[data-src]').forEach(function(img) {
            var src = img.getAttribute('data-src');
            if (src && src.includes('cdn.uso.com.br') && src.includes('.jpg')) {
                imgs.push(src);
            }
        });
        return imgs;
        """
        
        # Executar JavaScript
        image_urls = driver.execute_script(js_code)
        
        # Remover duplicatas mantendo ordem
        seen = set()
        unique_urls = []
        for url in image_urls:
            if url not in seen and 'foto_vazio' not in url:
                seen.add(url)
                unique_urls.append(url)
        
        # Adicionar ao imóvel
        imovel['images'] = unique_urls[:25]  # Máximo 25 fotos
        imovel['images_count'] = len(unique_urls)
        imovel['images_collected_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        logging.info(f"✅ {len(unique_urls)} fotos - {imovel.get('neighborhood', 'N/A')} - R$ {imovel.get('price', 0):,.0f}")
        return True
        
    except Exception as e:
        logging.error(f"❌ Erro: {e}")
        imovel['images'] = []
        imovel['images_count'] = 0
        return False

def main():
    # Carregar imóveis
    with open('data/processed/IMOVEIS_COMPLETOS_FINAL.json', 'r') as f:
        imoveis = json.load(f)
    
    logging.info(f"🏠 Total de imóveis: {len(imoveis)}")
    
    # Setup driver
    driver = setup_driver()
    
    # Processar TODOS (não só os sem fotos)
    batch_size = 20
    total_processados = 0
    total_fotos = 0
    
    try:
        for i in range(0, len(imoveis), batch_size):
            batch = imoveis[i:i+batch_size]
            logging.info(f"\n📦 Lote {i//batch_size + 1} ({len(batch)} imóveis)")
            
            for imovel in batch:
                if coletar_fotos_imovel(driver, imovel):
                    total_fotos += imovel.get('images_count', 0)
                
                total_processados += 1
                time.sleep(2)  # Delay entre requisições
                
                # Backup a cada 50 imóveis
                if total_processados % 50 == 0:
                    backup_file = f'data/processed/backup_fotos_{total_processados}.json'
                    with open(backup_file, 'w') as f:
                        json.dump(imoveis, f, ensure_ascii=False, indent=2)
                    logging.info(f"💾 Backup: {backup_file}")
            
            # Pausa entre lotes
            if i + batch_size < len(imoveis):
                logging.info("⏸️  Pausa 10s...")
                time.sleep(10)
    
    finally:
        driver.quit()
    
    # Salvar resultado final
    output_file = f'data/processed/IMOVEIS_COM_FOTOS_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(imoveis, f, ensure_ascii=False, indent=2)
    
    logging.info(f"""
    
    ✅ COLETA CONCLUÍDA!
    =====================================
    📊 Imóveis processados: {total_processados}
    🖼️  Total de fotos: {total_fotos}
    📁 Arquivo: {output_file}
    =====================================
    """)

if __name__ == "__main__":
    main()
