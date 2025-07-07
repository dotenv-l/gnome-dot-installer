#!/usr/bin/env python3
"""
Diagnóstico rápido para AppImages problemáticas
"""

import os
import sys
import subprocess

def quick_test_appimage(appimage_path):
    """Prueba rápida de una AppImage"""
    print(f"\n🔍 Probando: {os.path.basename(appimage_path)}")
    
    # Verificar que existe
    if not os.path.exists(appimage_path):
        print("❌ AppImage no existe")
        return False
    
    # Verificar permisos
    if not os.access(appimage_path, os.X_OK):
        print("❌ AppImage no es ejecutable")
        print("   Ejecuta: chmod +x '" + appimage_path + "'")
        return False
    
    # Verificar arquitectura
    try:
        result = subprocess.run(['file', appimage_path], capture_output=True, text=True)
        print(f"📋 Tipo: {result.stdout.strip()}")
    except:
        print("⚠️  No se pudo verificar el tipo de archivo")
    
    # Probar ejecución
    env = os.environ.copy()
    env['APPIMAGE'] = appimage_path
    env['APPIMAGE_EXTRACT_AND_RUN'] = '1'
    env['DESKTOPINTEGRATION'] = '0'
    
    try:
        print("🚀 Probando ejecución...")
        result = subprocess.run(
            [appimage_path, '--version'], 
            capture_output=True, 
            text=True, 
            timeout=5,
            env=env
        )
        
        if result.returncode == 0:
            print("✅ AppImage funciona correctamente")
            return True
        else:
            print(f"⚠️  AppImage se ejecutó pero con código {result.returncode}")
            if result.stderr:
                print(f"   Error: {result.stderr.strip()}")
            return True  # Consideramos éxito si no falla inmediatamente
            
    except subprocess.TimeoutExpired:
        print("✅ AppImage funciona (timeout esperado para apps GUI)")
        return True
    except Exception as e:
        print(f"❌ Error ejecutando AppImage: {e}")
        return False

def check_desktop_file(app_name):
    """Verifica el archivo .desktop de una aplicación"""
    desktop_dir = os.path.expanduser("~/.local/share/applications")
    
    # Buscar archivo .desktop
    desktop_files = []
    for file in os.listdir(desktop_dir):
        if app_name.lower() in file.lower() and file.endswith('.desktop'):
            desktop_files.append(os.path.join(desktop_dir, file))
    
    if not desktop_files:
        print(f"❌ No se encontró archivo .desktop para {app_name}")
        return False
    
    print(f"📄 Archivos .desktop encontrados: {len(desktop_files)}")
    
    for desktop_file in desktop_files:
        print(f"   - {os.path.basename(desktop_file)}")
        
        # Leer contenido
        try:
            with open(desktop_file, 'r') as f:
                content = f.read()
            
            # Verificar línea Exec
            if 'Exec=' in content:
                exec_line = [line for line in content.split('\n') if line.startswith('Exec=')][0]
                print(f"     Exec: {exec_line}")
                
                # Verificar si está bien configurado
                if 'APPIMAGE=' in exec_line or 'appimagelauncher' in exec_line or 'wrapper.sh' in exec_line:
                    print("     ✅ Configuración correcta")
                else:
                    print("     ❌ Configuración incorrecta")
            else:
                print("     ❌ Falta línea Exec")
                
        except Exception as e:
            print(f"     ❌ Error leyendo archivo: {e}")
    
    return True

def main():
    """Función principal"""
    print("🔧 Diagnóstico Rápido de AppImages")
    print("=" * 50)
    
    # Listar AppImages instaladas
    appimage_dir = os.path.expanduser("~/Applications")
    appimages = []
    
    if os.path.exists(appimage_dir):
        for file in os.listdir(appimage_dir):
            if file.endswith(('.AppImage', '.appimage')):
                appimages.append(os.path.join(appimage_dir, file))
    
    print(f"📱 AppImages encontradas: {len(appimages)}")
    
    # Probar cada AppImage
    results = {}
    for appimage_path in appimages:
        app_name = os.path.basename(appimage_path)
        results[app_name] = quick_test_appimage(appimage_path)
    
    # Verificar archivos .desktop
    print(f"\n📄 Verificando archivos .desktop...")
    
    # Buscar nombres de aplicaciones
    app_names = ['cursor', 'subwaysurfers', 'mpb', 'eaglercraft']
    
    for app_name in app_names:
        check_desktop_file(app_name)
    
    # Resumen
    print(f"\n📊 Resumen:")
    working = [name for name, result in results.items() if result]
    not_working = [name for name, result in results.items() if not result]
    
    print(f"✅ Funcionando: {len(working)}")
    for app in working:
        print(f"   - {app}")
    
    print(f"❌ Con problemas: {len(not_working)}")
    for app in not_working:
        print(f"   - {app}")
    
    if not_working:
        print(f"\n💡 Para reparar:")
        print("   1. Ejecuta: python3 fix_appimages.py")
        print("   2. Verifica permisos: chmod +x ~/Applications/*.AppImage")
        print("   3. Reinicia tu sesión de escritorio")

if __name__ == "__main__":
    main() 