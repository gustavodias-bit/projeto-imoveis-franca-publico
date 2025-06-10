import cv2
import numpy as np
from ultralytics import YOLO
from pathlib import Path
import logging
import requests
from PIL import Image
import io

class LogoRemovalPipeline:
    def __init__(self):
        self.models_dir = Path("image_processing/models")
        self.temp_dir = Path("image_processing/temp")
        self.output_dir = Path("image_processing/outputs")
        
        # Criar diretórios
        self.temp_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        
        # Carregar YOLO
        self.yolo_model = YOLO(self.models_dir / 'yolov8n.pt')
        
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def download_image(self, url, filename):
        """Baixa imagem da URL"""
        try:
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                img = Image.open(io.BytesIO(response.content))
                img.save(self.temp_dir / filename)
                return True
        except Exception as e:
            self.logger.error(f"Erro baixando {url}: {e}")
        return False
    
    def detect_text_regions(self, image_path):
        """Detecta regiões com texto/logos"""
        img = cv2.imread(str(image_path))
        if img is None:
            return []
        
        # Detectar com YOLO
        results = self.yolo_model(img, conf=0.25)
        
        text_regions = []
        for r in results:
            boxes = r.boxes
            if boxes is not None:
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    text_regions.append({
                        'bbox': [int(x1), int(y1), int(x2), int(y2)],
                        'confidence': float(box.conf[0])
                    })
        
        return text_regions
    
    def remove_watermarks(self, image_path, output_path):
        """Remove watermarks usando inpainting"""
        img = cv2.imread(str(image_path))
        if img is None:
            return False
        
        # Detectar regiões suspeitas
        height, width = img.shape[:2]
        
        # Máscaras para cantos (onde geralmente ficam logos)
        mask = np.zeros((height, width), dtype=np.uint8)
        
        # Canto superior esquerdo
        mask[0:100, 0:200] = 255
        # Canto superior direito  
        mask[0:100, width-200:width] = 255
        # Canto inferior esquerdo
        mask[height-100:height, 0:200] = 255
        # Canto inferior direito
        mask[height-100:height, width-200:width] = 255
        
        # Aplicar inpainting
        result = cv2.inpaint(img, mask, 3, cv2.INPAINT_TELEA)
        
        cv2.imwrite(str(output_path), result)
        return True

print("✅ Sistema de remoção de logos criado!")
