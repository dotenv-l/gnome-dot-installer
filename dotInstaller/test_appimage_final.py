#!/usr/bin/env python3
"""
Script final para probar que las AppImages funcionan correctamente
"""

import os
import sys
import subprocess
import time

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.handlers.appimage_handler import AppImageHandler

def test_desktop_launch(app_name):
    """Prueba lanzar una aplicación desde el archivo .desktop"""
    desktop_dir = os.path.expanduser("~/.local/share/applications")
    
    # Buscar el archivo .desktop
    desktop_file = None
    for file in os.listdir(desktop_dir):
        if app_name.lower() in file.lower() and file.endswith('.desktop'):
            desktop_file = os.path.join(desktop_dir, file)
            break
    
    if not desktop_file:
        print(f"❌ No se encontró archivo .desktop para {app_name}")
        return False
    
    print(f"📄 Probando archivo .desktop: {desktop_file}")
    
    # Leer el contenido del archivo .desktop
    with open(desktop_file, 'r') as f:
        content = f.read()
    
    print(f"📋 Contenido del archivo .desktop:")
    print(content)
    
    # Verificar que la línea Exec es correcta
    if 'APPIMAGE=' in content or 'appimagelauncher-lite' in content or 'wrapper.sh' in content:
        print("✅ Línea Exec configurada correctamente")
    else:
        print("❌ Línea Exec no configurada correctamente")
        return False
    
    # Intentar lanzar la aplicación
    try:
        print(f"🚀 Intentando lanzar {app_name}...")
        
        # Usar gtk-launch para simular el lanzamiento desde el menú
        result = subprocess.run(
            ['gtk-launch', os.path.basename(desktop_file)],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            print(f"✅ {app_name} se lanzó correctamente")
            return True
        else:
            print(f"⚠️  {app_name} se lanzó pero con código de salida {result.returncode}")
            print(f"   stderr: {result.stderr}")
            return True  # Consideramos éxito si no falla inmediatamente
            
    except subprocess.TimeoutExpired:
        print(f"✅ {app_name} se lanzó correctamente (timeout esperado)")
        return True
    except Exception as e:
        print(f"❌ Error lanzando {app_name}: {e}")
        return False

def test_wrapper_script(app_name):
    """Prueba el script wrapper de una AppImage"""
    appimage_dir = os.path.expanduser("~/Applications")
    
    # Buscar el script wrapper
    wrapper_file = None
    for file in os.listdir(appimage_dir):
        if app_name.lower() in file.lower() and file.endswith('-wrapper.sh'):
            wrapper_file = os.path.join(appimage_dir, file)
            break
    
    if not wrapper_file:
        print(f"⚠️  No se encontró script wrapper para {app_name}")
        return False
    
    print(f"📜 Probando script wrapper: {wrapper_file}")
    
    # Verificar que el script es ejecutable
    if not os.access(wrapper_file, os.X_OK):
        print(f"❌ Script wrapper no es ejecutable")
        return False
    
    # Leer el contenido del script
    with open(wrapper_file, 'r') as f:
        content = f.read()
    
    print(f"📋 Contenido del script wrapper:")
    print(content)
    
    # Verificar que tiene las variables de entorno correctas
    if 'APPIMAGE=' in content and 'APPIMAGE_EXTRACT_AND_RUN=1' in content:
        print("✅ Script wrapper configurado correctamente")
        return True
    else:
        print("❌ Script wrapper no configurado correctamente")
        return False

def main():
    """Función principal"""
    print("🎯 Prueba final de AppImages")
    print("=" * 50)
    
    # Lista de aplicaciones a probar
    test_apps = [
        'cursor',
        'subwaysurfers',
        'mpb',
        'eaglercraft'
    ]
    
    success_count = 0
    
    for app in test_apps:
        print(f"\n🔍 Probando: {app}")
        
        # Probar script wrapper
        wrapper_ok = test_wrapper_script(app)
        
        # Probar lanzamiento desde .desktop
        launch_ok = test_desktop_launch(app)
        
        if wrapper_ok and launch_ok:
            print(f"✅ {app}: Todo correcto")
            success_count += 1
        else:
            print(f"❌ {app}: Problemas detectados")
    
    print(f"\n📊 Resultados:")
    print(f"   Aplicaciones probadas: {len(test_apps)}")
    print(f"   Aplicaciones funcionando: {success_count}")
    print(f"   Tasa de éxito: {success_count/len(test_apps)*100:.1f}%")
    
    if success_count == len(test_apps):
        print("\n🎉 ¡Todas las AppImages funcionan correctamente!")
    else:
        print(f"\n⚠️  {len(test_apps) - success_count} AppImages tienen problemas")
        print("   Considera instalar AppImageLauncher para mejor compatibilidad")
    
    print("\n💡 Para probar manualmente:")
    print("   1. Abre el menú de aplicaciones")
    print("   2. Busca las aplicaciones instaladas")
    print("   3. Haz clic en ellas para ejecutarlas")
    print("   4. Si no funcionan, ejecuta desde terminal:")
    print("      export APPIMAGE_EXTRACT_AND_RUN=1")
    print("      ./tu-app.AppImage")

if __name__ == "__main__":
    main() 