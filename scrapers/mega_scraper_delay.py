from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import json
import re
from datetime import datetime
import time
import random

print("🚀 MEGA SCRAPER COM DELAY - MODO STEALTH")
print("⏱️  Delay de 5 segundos entre requisições")
print("🎯 Meta: Coletar o máximo possível\n")

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-blink-features=AutomationControlled')
options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36')

driver = webdriver.Firefox(options=options)
all_properties = []
page = 1
errors_count = 0
max_errors = 5

try:
    while errors_count < max_errors:
        url = f"https://www.olafranca.com.br/comprar/pagina-{page}/"
        print(f"\n📄 Página {page}: {url}")
        
        try:
            driver.get(url)
            time.sleep(5)
            
            links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/casa/"], a[href*="/apartamento/"]')
            
            if not links:
                print("❌ Sem mais imóveis")
                break
                
            page_links = []
            for elem in links:
                href = elem.get_attribute('href')
                if href and '/franca/' in href and href not in [p['url'] for p in all_properties]:
                    page_links.append(href)
            
            print(f"   📊 {len(page_links)} novos imóveis encontrados")
            
            for i, url in enumerate(page_links):
                try:
                    print(f"   🏠 [{i+1}/{len(page_links)}] Processando...")
                    driver.get(url)
                    time.sleep(3 + random.randint(1, 3))
                    
                    text = driver.find_element(By.TAG_NAME, "body").text
                    data = {'url': url, 'scraped_at': datetime.now().isoformat()}
                    
                    price_match = re.search(r'R\$\s*([\d\.]+)', text)
                    if price_match:
                        data['price'] = float(price_match.group(1).replace('.', ''))
                    
                    rooms_match = re.search(r'(\d+)\s*quartos?', text, re.I)
                    if rooms_match:
                        data['rooms'] = int(rooms_match.group(1))
                    
                    area_match = re.search(r'(\d+)\s*m[²2]', text)
                    if area_match:
                        data['area'] = int(area_match.group(1))
                    
                    parts = url.split('/')
                    if 'franca' in parts:
                        idx = parts.index('franca')
                        if idx + 1 < len(parts):
                            data['neighborhood'] = parts[idx + 1].replace('-', ' ').title()
                    
                    if data.get('price', 0) > 0:
                        all_properties.append(data)
                        print(f"      ✅ {data['neighborhood']} - R$ {data['price']:,.0f}")
                    
                    if len(all_properties) % 10 == 0:
                        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                        backup = f"data/processed/backup_{timestamp}.json"
                        with open(backup, 'w') as f:
                            json.dump(all_properties, f, indent=2)
                        print(f"      💾 Backup: {len(all_properties)} imóveis")
                        
                except Exception as e:
                    print(f"      ⚠️ Erro no imóvel: {str(e)[:50]}")
                    time.sleep(10)
            
            page += 1
            errors_count = 0
            
            print(f"   ⏳ Aguardando 10s antes da próxima página...")
            time.sleep(10)
            
        except Exception as e:
            print(f"❌ Erro na página {page}: {str(e)[:50]}")
            errors_count += 1
            print(f"⏳ Aguardando 30s... (Erro {errors_count}/{max_errors})")
            time.sleep(30)
            
except KeyboardInterrupt:
    print("\n⚠️ Interrompido pelo usuário!")
    
finally:
    driver.quit()
    
    if all_properties:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output = f"data/processed/mega_final_{timestamp}.json"
        
        with open(output, 'w') as f:
            json.dump(all_properties, f, indent=2)
        
        print(f"\n🎉 COLETA FINALIZADA!")
        print(f"📊 Total: {len(all_properties)} imóveis")
        print(f"💾 Arquivo final: {output}")
