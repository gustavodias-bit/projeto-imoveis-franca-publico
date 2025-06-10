import schedule
import time
import subprocess
import logging
from datetime import datetime

class SimpleScheduler:
    def __init__(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def run_scraper(self):
        """Executa o scraper"""
        self.logger.info(f"🚀 Iniciando coleta: {datetime.now()}")
        try:
            subprocess.run(["python", "scrapers/mega_scraper_delay.py"])
            self.logger.info("✅ Coleta concluída")
        except Exception as e:
            self.logger.error(f"❌ Erro na coleta: {e}")
    
    def run_processing(self):
        """Executa processamento"""
        self.logger.info("🔧 Iniciando processamento")
        try:
            subprocess.run(["python", "image_processing/processar_imoveis_completo.py"])
            self.logger.info("✅ Processamento concluído")
        except Exception as e:
            self.logger.error(f"❌ Erro no processamento: {e}")
    
    def setup_schedule(self):
        """Configura agendamento"""
        # Coleta a cada 4 horas
        schedule.every(4).hours.do(self.run_scraper)
        
        # Processamento 30min após coleta
        schedule.every(4).hours.do(
            lambda: time.sleep(1800) or self.run_processing()
        )
        
        # Relatório diário
        schedule.every().day.at("08:00").do(self.daily_report)
    
    def daily_report(self):
        """Gera relatório diário"""
        self.logger.info("📊 Gerando relatório diário")
        # Implementar relatório
    
    def run(self):
        """Executa o scheduler"""
        self.logger.info("⏰ Scheduler iniciado")
        while True:
            schedule.run_pending()
            time.sleep(60)

if __name__ == "__main__":
    scheduler = SimpleScheduler()
    scheduler.setup_schedule()
    print("✅ Scheduler configurado - NÃO EXECUTAR AGORA!")
