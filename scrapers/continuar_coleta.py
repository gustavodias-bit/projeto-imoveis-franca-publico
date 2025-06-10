from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
import json
import re
from datetime import datetime
import time
import random

print("🚀 CONTINUANDO COLETA - PÁGINA 22+")
print("📊 Já temos 192 imóveis\n")

# Carregar imóveis existentes
try:
    with open("data/processed/mega_final_20250609_210138.json", "r") as f:
        existing = json.load(f)
        existing_urls = {p['url'] for p in existing}
        print(f"✅ {len(existing)} imóveis já coletados\n")
except:
    existing = []
    existing_urls = set()

options = Options()
options.add_argument('--headless')
driver = webdriver.Firefox(options=options)

all_properties = existing.copy()
page = 22  # Começar da 22
errors_count = 0

try:
    while errors_count < 3:
        url = f"https://www.olafranca.com.br/comprar/pagina-{page}/"
        print(f"📄 Página {page}...")
        
        try:
            driver.get(url)
            time.sleep(5)
            
            links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/casa/"], a[href*="/apartamento/"]')
            
            if not links:
                print("❌ Sem mais imóveis")
                break
                
            new_links = []
            for elem in links:
                href = elem.get_attribute('href')
                if href and '/franca/' in href and href not in existing_urls:
                    new_links.append(href)
            
            if not new_links:
                print("   Todos já coletados, próxima página...")
                page += 1
                continue
                
            print(f"   📊 {len(new_links)} novos imóveis")
            
            for i, url in enumerate(new_links):
                try:
                    driver.get(url)
                    time.sleep(3 + random.randint(1, 2))
                    
                    text = driver.find_element(By.TAG_NAME, "body").text
                    data = {'url': url}
                    
                    price_match = re.search(r'R\$\s*([\d\.]+)', text)
                    if price_match:
                        data['price'] = float(price_match.group(1).replace('.', ''))
                    
                    rooms_match = re.search(r'(\d+)\s*quartos?', text, re.I)
                    if rooms_match:
                        data['rooms'] = int(rooms_match.group(1))
                    
                    parts = url.split('/')
                    if 'franca' in parts:
                        idx = parts.index('franca')
                        if idx + 1 < len(parts):
                            data['neighborhood'] = parts[idx + 1].replace('-', ' ').title()
                    
                    if data.get('price', 0) > 0:
                        all_properties.append(data)
                        existing_urls.add(url)
                        print(f"      ✅ {data.get('neighborhood', 'N/A')} - R$ {data.get('price', 0):,.0f}")
                        
                except Exception as e:
                    print(f"      ❌ Erro: {str(e)[:30]}")
            
            page += 1
            errors_count = 0
            time.sleep(8)
            
        except Exception as e:
            print(f"❌ Erro na página: {str(e)[:30]}")
            errors_count += 1
            time.sleep(20)
            
finally:
    driver.quit()
    
    if len(all_properties) > len(existing):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output = f"data/processed/completo_{timestamp}.json"
        
        with open(output, 'w') as f:
            json.dump(all_properties, f, indent=2)
        
        print(f"\n🎉 COLETA COMPLETA!")
        print(f"📊 Total: {len(all_properties)} imóveis")
        print(f"✨ Novos: {len(all_properties) - len(existing)}")
