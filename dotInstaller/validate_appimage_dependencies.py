#!/usr/bin/env python3
"""
Validador de dependencias para AppImages
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path

# Agregar el directorio src al path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.handlers.appimage_handler import AppImageHandler

def check_system_dependencies():
    """Verifica las dependencias del sistema necesarias para AppImages"""
    print("🔍 Verificando dependencias del sistema...")
    
    dependencies = {
        'fuse': 'libfuse2',
        'glibc': 'libc6',
        'gcc': 'libgcc-s1',
        'stdc++': 'libstdc++6',
        'glib': 'libglib2.0-0',
        'gtk': 'libgtk-3-0',
        'x11': 'libx11-6',
        'xrandr': 'libxrandr2',
        'xss': 'libxss1',
        'nss': 'libnss3',
        'atk': 'libatk1.0-0',
        'cairo': 'libcairo2',
        'pango': 'libpango-1.0-0',
        'gdk': 'libgdk-pixbuf2.0-0',
        'alsa': 'libasound2',
        'pulse': 'libpulse0',
        'dbus': 'libdbus-1-3',
        'udev': 'libudev1',
        'drm': 'libdrm2',
        'gbm': 'libgbm1',
        'xcb': 'libxcb1',
        'xkb': 'libxkbcommon0',
        'wayland': 'libwayland-client0',
        'egl': 'libegl1',
        'gl': 'libgl1',
        'vulkan': 'libvulkan1'
    }
    
    missing = []
    available = []
    
    for dep_name, package_name in dependencies.items():
        try:
            # Verificar si la librería está disponible
            result = subprocess.run(
                ['ldconfig', '-p'], 
                capture_output=True, 
                text=True
            )
            
            if package_name in result.stdout:
                available.append(dep_name)
            else:
                missing.append(dep_name)
                
        except Exception as e:
            print(f"⚠️  Error verificando {dep_name}: {e}")
    
    print(f"✅ Librerías disponibles: {len(available)}")
    print(f"❌ Librerías faltantes: {len(missing)}")
    
    if missing:
        print("\n📦 Librerías faltantes:")
        for dep in missing:
            print(f"   - {dep}")
        
        print("\n💡 Para instalar las dependencias faltantes:")
        print("   sudo apt update")
        print("   sudo apt install -y " + " ".join([dependencies[dep] for dep in missing]))
    
    return missing, available

def extract_appimage_info(appimage_path):
    """Extrae información detallada de una AppImage"""
    print(f"\n🔍 Analizando: {os.path.basename(appimage_path)}")
    
    info = {
        'path': appimage_path,
        'size': os.path.getsize(appimage_path),
        'permissions': oct(os.stat(appimage_path).st_mode)[-3:],
        'executable': os.access(appimage_path, os.X_OK),
        'dependencies': [],
        'architecture': 'unknown',
        'glibc_version': 'unknown'
    }
    
    # Verificar arquitectura
    try:
        result = subprocess.run(
            ['file', appimage_path], 
            capture_output=True, 
            text=True
        )
        if 'x86-64' in result.stdout:
            info['architecture'] = 'x86-64'
        elif 'i386' in result.stdout:
            info['architecture'] = 'i386'
        elif 'arm' in result.stdout:
            info['architecture'] = 'arm'
    except Exception as e:
        print(f"⚠️  Error verificando arquitectura: {e}")
    
    # Extraer y analizar el contenido
    with tempfile.TemporaryDirectory() as temp_dir:
        try:
            env = os.environ.copy()
            env['APPIMAGE_EXTRACT_AND_RUN'] = '1'
            
            result = subprocess.run(
                [appimage_path, '--appimage-extract'], 
                cwd=temp_dir, 
                capture_output=True, 
                text=True, 
                timeout=60,
                env=env
            )
            
            if result.returncode == 0:
                squashfs_root = os.path.join(temp_dir, 'squashfs-root')
                if os.path.exists(squashfs_root):
                    # Buscar archivos ejecutables principales
                    main_executables = []
                    for root, dirs, files in os.walk(squashfs_root):
                        for file in files:
                            file_path = os.path.join(root, file)
                            if os.access(file_path, os.X_OK) and not file.endswith('.so'):
                                main_executables.append(file_path)
                    
                    # Analizar dependencias de los ejecutables principales
                    for exec_path in main_executables[:3]:  # Solo los primeros 3
                        try:
                            result = subprocess.run(
                                ['ldd', exec_path], 
                                capture_output=True, 
                                text=True,
                                timeout=30
                            )
                            
                            if result.returncode == 0:
                                for line in result.stdout.split('\n'):
                                    if '=>' in line and 'not found' in line:
                                        lib_name = line.split('=>')[0].strip()
                                        info['dependencies'].append(lib_name)
                        except Exception as e:
                            print(f"⚠️  Error analizando dependencias de {exec_path}: {e}")
                    
                    # Buscar información de glibc
                    try:
                        result = subprocess.run(
                            ['strings', '-d', main_executables[0] if main_executables else appimage_path], 
                            capture_output=True, 
                            text=True,
                            timeout=30
                        )
                        
                        for line in result.stdout.split('\n'):
                            if 'GLIBC_' in line:
                                info['glibc_version'] = line.strip()
                                break
                    except Exception as e:
                        print(f"⚠️  Error obteniendo versión de glibc: {e}")
                        
        except Exception as e:
            print(f"⚠️  Error extrayendo AppImage: {e}")
    
    return info

def test_appimage_execution(appimage_path, timeout=10):
    """Prueba la ejecución de una AppImage con diagnóstico detallado"""
    print(f"\n🚀 Probando ejecución de: {os.path.basename(appimage_path)}")
    
    # Configurar variables de entorno
    env = os.environ.copy()
    env['APPIMAGE'] = appimage_path
    env['APPIMAGE_EXTRACT_AND_RUN'] = '1'
    env['DESKTOPINTEGRATION'] = '0'
    
    try:
        # Intentar ejecutar con timeout
        result = subprocess.run(
            [appimage_path, '--help'], 
            capture_output=True, 
            text=True, 
            timeout=timeout,
            env=env
        )
        
        if result.returncode == 0:
            print("✅ AppImage se ejecutó correctamente")
            return True, "Éxito"
        else:
            print(f"⚠️  AppImage se ejecutó pero con código de salida {result.returncode}")
            print(f"   stderr: {result.stderr}")
            return False, f"Código de salida: {result.returncode}"
            
    except subprocess.TimeoutExpired:
        print("✅ AppImage se ejecutó correctamente (timeout esperado)")
        return True, "Timeout (normal para apps GUI)"
    except FileNotFoundError:
        return False, "Archivo no encontrado"
    except PermissionError:
        return False, "Error de permisos"
    except Exception as e:
        return False, f"Error: {str(e)}"

def diagnose_appimage(appimage_path):
    """Diagnóstico completo de una AppImage"""
    print(f"\n{'='*60}")
    print(f"🔬 DIAGNÓSTICO COMPLETO: {os.path.basename(appimage_path)}")
    print(f"{'='*60}")
    
    # Información básica
    info = extract_appimage_info(appimage_path)
    
    print(f"\n📋 Información básica:")
    print(f"   Ruta: {info['path']}")
    print(f"   Tamaño: {info['size'] / (1024*1024):.1f} MB")
    print(f"   Permisos: {info['permissions']}")
    print(f"   Ejecutable: {'✅' if info['executable'] else '❌'}")
    print(f"   Arquitectura: {info['architecture']}")
    print(f"   GLIBC: {info['glibc_version']}")
    
    # Dependencias faltantes
    if info['dependencies']:
        print(f"\n📦 Dependencias faltantes detectadas:")
        for dep in set(info['dependencies']):
            print(f"   - {dep}")

        # Mapeo de librerías a paquetes (puedes expandir este diccionario)
        lib_to_pkg = {
            'libX11.so.6': 'libx11-6',
            'libXrandr.so.2': 'libxrandr2',
            'libXss.so.1': 'libxss1',
            'libnss3.so': 'libnss3',
            'libatk-1.0.so.0': 'libatk1.0-0',
            'libcairo.so.2': 'libcairo2',
            'libpango-1.0.so.0': 'libpango-1.0-0',
            'libgdk_pixbuf-2.0.so.0': 'libgdk-pixbuf2.0-0',
            'libasound.so.2': 'libasound2',
            'libpulse.so.0': 'libpulse0',
            'libdbus-1.so.3': 'libdbus-1-3',
            'libudev.so.1': 'libudev1',
            'libdrm.so.2': 'libdrm2',
            'libgbm.so.1': 'libgbm1',
            'libxcb.so.1': 'libxcb1',
            'libxkbcommon.so.0': 'libxkbcommon0',
            'libwayland-client.so.0': 'libwayland-client0',
            'libEGL.so.1': 'libegl1',
            'libGL.so.1': 'libgl1',
            'libvulkan.so.1': 'libvulkan1',
            'libfuse.so.2': 'libfuse2',
            'libglib-2.0.so.0': 'libglib2.0-0',
            'libgtk-3.so.0': 'libgtk-3-0',
            'libstdc++.so.6': 'libstdc++6',
            'libgcc_s.so.1': 'libgcc-s1',
            'libc.so.6': 'libc6',
        }
        install_missing_dependencies(info['dependencies'], lib_to_pkg)
    
    # Prueba de ejecución
    success, message = test_appimage_execution(appimage_path)
    
    print(f"\n🎯 Resultado de la prueba:")
    print(f"   Estado: {'✅ Funciona' if success else '❌ No funciona'}")
    print(f"   Mensaje: {message}")
    
    # Recomendaciones
    print(f"\n💡 Recomendaciones:")
    
    if not info['executable']:
        print("   1. Otorgar permisos de ejecución:")
        print(f"      chmod +x '{appimage_path}'")
    
    if info['dependencies']:
        print("   2. Instalar dependencias faltantes:")
        print("      sudo apt update")
        print("      sudo apt install -y " + " ".join(set(info['dependencies'])))
    
    if not success:
        print("   3. Probar con variables de entorno específicas:")
        print(f"      export APPIMAGE='{appimage_path}'")
        print("      export APPIMAGE_EXTRACT_AND_RUN=1")
        print("      export DESKTOPINTEGRATION=0")
        print(f"      '{appimage_path}'")
    
    return success, info

def install_missing_dependencies(missing_libs, dep_to_pkg_map):
    """Intenta instalar dependencias faltantes usando apt, notificando y pidiendo confirmación al usuario."""
    if not missing_libs:
        print("\n✅ No hay dependencias faltantes para instalar.")
        return

    # Mapear dependencias a paquetes
    pkgs_to_install = []
    unmapped = []
    for dep in missing_libs:
        pkg = dep_to_pkg_map.get(dep)
        if pkg:
            pkgs_to_install.append(pkg)
        else:
            unmapped.append(dep)

    if not pkgs_to_install:
        print("\n❌ No se pudo mapear ninguna dependencia a un paquete del sistema.")
        if unmapped:
            print("Dependencias no mapeadas:")
            for dep in unmapped:
                print(f"   - {dep}")
        return

    print("\n📦 Se instalarán los siguientes paquetes:")
    print("   " + " ".join(pkgs_to_install))
    if unmapped:
        print("\n⚠️  No se pudo mapear a paquete:")
        for dep in unmapped:
            print(f"   - {dep}")

    confirm = input("\n¿Deseas instalar estos paquetes ahora? [s/N]: ").strip().lower()
    if confirm != 's':
        print("❌ Instalación cancelada por el usuario.")
        return

    try:
        print("\n🔑 Solicitando privilegios de superusuario para instalar dependencias...")
        subprocess.run(["sudo", "apt", "update"], check=True)
        subprocess.run(["sudo", "apt", "install", "-y"] + pkgs_to_install, check=True)
        print("\n✅ Dependencias instaladas correctamente.")
    except subprocess.CalledProcessError as e:
        print(f"\n❌ Error instalando dependencias: {e}")

def main():
    """Función principal"""
    print("🔧 Validador de Dependencias para AppImages")
    print("=" * 60)
    
    # Verificar dependencias del sistema
    missing_deps, available_deps = check_system_dependencies()

    # Diccionario de mapeo de dependencias a paquetes
    dependencies = {
        'fuse': 'libfuse2',
        'glibc': 'libc6',
        'gcc': 'libgcc-s1',
        'stdc++': 'libstdc++6',
        'glib': 'libglib2.0-0',
        'gtk': 'libgtk-3-0',
        'x11': 'libx11-6',
        'xrandr': 'libxrandr2',
        'xss': 'libxss1',
        'nss': 'libnss3',
        'atk': 'libatk1.0-0',
        'cairo': 'libcairo2',
        'pango': 'libpango-1.0-0',
        'gdk': 'libgdk-pixbuf2.0-0',
        'alsa': 'libasound2',
        'pulse': 'libpulse0',
        'dbus': 'libdbus-1-3',
        'udev': 'libudev1',
        'drm': 'libdrm2',
        'gbm': 'libgbm1',
        'xcb': 'libxcb1',
        'xkb': 'libxkbcommon0',
        'wayland': 'libwayland-client0',
        'egl': 'libegl1',
        'gl': 'libgl1',
        'vulkan': 'libvulkan1'
    }

    # Intentar instalar dependencias del sistema si faltan
    install_missing_dependencies(missing_deps, dependencies)

    # Listar AppImages instaladas
    appimage_dir = os.path.expanduser("~/Applications")
    appimages = []
    
    if os.path.exists(appimage_dir):
        for file in os.listdir(appimage_dir):
            if file.endswith(('.AppImage', '.appimage')):
                appimages.append(os.path.join(appimage_dir, file))
    
    if not appimages:
        print("\n❌ No se encontraron AppImages instaladas")
        return
    
    print(f"\n📱 AppImages encontradas: {len(appimages)}")
    
    # Diagnosticar cada AppImage
    results = []
    for appimage_path in appimages:
        success, info = diagnose_appimage(appimage_path)
        results.append({
            'path': appimage_path,
            'name': os.path.basename(appimage_path),
            'success': success,
            'info': info
        })
    
    # Resumen final
    print(f"\n{'='*60}")
    print("📊 RESUMEN FINAL")
    print(f"{'='*60}")
    
    working = [r for r in results if r['success']]
    not_working = [r for r in results if not r['success']]
    
    print(f"✅ AppImages funcionando: {len(working)}")
    for app in working:
        print(f"   - {app['name']}")
    
    print(f"\n❌ AppImages con problemas: {len(not_working)}")
    for app in not_working:
        print(f"   - {app['name']}")
    
    if not_working:
        print(f"\n🔧 Para reparar las AppImages con problemas:")
        print("   1. Ejecuta el reparador:")
        print("      python3 fix_appimages.py")
        print("   2. Instala las dependencias faltantes del sistema")
        print("   3. Reinicia tu sesión de escritorio")
    
    print(f"\n💡 Dependencias del sistema:")
    print(f"   Disponibles: {len(available_deps)}")
    print(f"   Faltantes: {len(missing_deps)}")
    
    if missing_deps:
        print(f"\n📦 Para instalar dependencias faltantes:")
        print("   sudo apt update && sudo apt install -y " + " ".join(missing_deps))

if __name__ == "__main__":
    main() 