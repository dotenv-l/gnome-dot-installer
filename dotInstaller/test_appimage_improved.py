#!/usr/bin/env python3
"""
Script de prueba para verificar las mejoras en el manejo de AppImages
"""

import os
import sys
import tempfile
import shutil

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.handlers.appimage_handler import AppImageHandler

def test_appimagelauncher_detection():
    """Prueba la detección de AppImageLauncher"""
    print("🧪 Probando detección de AppImageLauncher...")
    
    handler = AppImageHandler()
    has_appimagelauncher = handler.check_appimagelauncher()
    
    if has_appimagelauncher:
        print("✅ AppImageLauncher está disponible")
    else:
        print("⚠️  AppImageLauncher no está disponible")
        print("   Esto puede causar problemas con algunas AppImages")
    
    return has_appimagelauncher

def test_desktop_file_creation():
    """Prueba la creación mejorada de archivos .desktop"""
    print("\n🧪 Probando creación mejorada de archivos .desktop...")
    
    # Crear un AppImage de prueba
    test_appimage = "/tmp/test-improved.AppImage"
    with open(test_appimage, 'w') as f:
        f.write("#!/bin/bash\necho 'Test AppImage'")
    os.chmod(test_appimage, 0o755)
    
    handler = AppImageHandler()
    
    # Información de prueba
    app_info = {
        'name': 'Test Improved App',
        'comment': 'Test application for improved AppImage handling',
        'categories': 'Utility;Development;'
    }
    
    # Crear archivo .desktop
    desktop_file = handler._create_desktop_file(test_appimage, app_info)
    
    if desktop_file and os.path.exists(desktop_file):
        print("✅ Archivo .desktop creado correctamente")
        
        # Leer y mostrar el contenido
        with open(desktop_file, 'r') as f:
            content = f.read()
            print("\n📋 Contenido del archivo .desktop:")
            print(content)
        
        # Verificar que la línea Exec es correcta
        if 'APPIMAGE=' in content or 'appimagelauncher-lite' in content or 'wrapper.sh' in content:
            print("✅ Línea Exec configurada correctamente")
        else:
            print("❌ Línea Exec no configurada correctamente")
        
        # Limpiar
        os.remove(desktop_file)
    else:
        print("❌ Error creando archivo .desktop")
    
    # Limpiar archivo de prueba
    os.remove(test_appimage)

def test_icon_handling():
    """Prueba el manejo mejorado de íconos"""
    print("\n🧪 Probando manejo mejorado de íconos...")
    
    handler = AppImageHandler()
    
    # Probar con un AppImage que no existe (debería usar fallback)
    test_appimage = "/tmp/nonexistent.AppImage"
    app_name = "Test App"
    
    icon_path = handler._extract_icon(test_appimage, app_name)
    
    if icon_path is None:
        print("✅ Manejo de íconos funciona correctamente (usando fallback)")
    else:
        print("⚠️  Se extrajo un ícono inesperado")

def main():
    """Función principal de pruebas"""
    print("🚀 Iniciando pruebas de mejoras en AppImage...")
    
    # Prueba 1: Detección de AppImageLauncher
    test_appimagelauncher_detection()
    
    # Prueba 2: Creación de archivos .desktop
    test_desktop_file_creation()
    
    # Prueba 3: Manejo de íconos
    test_icon_handling()
    
    print("\n✅ Todas las pruebas completadas")
    print("\n💡 Recomendaciones:")
    print("   1. Instala AppImageLauncher para mejor integración:")
    print("      sudo apt install appimagelauncher")
    print("   2. Si tienes problemas con AppImages específicas, prueba:")
    print("      export APPIMAGE_EXTRACT_AND_RUN=1")
    print("      ./tu-app.AppImage")

if __name__ == "__main__":
    main() 