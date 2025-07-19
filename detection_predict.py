from ultralytics import YOLO
from PIL.Image import Image as PILImageType  # for type checking
import json

def detect_pil_object(image_pil, model_path="best.pt", conf=0.25):
    """
    Detects objects in a PIL image using a YOLO model.

    Parameters:
        image_pil (PIL.Image.Image): PIL image object.
        model_path (str): Path to the trained YOLO model (.pt file).
        conf (float): Minimum confidence threshold to consider a detection.

    Returns:
        list: List of detected objects with label, confidence, and bounding box.
    """
    if not isinstance(image_pil, PILImageType):
        raise ValueError("The provided image is not a PIL.Image object.")

    model = YOLO(model_path)
    
    results = model(image_pil, conf=conf)

    output = []

    for result in results:
        for box in result.boxes:
            class_id = int(box.cls[0])
            confidence = float(box.conf[0])
            class_name = model.names[class_id]
            x1, y1, x2, y2 = map(float, box.xyxy[0])

            output.append({
                "class_id": class_id,
                "class_name": class_name,
                "confidence": confidence,
                "box": [x1, y1, x2, y2]
            })

    return output

from PIL import ImageDraw, ImageFont
import os
import sys

def carregar_fonte_auto(size=16):
    """
    Tenta carregar uma fonte TTF com o tamanho desejado.
    Se não encontrar uma fonte específica, procura uma fonte genérica do sistema.
    """
    fontes_comuns = []

    if sys.platform.startswith("linux"):
        fontes_comuns = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf",
        ]
    elif sys.platform == "darwin":  # macOS
        fontes_comuns = [
            "/System/Library/Fonts/Supplemental/Arial.ttf",
            "/Library/Fonts/Arial.ttf"
        ]
    elif sys.platform == "win32":  # Windows
        fontes_comuns = [
            "C:/Windows/Fonts/arial.ttf",
            "C:/Windows/Fonts/Calibri.ttf",
        ]

    # Tenta carregar a primeira fonte existente
    for path in fontes_comuns:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    # Última tentativa: procurar por qualquer TTF no sistema
    for root, dirs, files in os.walk("/usr/share/fonts" if sys.platform.startswith("linux") else "C:/Windows/Fonts"):
        for file in files:
            if file.lower().endswith(".ttf"):
                try:
                    return ImageFont.truetype(os.path.join(root, file), size)
                except:
                    continue

    print("⚠️ Nenhuma fonte TTF encontrada, usando fonte padrão (sem controle de tamanho).")
    return ImageFont.load_default()
    
def draw_detections(image_pil, res_list, cor_box=(255, 0, 0), cor_texto=(255, 255, 255), fontsize=24):
    """
    Desenha as detecções na imagem PIL usando os dados de bounding box, classe e confiança.

    Parâmetros:
        image_pil (PIL.Image.Image): Imagem original.
        res_list (list): Lista de detecções retornada por detect_pil_object().
        cor_box (tuple): Cor da caixa em RGB.
        cor_texto (tuple): Cor do texto (classe e confiança) em RGB.

    Retorna:
        PIL.Image.Image: Nova imagem com as detecções desenhadas.
    """
    image_edit = image_pil.copy()
    draw = ImageDraw.Draw(image_edit)

    font = carregar_fonte_auto(size=20)

    for obj in res_list:
        x1, y1, x2, y2 = obj["box"]
        class_name = obj["class_name"]
        confidence = obj["confidence"]

        label = f"{class_name} - {confidence:.2f}"

        # Desenha retângulo
        draw.rectangle([x1, y1, x2, y2], outline=cor_box, width=2)

        # Mede o texto
        text_size = draw.textbbox((x1, y1), label, font=font)
        text_width = text_size[2] - text_size[0]
        text_height = 1.5*(text_size[3] - text_size[1])

        # Fundo do texto
        draw.rectangle([x1, y1, x1 + text_width + 4, y1 + text_height + 4], fill=cor_box)

        # Texto da label
        draw.text((x1 + 2, y1 + 2), label, fill=cor_texto, font=font)

    return image_edit

if __name__ == "__main__":

    from PIL import Image

    image_pil = Image.open("img_1.png").convert("RGB")
    model_path = "best.pt"
    
    res_list = detect_pil_object(image_pil, model_path=model_path, conf=0.25)
    
    image_pil_with_boxes = draw_detections(image_pil, res_list)
    
    #image_pil_with_boxes.show()  # Visualiza
    image_pil_with_boxes.save("img_1.boxes.png")  # Salva imagem com as detecções

