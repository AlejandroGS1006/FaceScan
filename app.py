from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import io
import base64
from PIL import Image
import logging
from detection_predict import detect_pil_object, draw_detections

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Habilitar CORS para peticiones desde apps móviles

# Configuración
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'bmp'}
MODEL_PATH = 'best.pt'

# Crear carpeta de uploads si no existe
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    """Verificar si el archivo tiene una extensión permitida"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint de salud para verificar que el servidor está funcionando"""
    return jsonify({
        'status': 'healthy',
        'message': 'Servidor de detección de emociones funcionando correctamente'
    })

@app.route('/detect', methods=['POST'])
def detect_emotions():
    """
    Endpoint principal para detección de emociones
    Acepta imágenes en formato multipart/form-data o base64
    """
    try:
        # Verificar si hay archivo en la petición
        if 'image' in request.files:
            file = request.files['image']
            if file.filename == '':
                return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'error': 'Tipo de archivo no permitido'}), 400
            
            # Leer imagen desde archivo
            image_pil = Image.open(file.stream).convert('RGB')
            
        elif 'image_base64' in request.json:
            # Leer imagen desde base64
            image_data = request.json['image_base64']
            if image_data.startswith('data:image'):
                # Remover el prefijo data:image/...;base64,
                image_data = image_data.split(',')[1]
            
            image_bytes = base64.b64decode(image_data)
            image_pil = Image.open(io.BytesIO(image_bytes)).convert('RGB')
            
        else:
            return jsonify({'error': 'Se requiere una imagen (archivo o base64)'}), 400

        # Obtener parámetros opcionales
        confidence = request.args.get('confidence', 0.25, type=float)
        draw_boxes = request.args.get('draw_boxes', 'false').lower() == 'true'
        
        # Realizar detección
        logger.info(f"Realizando detección con confianza: {confidence}")
        detections = detect_pil_object(image_pil, model_path=MODEL_PATH, conf=confidence)
        
        # Preparar respuesta
        response = {
            'success': True,
            'detections': detections,
            'total_detections': len(detections)
        }
        
        # Si se solicita dibujar cajas, generar imagen con detecciones
        if draw_boxes and detections:
            image_with_boxes = draw_detections(image_pil, detections)
            
            # Convertir a base64 para enviar en la respuesta
            img_buffer = io.BytesIO()
            image_with_boxes.save(img_buffer, format='PNG')
            img_str = base64.b64encode(img_buffer.getvalue()).decode()
            
            response['image_with_boxes'] = f"data:image/png;base64,{img_str}"
        
        logger.info(f"Detección completada: {len(detections)} objetos encontrados")
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error en detección: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/detect_file', methods=['POST'])
def detect_emotions_file():
    """
    Endpoint alternativo que guarda la imagen y devuelve la imagen con detecciones
    """
    try:
        if 'image' not in request.files:
            return jsonify({'error': 'No se proporcionó imagen'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No se seleccionó ningún archivo'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({'error': 'Tipo de archivo no permitido'}), 400
        
        # Guardar archivo original
        filename = os.path.join(UPLOAD_FOLDER, file.filename)
        file.save(filename)
        
        # Leer imagen
        image_pil = Image.open(filename).convert('RGB')
        
        # Obtener parámetros
        confidence = request.args.get('confidence', 0.25, type=float)
        
        # Realizar detección
        detections = detect_pil_object(image_pil, model_path=MODEL_PATH, conf=confidence)
        
        # Generar imagen con detecciones
        if detections:
            image_with_boxes = draw_detections(image_pil, detections)
            output_filename = f"detected_{file.filename}"
            output_path = os.path.join(UPLOAD_FOLDER, output_filename)
            image_with_boxes.save(output_path)
            
            return jsonify({
                'success': True,
                'detections': detections,
                'total_detections': len(detections),
                'original_image': filename,
                'detected_image': output_path
            })
        else:
            return jsonify({
                'success': True,
                'detections': [],
                'total_detections': 0,
                'message': 'No se detectaron emociones en la imagen'
            })
            
    except Exception as e:
        logger.error(f"Error en detección de archivo: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/download/<filename>')
def download_file(filename):
    """Endpoint para descargar archivos procesados"""
    try:
        return send_file(os.path.join(UPLOAD_FOLDER, filename), as_attachment=True)
    except FileNotFoundError:
        return jsonify({'error': 'Archivo no encontrado'}), 404

if __name__ == '__main__':
    # Configuración para producción
    port = int(os.environ.get('PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    logger.info(f"Iniciando servidor en puerto {port}")
    app.run(host='0.0.0.0', port=port, debug=debug) 