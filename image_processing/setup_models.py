import os
import requests
import logging
from pathlib import Path
import time

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

def download_file(url, filepath, chunk_size=8192):
    """Download com progresso"""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get('content-length', 0))
    
    downloaded = 0
    start_time = time.time()
    
    with open(filepath, 'wb') as f:
        for chunk in response.iter_content(chunk_size=chunk_size):
            if chunk:
                f.write(chunk)
                downloaded += len(chunk)
                
                # Mostrar progresso
                if total_size > 0:
                    percent = (downloaded / total_size) * 100
                    speed = downloaded / (time.time() - start_time) / 1024 / 1024
                    print(f"\r{percent:.1f}% - {speed:.1f} MB/s", end='')
    
    print()  # Nova linha

def setup_yolo_models():
    """Baixa modelos necessários"""
    models_dir = Path("image_processing/models")
    models_dir.mkdir(exist_ok=True)
    
    models = {
        # YOLOv8 nano (menor e mais rápido)
        'yolov8n.pt': 'https://github.com/ultralytics/assets/releases/download/v8.0.0/yolov8n.pt',
        # YOLOv8 small (balanço entre velocidade e precisão)
        'yolov8s.pt': 'https://github.com/ultralytics/assets/releases/download/v8.0.0/yolov8s.pt',
    }
    
    for model_name, url in models.items():
        model_path = models_dir / model_name
        
        if model_path.exists():
            logging.info(f"✅ {model_name} já existe")
        else:
            logging.info(f"📥 Baixando {model_name}...")
            try:
                download_file(url, model_path)
                logging.info(f"✅ {model_name} baixado com sucesso!")
            except Exception as e:
                logging.error(f"❌ Erro baixando {model_name}: {e}")

if __name__ == "__main__":
    setup_yolo_models()
