# Servidor de Detección de Emociones

Este proyecto proporciona una API REST para la detección de emociones en imágenes utilizando un modelo YOLO entrenado.

## 🚀 Características

- **API REST**: Endpoints para detección de emociones
- **Múltiples formatos**: Soporte para archivos de imagen y base64
- **CORS habilitado**: Compatible con aplicaciones móviles y web
- **Configuración para Render**: Listo para despliegue en la nube
- **Logging**: Registro detallado de operaciones
- **Manejo de errores**: Respuestas de error estructuradas

## 📋 Requisitos

- Python 3.9+
- Modelo YOLO entrenado (`best.pt`)
- Dependencias listadas en `requirements.txt`

## 🛠️ Instalación Local

1. **Clonar el repositorio**:
```bash
git clone <tu-repositorio>
cd <tu-repositorio>
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Ejecutar el servidor**:
```bash
python app.py
```

El servidor estará disponible en `http://localhost:5000`

## 🌐 Despliegue en Render

1. **Subir a GitHub**: Asegúrate de que tu código esté en un repositorio de GitHub

2. **Conectar con Render**:
   - Ve a [Render Dashboard](https://dashboard.render.com)
   - Crea un nuevo "Web Service"
   - Conecta tu repositorio de GitHub
   - **Importante**: En la configuración del servicio:
     - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
     - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
     - **Python Version**: `3.11.7`

3. **Configuración automática**: Los archivos `render.yaml`, `Procfile` y `runtime.txt` están configurados

## 📡 Endpoints de la API

### 1. Health Check
```http
GET /health
```
**Respuesta**:
```json
{
  "status": "healthy",
  "message": "Servidor de detección de emociones funcionando correctamente"
}
```

### 2. Detección de Emociones (Principal)
```http
POST /detect
```

**Parámetros de consulta**:
- `confidence` (opcional): Umbral de confianza (0.0-1.0, default: 0.25)
- `draw_boxes` (opcional): Dibujar cajas en la imagen (true/false, default: false)

**Formato de entrada**:
- **Archivo**: `multipart/form-data` con campo `image`
- **Base64**: JSON con campo `image_base64`

**Ejemplo con archivo**:
```bash
curl -X POST \
  -F "image=@tu_imagen.jpg" \
  "https://tu-servidor.onrender.com/detect?confidence=0.3&draw_boxes=true"
```

**Ejemplo con base64**:
```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -d '{"image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ..."}' \
  "https://tu-servidor.onrender.com/detect"
```

**Respuesta**:
```json
{
  "success": true,
  "detections": [
    {
      "class_id": 0,
      "class_name": "feliz",
      "confidence": 0.85,
      "box": [100, 150, 200, 250]
    }
  ],
  "total_detections": 1,
  "image_with_boxes": "data:image/png;base64,..." // Solo si draw_boxes=true
}
```

### 3. Detección con Guardado de Archivo
```http
POST /detect_file
```
Similar a `/detect` pero guarda las imágenes en el servidor.

### 4. Descarga de Archivos
```http
GET /download/<filename>
```
Descarga archivos procesados desde la carpeta `uploads/`.

## 📱 Integración con Apps Móviles

### Android (Kotlin)
```kotlin
// Ejemplo de petición con archivo
val file = File("path/to/image.jpg")
val requestBody = MultipartBody.Builder()
    .setType(MultipartBody.FORM)
    .addFormDataPart("image", file.name, 
        RequestBody.create("image/*".toMediaTypeOrNull(), file))
    .build()

val request = Request.Builder()
    .url("https://tu-servidor.onrender.com/detect?confidence=0.3")
    .post(requestBody)
    .build()
```

### iOS (Swift)
```swift
// Ejemplo de petición con archivo
let imageData = UIImage(named: "image")?.jpegData(compressionQuality: 0.8)
let boundary = UUID().uuidString

var request = URLRequest(url: URL(string: "https://tu-servidor.onrender.com/detect?confidence=0.3")!)
request.httpMethod = "POST"
request.setValue("multipart/form-data; boundary=\(boundary)", forHTTPHeaderField: "Content-Type")

var body = Data()
body.append("--\(boundary)\r\n".data(using: .utf8)!)
body.append("Content-Disposition: form-data; name=\"image\"; filename=\"image.jpg\"\r\n".data(using: .utf8)!)
body.append("Content-Type: image/jpeg\r\n\r\n".data(using: .utf8)!)
body.append(imageData!)
body.append("\r\n--\(boundary)--\r\n".data(using: .utf8)!)

request.httpBody = body
```

## 🔧 Configuración Avanzada

### Variables de Entorno
- `PORT`: Puerto del servidor (Render lo establece automáticamente)
- `FLASK_ENV`: Entorno de Flask (development/production)

### Personalización del Modelo
Para usar un modelo diferente, modifica la variable `MODEL_PATH` en `app.py`:
```python
MODEL_PATH = 'tu_modelo.pt'
```

## 📊 Monitoreo y Logs

El servidor incluye logging detallado que puedes ver en:
- **Local**: Consola donde ejecutas el servidor
- **Render**: Dashboard de Render > Logs

## 🚨 Manejo de Errores

El servidor devuelve códigos de estado HTTP apropiados:
- `200`: Operación exitosa
- `400`: Error en los datos de entrada
- `404`: Recurso no encontrado
- `500`: Error interno del servidor

## 📝 Notas Importantes

1. **Tamaño de archivos**: Render tiene límites en el tamaño de archivos
2. **Timeout**: Las peticiones tienen un timeout de 120 segundos
3. **Workers**: Configurado para 1 worker para evitar conflictos de memoria
4. **Modelo**: Asegúrate de que `best.pt` esté en el repositorio

## 🔧 Solución de Problemas

### Error: "Service Root Directory is missing"
Si ves este error en Render:
1. **Verifica la estructura del repositorio**: Asegúrate de que todos los archivos estén en la raíz del repositorio
2. **Configuración manual**: En Render, configura manualmente:
   - **Build Command**: `pip install --upgrade pip && pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --timeout 120`
   - **Python Version**: `3.11.7`
3. **Reinicia el servicio**: Después de cambiar la configuración, reinicia el servicio

### Error: "Build failed" con Pillow o dependencias
Si hay errores de build con Pillow u otras dependencias:
1. **Usa versiones específicas**: Cambia el Build Command a: `pip install --upgrade pip && pip install -r requirements-stable.txt`
2. **Verifica la versión de Python**: Asegúrate de usar Python 3.11.7
3. **Limpia el cache**: En Render, ve a "Settings" > "Clear build cache"

### Error: "Module not found"
Si hay errores de módulos:
1. Verifica que `requirements.txt` esté actualizado
2. Asegúrate de que el modelo `best.pt` esté en el repositorio
3. Revisa los logs de Render para más detalles

## 🤝 Contribución

1. Fork el proyecto
2. Crea una rama para tu feature
3. Commit tus cambios
4. Push a la rama
5. Abre un Pull Request

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. 