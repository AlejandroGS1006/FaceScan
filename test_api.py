#!/usr/bin/env python3
"""
Script de prueba para verificar que la API de detección de emociones funciona correctamente
"""

import requests
import json
import base64
from PIL import Image
import io
import os

# Configuración
BASE_URL = "http://localhost:5000"  # Cambiar a tu URL de Render cuando esté desplegado
TEST_IMAGE = "img_1.png"  # Usar la imagen de prueba existente

def test_health_check():
    """Prueba el endpoint de salud"""
    print("🔍 Probando health check...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code == 200:
            print("✅ Health check exitoso")
            print(f"   Respuesta: {response.json()}")
        else:
            print(f"❌ Health check falló: {response.status_code}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Error en health check: {e}")
        return False

def test_detection_with_file():
    """Prueba la detección con archivo"""
    print("\n🔍 Probando detección con archivo...")
    
    if not os.path.exists(TEST_IMAGE):
        print(f"❌ Imagen de prueba no encontrada: {TEST_IMAGE}")
        return False
    
    try:
        with open(TEST_IMAGE, 'rb') as f:
            files = {'image': f}
            params = {'confidence': 0.25, 'draw_boxes': 'true'}
            
            response = requests.post(f"{BASE_URL}/detect", files=files, params=params)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Detección con archivo exitosa")
                print(f"   Detecciones encontradas: {result.get('total_detections', 0)}")
                if result.get('detections'):
                    for i, detection in enumerate(result['detections']):
                        print(f"   Detección {i+1}: {detection['class_name']} (confianza: {detection['confidence']:.2f})")
                return True
            else:
                print(f"❌ Detección con archivo falló: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Error en detección con archivo: {e}")
        return False

def test_detection_with_base64():
    """Prueba la detección con base64"""
    print("\n🔍 Probando detección con base64...")
    
    if not os.path.exists(TEST_IMAGE):
        print(f"❌ Imagen de prueba no encontrada: {TEST_IMAGE}")
        return False
    
    try:
        # Convertir imagen a base64
        with open(TEST_IMAGE, 'rb') as f:
            image_data = f.read()
            base64_data = base64.b64encode(image_data).decode('utf-8')
        
        payload = {'image_base64': f"data:image/png;base64,{base64_data}"}
        params = {'confidence': 0.25}
        
        response = requests.post(f"{BASE_URL}/detect", json=payload, params=params)
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Detección con base64 exitosa")
            print(f"   Detecciones encontradas: {result.get('total_detections', 0)}")
            return True
        else:
            print(f"❌ Detección con base64 falló: {response.status_code}")
            print(f"   Error: {response.text}")
            return False
    except Exception as e:
        print(f"❌ Error en detección con base64: {e}")
        return False

def test_detection_file_endpoint():
    """Prueba el endpoint de detección con guardado de archivo"""
    print("\n🔍 Probando endpoint de detección con guardado...")
    
    if not os.path.exists(TEST_IMAGE):
        print(f"❌ Imagen de prueba no encontrada: {TEST_IMAGE}")
        return False
    
    try:
        with open(TEST_IMAGE, 'rb') as f:
            files = {'image': f}
            params = {'confidence': 0.25}
            
            response = requests.post(f"{BASE_URL}/detect_file", files=files, params=params)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Detección con guardado exitosa")
                print(f"   Detecciones encontradas: {result.get('total_detections', 0)}")
                if result.get('detected_image'):
                    print(f"   Imagen guardada: {result['detected_image']}")
                return True
            else:
                print(f"❌ Detección con guardado falló: {response.status_code}")
                print(f"   Error: {response.text}")
                return False
    except Exception as e:
        print(f"❌ Error en detección con guardado: {e}")
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("🚀 Iniciando pruebas de la API de detección de emociones")
    print(f"📍 URL base: {BASE_URL}")
    print(f"🖼️  Imagen de prueba: {TEST_IMAGE}")
    print("=" * 50)
    
    tests = [
        test_health_check,
        test_detection_with_file,
        test_detection_with_base64,
        test_detection_file_endpoint
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 50)
    print(f"📊 Resultados: {passed}/{total} pruebas exitosas")
    
    if passed == total:
        print("🎉 ¡Todas las pruebas pasaron! La API está funcionando correctamente.")
    else:
        print("⚠️  Algunas pruebas fallaron. Revisa los errores arriba.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1) 