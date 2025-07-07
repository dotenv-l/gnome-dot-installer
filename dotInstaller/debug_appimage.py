#!/usr/bin/env python3
"""
Script de depuración para AppImage
"""

import os
import sys
from src.data.database import list_installed, remove_app

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.handlers.appimage_handler import AppImageHandler

def test_desktop_creation():
    """Prueba la creación del archivo .desktop"""
    print("🧪 Probando creación de archivo .desktop...")
    
    # Crear un AppImage de prueba simple
    test_file = "/tmp/test-debug.AppImage"
    with open(test_file, 'w') as f:
        f.write("#!/bin/bash\necho 'test'")
    os.chmod(test_file, 0o755)
    
    print(f"📱 Archivo de prueba creado: {test_file}")
    
    # Probar el handler
    handler = AppImageHandler()
    
    # Probar solo la creación del .desktop
    app_name = handler._get_app_name(test_file)
    print(f"📝 Nombre de aplicación: {app_name}")
    
    # Crear el archivo .desktop
    desktop_file = handler._create_desktop_file(test_file, app_name)
    print(f"📄 Archivo .desktop creado: {desktop_file}")
    
    # Verificar que existe
    if os.path.exists(desktop_file):
        print("✅ Archivo .desktop existe")
        with open(desktop_file, 'r') as f:
            content = f.read()
            print("📋 Contenido del archivo .desktop:")
            print(content)
    else:
        print("❌ Archivo .desktop no existe")
    
    # Limpiar
    os.remove(test_file)
    if os.path.exists(desktop_file):
        os.remove(desktop_file)

def print_all():
    print("\nRegistros actuales en la base de datos:")
    for app in list_installed():
        print(app)

def clean_orphan_subway():
    found = False
    print_all()
    for app in list_installed():
        _id, name, file_path, type_, _ = app
        if type_ == 'appimage' and os.path.basename(file_path) == 'SubwaySurfers-x86-64.AppImage':
            print(f"Eliminando registro huérfano: {name} (id={_id}) {file_path}")
            remove_app(_id)
            found = True
    if not found:
        print("No se encontró registro huérfano de SubwaySurfers-x86-64.AppImage.")
    print_all()

if __name__ == "__main__":
    clean_orphan_subway() 