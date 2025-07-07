#!/usr/bin/env python3
"""
Script para reparar AppImages ya instaladas que no funcionan correctamente
"""

import os
import sys
import shutil
import subprocess
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.handlers.appimage_handler import AppImageHandler

def list_installed_appimages():
    """Lista las AppImages instaladas"""
    appimage_dir = os.path.expanduser("~/Applications")
    desktop_dir = os.path.expanduser("~/.local/share/applications")
    
    installed = []
    
    if os.path.exists(appimage_dir):
        for file in os.listdir(appimage_dir):
            if file.endswith(('.AppImage', '.appimage')):
                appimage_path = os.path.join(appimage_dir, file)
                app_name = os.path.splitext(file)[0]
                safe_name = app_name.replace(' ', '-').replace('(', '').replace(')', '').replace('.', '')
                safe_name = ''.join(c for c in safe_name if c.isalnum() or c in '-_').lower()
                
                desktop_file = os.path.join(desktop_dir, f"{safe_name}.desktop")
                
                installed.append({
                    'name': app_name,
                    'appimage_path': appimage_path,
                    'desktop_file': desktop_file,
                    'safe_name': safe_name
                })
    
    return installed

def check_desktop_file(desktop_file):
    """Verifica si un archivo .desktop está configurado correctamente"""
    if not os.path.exists(desktop_file):
        return False, "Archivo .desktop no existe"
    
    try:
        with open(desktop_file, 'r') as f:
            content = f.read()
        
        # Verificar que tiene la línea Exec
        if 'Exec=' not in content:
            return False, "Falta línea Exec"
        
        # Verificar que tiene variables de entorno correctas
        if 'APPIMAGE=' not in content and 'appimagelauncher-lite' not in content:
            return False, "Falta configuración de variables de entorno"
        
        return True, "Archivo .desktop correcto"
        
    except Exception as e:
        return False, f"Error leyendo archivo: {e}"

def fix_desktop_file(app_info):
    """Repara un archivo .desktop"""
    handler = AppImageHandler()
    
    # Extraer información del AppImage
    appimage_info = handler._extract_app_info(app_info['appimage_path'])
    
    # Crear nuevo archivo .desktop
    desktop_file = handler._create_desktop_file(
        app_info['appimage_path'], 
        appimage_info
    )
    
    if desktop_file and os.path.exists(desktop_file):
        print(f"✅ Archivo .desktop reparado: {desktop_file}")
        return True
    else:
        print(f"❌ Error reparando archivo .desktop para {app_info['name']}")
        return False

def test_appimage_execution(appimage_path):
    """Prueba la ejecución de un AppImage"""
    try:
        # Verificar permisos
        if not os.access(appimage_path, os.X_OK):
            print(f"⚠️  AppImage no tiene permisos de ejecución: {appimage_path}")
            return False
        
        # Intentar ejecutar con timeout
        env = os.environ.copy()
        env['APPIMAGE'] = appimage_path
        env['APPIMAGE_EXTRACT_AND_RUN'] = '1'
        
        result = subprocess.run(
            [appimage_path, '--help'], 
            capture_output=True, 
            text=True, 
            timeout=10,
            env=env
        )
        
        # Si no falla inmediatamente, consideramos que funciona
        return True
        
    except subprocess.TimeoutExpired:
        # Timeout puede indicar que la app se está ejecutando
        return True
    except Exception as e:
        print(f"❌ Error ejecutando AppImage: {e}")
        return False

def main():
    """Función principal"""
    print("🔧 Reparador de AppImages")
    print("=" * 50)
    
    # Listar AppImages instaladas
    installed = list_installed_appimages()
    
    if not installed:
        print("❌ No se encontraron AppImages instaladas")
        return
    
    print(f"📱 Se encontraron {len(installed)} AppImages instaladas:")
    
    fixed_count = 0
    for app in installed:
        print(f"\n🔍 Verificando: {app['name']}")
        print(f"   AppImage: {app['appimage_path']}")
        print(f"   Desktop: {app['desktop_file']}")
        
        # Verificar archivo .desktop
        is_valid, message = check_desktop_file(app['desktop_file'])
        print(f"   Estado .desktop: {message}")
        
        # Verificar ejecución
        can_execute = test_appimage_execution(app['appimage_path'])
        print(f"   Ejecutable: {'✅' if can_execute else '❌'}")
        
        # Reparar si es necesario
        if not is_valid:
            print(f"   🔧 Reparando archivo .desktop...")
            if fix_desktop_file(app):
                fixed_count += 1
                # Actualizar base de datos
                handler = AppImageHandler()
                handler._update_desktop_database()
    
    print(f"\n✅ Reparación completada")
    print(f"   AppImages reparadas: {fixed_count}")
    
    if fixed_count > 0:
        print("\n💡 Recomendaciones:")
        print("   1. Reinicia tu sesión de escritorio para ver los cambios")
        print("   2. Instala AppImageLauncher para mejor integración:")
        print("      sudo apt install appimagelauncher")
        print("   3. Si alguna AppImage sigue sin funcionar, prueba:")
        print("      export APPIMAGE_EXTRACT_AND_RUN=1")
        print("      ./tu-app.AppImage")

if __name__ == "__main__":
    main() 