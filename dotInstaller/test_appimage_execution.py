#!/usr/bin/env python3
"""
Script para probar la ejecución de AppImages instalados
"""

import os
import subprocess
import sys

def test_appimage_execution():
    """Prueba la ejecución de AppImages instalados"""
    
    # Ruta del AppImage instalado
    appimage_path = os.path.expanduser("~/Applications/SubwaySurfers-x86-64.AppImage")
    desktop_file = os.path.expanduser("~/.local/share/applications/subwaysurfers-x86-64.desktop")
    
    print("=== Prueba de ejecución de AppImage ===")
    
    # 1. Verificar que el archivo existe
    if not os.path.exists(appimage_path):
        print(f"❌ AppImage no encontrado: {appimage_path}")
        return False
    
    print(f"✅ AppImage encontrado: {appimage_path}")
    
    # 2. Verificar permisos
    if os.access(appimage_path, os.X_OK):
        print("✅ AppImage tiene permisos de ejecución")
    else:
        print("❌ AppImage NO tiene permisos de ejecución")
        return False
    
    # 3. Verificar archivo .desktop
    if os.path.exists(desktop_file):
        print(f"✅ Archivo .desktop encontrado: {desktop_file}")
        
        # Leer contenido del .desktop
        with open(desktop_file, 'r') as f:
            content = f.read()
            print("\nContenido del archivo .desktop:")
            print(content)
    else:
        print(f"❌ Archivo .desktop no encontrado: {desktop_file}")
        return False
    
    # 4. Probar ejecución directa del AppImage
    print("\n=== Probando ejecución directa ===")
    try:
        # Usar APPIMAGE_EXTRACT_AND_RUN para evitar que se abra el AppImageLauncher
        env = os.environ.copy()
        env['APPIMAGE_EXTRACT_AND_RUN'] = '1'
        
        result = subprocess.run([appimage_path, '--help'], 
                             capture_output=True, text=True, timeout=10, env=env)
        
        if result.returncode == 0:
            print("✅ AppImage responde a --help")
            print(f"Salida: {result.stdout[:200]}...")
        else:
            print(f"⚠️ AppImage no responde a --help (código: {result.returncode})")
            print(f"Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("⚠️ Timeout al ejecutar AppImage")
    except Exception as e:
        print(f"❌ Error ejecutando AppImage: {e}")
    
    # 5. Probar ejecución a través del .desktop
    print("\n=== Probando ejecución a través de .desktop ===")
    try:
        # Usar gtk-launch para probar el .desktop
        result = subprocess.run(['gtk-launch', 'subwaysurfers-x86-64'], 
                             capture_output=True, text=True, timeout=5)
        
        if result.returncode == 0:
            print("✅ gtk-launch ejecutó el .desktop correctamente")
        else:
            print(f"⚠️ gtk-launch falló (código: {result.returncode})")
            print(f"Error: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("✅ gtk-launch inició la aplicación (timeout esperado)")
    except FileNotFoundError:
        print("⚠️ gtk-launch no está disponible")
    except Exception as e:
        print(f"❌ Error con gtk-launch: {e}")
    
    # 6. Verificar que el .desktop es válido
    print("\n=== Verificando validez del .desktop ===")
    try:
        result = subprocess.run(['desktop-file-validate', desktop_file], 
                             capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Archivo .desktop es válido")
        else:
            print(f"❌ Archivo .desktop NO es válido:")
            print(result.stderr)
            
    except FileNotFoundError:
        print("⚠️ desktop-file-validate no está disponible")
    except Exception as e:
        print(f"❌ Error validando .desktop: {e}")
    
    print("\n=== Fin de pruebas ===")
    return True

if __name__ == "__main__":
    test_appimage_execution() 