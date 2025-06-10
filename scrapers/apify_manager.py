import os
import time
import logging
from apify_client import ApifyClient
from dotenv import load_dotenv
from typing import Dict, List, Optional

load_dotenv('config/.env')

class ApifyManager:
    def __init__(self):
        self.client = ApifyClient(os.getenv('APIFY_TOKEN'))
        self.setup_logging()
        
    def setup_logging(self):
        # Criar diretório de logs se não existir
        os.makedirs('data/logs', exist_ok=True)
        
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('data/logs/apify.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def list_actors(self):
        """Lista actors disponíveis"""
        try:
            actors = list(self.client.actors().list().items)
            self.logger.info(f"📋 Encontrados {len(actors)} actors")
            return actors
        except Exception as e:
            self.logger.error(f"Erro listando actors: {e}")
            return []
    
    def run_crawler(self, url: str, actor_id: str = "aYG0l9s7dbB7j3gbS"):
        """Executa o website-content-crawler"""
        try:
            self.logger.info(f"🚀 Iniciando crawler para: {url}")
            
            # Input para o actor
            run_input = {
                "startUrls": [{"url": url}],
                "maxCrawlDepth": 1,
                "maxCrawlPages": 10
            }
            
            # Executar
            run = self.client.actor(actor_id).call(run_input=run_input)
            self.logger.info(f"✅ Crawler iniciado - Run ID: {run['id']}")
            
            return run
            
        except Exception as e:
            self.logger.error(f"❌ Erro no crawler: {e}")
            return None

# Teste
if __name__ == "__main__":
    manager = ApifyManager()
    print("🚀 ApifyManager pronto!")
    print("\n📋 Actors disponíveis:")
    actors = manager.list_actors()
    for actor in actors:
        print(f"  - {actor.get('name')} (ID: {actor.get('id')})")
