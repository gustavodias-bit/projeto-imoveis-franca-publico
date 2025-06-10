import json
import pandas as pd
import re
from pathlib import Path
import logging

class DataPipeline:
    def __init__(self):
        self.data_dir = Path("data/processed")
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def clean_price(self, price_str):
        """Limpa e converte preço"""
        if isinstance(price_str, (int, float)):
            return float(price_str)
        
        # Remover R$ e espaços
        price_clean = re.sub(r'[^\d,.]', '', str(price_str))
        price_clean = price_clean.replace('.', '').replace(',', '.')
        
        try:
            return float(price_clean)
        except:
            return 0.0
    
    def extract_details(self, title, description=""):
        """Extrai detalhes do imóvel"""
        text = f"{title} {description}".lower()
        
        details = {
            'rooms': 0,
            'bathrooms': 0,
            'garage_spots': 0,
            'suites': 0
        }
        
        # Quartos
        rooms_match = re.search(r'(\d+)\s*(?:quartos?|dorms?|dormitórios?)', text)
        if rooms_match:
            details['rooms'] = int(rooms_match.group(1))
        
        # Banheiros
        bath_match = re.search(r'(\d+)\s*(?:banheiros?|wc)', text)
        if bath_match:
            details['bathrooms'] = int(bath_match.group(1))
        
        # Vagas
        garage_match = re.search(r'(\d+)\s*(?:vagas?|garagem)', text)
        if garage_match:
            details['garage_spots'] = int(garage_match.group(1))
        
        # Suítes
        suite_match = re.search(r'(\d+)\s*suítes?', text)
        if suite_match:
            details['suites'] = int(suite_match.group(1))
        
        return details
    
    def process_properties(self, input_file, output_file):
        """Processa e padroniza propriedades"""
        with open(input_file, 'r') as f:
            properties = json.load(f)
        
        processed = []
        for prop in properties:
            # Limpar preço
            prop['price_clean'] = self.clean_price(prop.get('price', 0))
            
            # Extrair detalhes
            details = self.extract_details(
                prop.get('title', ''),
                prop.get('description', '')
            )
            prop.update(details)
            
            # Adicionar campos calculados
            if prop['price_clean'] > 0 and prop.get('area', 0) > 0:
                prop['price_per_m2'] = prop['price_clean'] / prop['area']
            
            processed.append(prop)
        
        # Salvar processado
        with open(output_file, 'w') as f:
            json.dump(processed, f, ensure_ascii=False, indent=2)
