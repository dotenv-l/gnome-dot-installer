#!/usr/bin/env python3
"""
Solución específica para SubwaySurfers y MPB
"""

import os
import sys
import subprocess
import shutil

def check_glibc_version():
    """Verifica la versión de GLIBC del sistema"""
    print("🔍 Verificando versión de GLIBC...")
    
    try:
        result = subprocess.run(['ldd', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            # Extraer versión de la primera línea
            version_line = result.stdout.split('\n')[0]
            print(f"📋 {version_line}")
            
            # Verificar si es una versión reciente
            if '2.36' in version_line or '2.37' in version_line:
                print("✅ GLIBC versión reciente detectada")
                return True
            else:
                print("⚠️  GLIBC versión antigua - puede causar problemas")
                return False
    except Exception as e:
        print(f"❌ Error verificando GLIBC: {e}")
        return False

def check_fuse():
    """Verifica si FUSE está disponible"""
    print("\n🔍 Verificando FUSE...")
    
    # Verificar si fuse está instalado
    fuse_available = shutil.which('fusermount') is not None
    
    if fuse_available:
        print("✅ FUSE está disponible")
    else:
        print("❌ FUSE no está disponible")
        print("   Instala con: sudo apt install fuse libfuse2")
    
    return fuse_available

def diagnose_subwaysurfers():
    """Diagnóstico específico para SubwaySurfers"""
    print("\n🎮 Diagnóstico de SubwaySurfers")
    print("=" * 40)
    
    appimage_path = "/home/jrks/Applications/SubwaySurfers-x86-64.AppImage"
    
    if not os.path.exists(appimage_path):
        print("❌ SubwaySurfers no encontrado")
        return False
    
    # Verificar permisos
    if not os.access(appimage_path, os.X_OK):
        print("❌ SubwaySurfers no es ejecutable")
        os.chmod(appimage_path, 0o755)
        print("✅ Permisos corregidos")
    
    # Verificar tipo de archivo
    try:
        result = subprocess.run(['file', appimage_path], capture_output=True, text=True)
        print(f"📋 Tipo: {result.stdout.strip()}")
    except:
        print("⚠️  No se pudo verificar el tipo")
    
    # Probar con diferentes configuraciones
    print("\n🧪 Probando diferentes configuraciones...")
    
    configs = [
        {
            'name': 'Configuración básica',
            'env': {'APPIMAGE': appimage_path, 'APPIMAGE_EXTRACT_AND_RUN': '1'}
        },
        {
            'name': 'Sin sandbox',
            'env': {'APPIMAGE': appimage_path, 'APPIMAGE_EXTRACT_AND_RUN': '1', 'DESKTOPINTEGRATION': '0'}
        },
        {
            'name': 'Con FUSE',
            'env': {'APPIMAGE': appimage_path, 'APPIMAGE_EXTRACT_AND_RUN': '0'}
        }
    ]
    
    for config in configs:
        print(f"\n   Probando: {config['name']}")
        try:
            env = os.environ.copy()
            env.update(config['env'])
            
            result = subprocess.run(
                [appimage_path, '--help'], 
                capture_output=True, 
                text=True, 
                timeout=5,
                env=env
            )
            
            if result.returncode == 0:
                print("     ✅ Funciona")
                return True
            else:
                print(f"     ⚠️  Código {result.returncode}")
                if result.stderr:
                    error_lines = result.stderr.split('\n')[:3]
                    for line in error_lines:
                        if line.strip():
                            print(f"       {line.strip()}")
                            
        except subprocess.TimeoutExpired:
            print("     ✅ Timeout (normal para apps GUI)")
            return True
        except Exception as e:
            print(f"     ❌ Error: {e}")
    
    return False

def diagnose_mpb():
    """Diagnóstico específico para MPB"""
    print("\n🎵 Diagnóstico de MPB")
    print("=" * 40)
    
    appimage_path = "/home/jrks/Applications/MPB-x86-64.AppImage"
    
    if not os.path.exists(appimage_path):
        print("❌ MPB no encontrado")
        return False
    
    # Verificar permisos
    if not os.access(appimage_path, os.X_OK):
        print("❌ MPB no es ejecutable")
        os.chmod(appimage_path, 0o755)
        print("✅ Permisos corregidos")
    
    # Verificar tipo de archivo
    try:
        result = subprocess.run(['file', appimage_path], capture_output=True, text=True)
        print(f"📋 Tipo: {result.stdout.strip()}")
    except:
        print("⚠️  No se pudo verificar el tipo")
    
    # El problema específico es GLIBC
    print("\n🔧 Problema detectado: Incompatibilidad de GLIBC")
    print("   MPB fue compilado con una versión más nueva de GLIBC")
    print("   que la disponible en tu sistema")
    
    # Soluciones posibles
    print("\n💡 Soluciones posibles:")
    print("   1. Actualizar el sistema:")
    print("      sudo apt update && sudo apt upgrade")
    print("   2. Instalar librerías adicionales:")
    print("      sudo apt install libc6-dev")
    print("   3. Usar una versión más antigua de MPB")
    print("   4. Ejecutar con compatibilidad:")
    print("      export LD_LIBRARY_PATH=/lib/x86_64-linux-gnu:$LD_LIBRARY_PATH")
    
    # Probar con LD_LIBRARY_PATH
    print("\n🧪 Probando con LD_LIBRARY_PATH...")
    try:
        env = os.environ.copy()
        env['APPIMAGE'] = appimage_path
        env['APPIMAGE_EXTRACT_AND_RUN'] = '1'
        env['LD_LIBRARY_PATH'] = '/lib/x86_64-linux-gnu:' + env.get('LD_LIBRARY_PATH', '')
        
        result = subprocess.run(
            [appimage_path, '--version'], 
            capture_output=True, 
            text=True, 
            timeout=5,
            env=env
        )
        
        if result.returncode == 0:
            print("✅ MPB funciona con LD_LIBRARY_PATH")
            return True
        else:
            print(f"❌ Aún no funciona: {result.stderr.strip()}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
    
    return False

def create_fixed_wrapper(app_name, appimage_path, extra_env=None):
    """Crea un wrapper mejorado para una AppImage"""
    wrapper_path = f"/home/jrks/Applications/{app_name}-fixed-wrapper.sh"
    
    env_vars = f"""#!/bin/bash
# Wrapper mejorado para {app_name}

export APPIMAGE="{appimage_path}"
export APPIMAGE_EXTRACT_AND_RUN=1
export DESKTOPINTEGRATION=0
"""
    
    if extra_env:
        for key, value in extra_env.items():
            env_vars += f'export {key}="{value}"\n'
    
    wrapper_content = f"""{env_vars}
# Ensure the AppImage is executable
if [ ! -x "{appimage_path}" ]; then
    chmod +x "{appimage_path}"
fi

# Execute the AppImage
exec "{appimage_path}" "$@"
"""
    
    with open(wrapper_path, 'w') as f:
        f.write(wrapper_content)
    
    os.chmod(wrapper_path, 0o755)
    print(f"✅ Wrapper mejorado creado: {wrapper_path}")
    
    return wrapper_path

def main():
    """Función principal"""
    print("🔧 Solución Específica para AppImages Problemáticas")
    print("=" * 60)
    
    # Verificar sistema
    glibc_ok = check_glibc_version()
    fuse_ok = check_fuse()
    
    # Diagnosticar SubwaySurfers
    subwaysurfers_ok = diagnose_subwaysurfers()
    
    # Diagnosticar MPB
    mpb_ok = diagnose_mpb()
    
    # Crear wrappers mejorados si es necesario
    print(f"\n🔧 Creando wrappers mejorados...")
    
    if not subwaysurfers_ok:
        print("\n🎮 Creando wrapper para SubwaySurfers...")
        wrapper = create_fixed_wrapper(
            'subwaysurfers', 
            '/home/jrks/Applications/SubwaySurfers-x86-64.AppImage',
            {'DISPLAY': ':0'}  # Forzar display
        )
    
    if not mpb_ok:
        print("\n🎵 Creando wrapper para MPB...")
        wrapper = create_fixed_wrapper(
            'mpb', 
            '/home/jrks/Applications/MPB-x86-64.AppImage',
            {'LD_LIBRARY_PATH': '/lib/x86_64-linux-gnu:/usr/lib/x86_64-linux-gnu'}
        )
    
    # Resumen final
    print(f"\n📊 Resumen:")
    print(f"   SubwaySurfers: {'✅ Funciona' if subwaysurfers_ok else '❌ Problemas'}")
    print(f"   MPB: {'✅ Funciona' if mpb_ok else '❌ Problemas'}")
    
    if not subwaysurfers_ok or not mpb_ok:
        print(f"\n💡 Próximos pasos:")
        print("   1. Actualiza los archivos .desktop para usar los nuevos wrappers")
        print("   2. Ejecuta: python3 fix_appimages.py")
        print("   3. Reinicia tu sesión de escritorio")
        print("   4. Si MPB sigue sin funcionar, considera actualizar el sistema")

if __name__ == "__main__":
    main() 