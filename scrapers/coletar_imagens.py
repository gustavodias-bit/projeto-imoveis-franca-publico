import json
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import logging
from datetime import datetime

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def setup_driver():
    """Configura o Selenium"""
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1920,1080')
    options.add_argument('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')
    
    return webdriver.Chrome(options=options)

def coletar_imagens_imovel(driver, imovel, timeout=10):
    """Coleta URLs das imagens de um imóvel"""
    try:
        url = imovel['url']
        driver.get(url)
        
        # Aguardar página carregar
        time.sleep(3)
        
        # Buscar imagens - ajustar seletores conforme o site
        image_urls = []
        
        # Tentar diferentes seletores comuns
        selectors = [
            'img.gallery-image',
            'img[data-src]',
            'div.carousel img',
            '.property-images img',
            'img[src*="imoveis"]',
            'img[src*="property"]'
        ]
        
        for selector in selectors:
            try:
                images = driver.find_elements(By.CSS_SELECTOR, selector)
                for img in images:
                    src = img.get_attribute('src') or img.get_attribute('data-src')
                    if src and 'http' in src:
                        image_urls.append(src)
            except:
                pass
        
        # Remover duplicatas
        image_urls = list(set(image_urls))
        
        # Adicionar ao objeto do imóvel
        imovel['images'] = image_urls
        imovel['images_count'] = len(image_urls)
        imovel['collected_at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        logging.info(f"✅ {len(image_urls)} imagens encontradas para: {imovel.get('neighborhood', 'N/A')}")
        return True
        
    except Exception as e:
        logging.error(f"❌ Erro coletando imagens: {e}")
        imovel['images'] = []
        imovel['images_count'] = 0
        imovel['error'] = str(e)
        return False

def main():
    # Carregar imóveis
    with open('data/processed/IMOVEIS_UNICOS_FINAL.json', 'r') as f:
        imoveis = json.load(f)
    
    logging.info(f"🏠 Total de imóveis para processar: {len(imoveis)}")
    
    # Configurar driver
    driver = setup_driver()
    
    # Processar em lotes
    batch_size = 50
    processed = 0
    
    try:
        for i in range(0, len(imoveis), batch_size):
            batch = imoveis[i:i+batch_size]
            
            for imovel in batch:
                coletar_imagens_imovel(driver, imovel)
                processed += 1
                
                # Delay entre requisições
                time.sleep(2)
                
                # Salvar progresso a cada 10 imóveis
                if processed % 10 == 0:
                    logging.info(f"📊 Progresso: {processed}/{len(imoveis)}")
                    # Backup
                    with open(f'data/processed/imoveis_com_imagens_backup_{processed}.json', 'w') as f:
                        json.dump(imoveis[:processed], f, ensure_ascii=False, indent=2)
            
            # Pausa entre lotes
            logging.info(f"⏸️  Pausa entre lotes... ({processed}/{len(imoveis)})")
            time.sleep(5)
    
    finally:
        driver.quit()
    
    # Salvar resultado final
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_file = f'data/processed/IMOVEIS_COM_IMAGENS_{timestamp}.json'
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(imoveis, f, ensure_ascii=False, indent=2)
    
    # Estatísticas
    total_images = sum(im.get('images_count', 0) for im in imoveis)
    with_images = sum(1 for im in imoveis if im.get('images_count', 0) > 0)
    
    logging.info(f"""
    ✅ COLETA CONCLUÍDA!
    - Total de imóveis: {len(imoveis)}
    - Imóveis com fotos: {with_images}
    - Total de imagens: {total_images}
    - Arquivo salvo: {output_file}
    """)

if __name__ == "__main__":
    main()
