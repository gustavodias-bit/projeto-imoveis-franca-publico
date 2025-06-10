"""
Preparação do analisador de condição de imóveis
Pronto para usar quando o scraper terminar
"""
import cv2
import numpy as np
from pathlib import Path
import json
import logging

class PropertyConditionAnalyzer:
    def __init__(self):
        self.setup_logging()
        self.quality_weights = {
            'brightness': 0.2,
            'contrast': 0.2,
            'sharpness': 0.3,
            'color_vibrancy': 0.3
        }
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def analyze_image_quality(self, image_path):
        """Analisa qualidade técnica da imagem"""
        try:
            img = cv2.imread(str(image_path))
            if img is None:
                return None
                
            # Converter para RGB
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            
            # Análises
            brightness = np.mean(img_rgb)
            contrast = np.std(img_rgb)
            
            # Detecção de desfoque (Laplacian)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            
            # Score de qualidade (0-10)
            quality_score = min(10, (
                (brightness / 255) * 3 +
                (contrast / 100) * 3 +
                (laplacian_var / 100) * 4
            ))
            
            return {
                'brightness': float(brightness),
                'contrast': float(contrast),
                'sharpness': float(laplacian_var),
                'quality_score': round(quality_score, 2)
            }
            
        except Exception as e:
            self.logger.error(f"Erro analisando imagem: {e}")
            return None
    
    def prepare_for_yolo(self, image_path, output_path):
        """Prepara imagem para detecção YOLO"""
        img = cv2.imread(str(image_path))
        if img is None:
            return False
            
        # Redimensionar se muito grande
        height, width = img.shape[:2]
        if width > 1920:
            scale = 1920 / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            img = cv2.resize(img, (new_width, new_height))
            
        cv2.imwrite(str(output_path), img)
        return True

# Criar instância para teste
analyzer = PropertyConditionAnalyzer()
print("✅ Analisador de condição preparado!")
print("📁 Pronto para processar imagens quando o scraper terminar")
