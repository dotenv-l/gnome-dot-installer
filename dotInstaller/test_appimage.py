#!/usr/bin/env python3
"""
Script de prueba para verificar la funcionalidad de AppImages
"""

import os
import sys
import tempfile
import shutil

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.handlers.appimage_handler import AppImageHandler
from src.core.installer import Installer
from src.data.database import init_db, list_installed, remove_app

def create_test_appimage():
    """Crea un AppImage de prueba"""
    # Crear un directorio temporal para el AppImage
    temp_dir = "/tmp/test_appimage"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
    
    # Crear estructura básica de AppImage
    app_dir = os.path.join(temp_dir, "test-app")
    os.makedirs(app_dir)
    
    # Crear AppRun
    apprun_content = """#!/bin/bash
echo "Test AppImage Running"
"""
    with open(os.path.join(app_dir, "AppRun"), "w") as f:
        f.write(apprun_content)
    os.chmod(os.path.join(app_dir, "AppRun"), 0o755)
    
    # Crear archivo .desktop
    desktop_content = """[Desktop Entry]
Name=Test App
Exec=test-app
Icon=test-app
Type=Application
Categories=Utility;
"""
    with open(os.path.join(app_dir, "test-app.desktop"), "w") as f:
        f.write(desktop_content)
    
    # Crear un icono simple
    icon_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="256" height="256" version="1.1" xmlns="http://www.w3.org/2000/svg">
  <rect width="256" height="256" fill="#4CAF50"/>
  <text x="128" y="128" text-anchor="middle" dy=".3em" fill="white" font-size="48">T</text>
</svg>
"""
    with open(os.path.join(app_dir, "test-app.svg"), "w") as f:
        f.write(icon_content)
    
    # Crear el AppImage (simulado)
    appimage_path = os.path.join(temp_dir, "test-app.AppImage")
    shutil.copy2(os.path.join(app_dir, "AppRun"), appimage_path)
    os.chmod(appimage_path, 0o755)
    
    return appimage_path

def test_appimage_handler():
    """Prueba el AppImageHandler"""
    print("🧪 Probando AppImageHandler...")
    
    # Crear AppImage de prueba
    test_appimage = create_test_appimage()
    print(f"📱 AppImage de prueba creado: {test_appimage}")
    
    # Probar instalación
    handler = AppImageHandler()
    print("📦 Instalando AppImage...")
    success = handler.install(test_appimage)
    
    if success:
        print("✅ AppImage instalado correctamente")
        
        # Verificar que se creó el archivo .desktop
        desktop_file = os.path.expanduser("~/.local/share/applications/test-app.AppImage.desktop")
        if os.path.exists(desktop_file):
            print("✅ Archivo .desktop creado")
        else:
            print("❌ Archivo .desktop no encontrado")
        
        # Probar desinstalación
        print("🗑️ Desinstalando AppImage...")
        uninstall_success = handler.uninstall(test_appimage)
        
        if uninstall_success:
            print("✅ AppImage desinstalado correctamente")
        else:
            print("❌ Error al desinstalar AppImage")
    else:
        print("❌ Error al instalar AppImage")

def test_installer():
    """Prueba el instalador completo"""
    print("\n🧪 Probando instalador completo...")
    
    # Inicializar base de datos
    init_db()
    
    # Crear AppImage de prueba
    test_appimage = create_test_appimage()
    
    # Probar instalación
    installer = Installer()
    print("📦 Instalando AppImage con instalador...")
    result = installer.install_file(test_appimage)
    
    if result == True:
        print("✅ AppImage instalado con instalador")
        
        # Listar aplicaciones instaladas
        installed = list_installed()
        print(f"📋 Aplicaciones instaladas: {len(installed)}")
        for app in installed:
            print(f"  - {app[1]} ({app[3]})")
        
        # Probar desinstalación
        if installed:
            app_id = installed[0][0]  # ID de la primera aplicación
            print(f"🗑️ Desinstalando aplicación ID {app_id}...")
            uninstall_result = installer.uninstall_file(app_id)
            
            if uninstall_result:
                print("✅ Aplicación desinstalada correctamente")
            else:
                print("❌ Error al desinstalar aplicación")
    else:
        print(f"❌ Error al instalar AppImage: {result}")

def main():
    """Función principal"""
    print("🚀 Iniciando pruebas de AppImage...")
    
    try:
        test_appimage_handler()
        test_installer()
        print("\n✅ Todas las pruebas completadas")
    except Exception as e:
        print(f"\n❌ Error en las pruebas: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main() 