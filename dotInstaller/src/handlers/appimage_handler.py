import os
import shutil
import subprocess
from pathlib import Path
import tempfile
import json

class AppImageHandler:
    def __init__(self):
        # Directorios estándar para AppImages
        self.appimage_dir = os.path.expanduser("~/Applications")
        self.desktop_dir = os.path.expanduser("~/.local/share/applications")
        self.icon_dir = os.path.expanduser("~/.local/share/icons")
        
        # Crear directorios si no existen
        os.makedirs(self.appimage_dir, exist_ok=True)
        os.makedirs(self.desktop_dir, exist_ok=True)
        os.makedirs(self.icon_dir, exist_ok=True)

    def install(self, file_path):
        """Instala un AppImage en el sistema"""
        try:
            # Verificar AppImageLauncher al inicio
            self.check_appimagelauncher()
            
            # Verificar permisos de ejecución
            if not os.access(file_path, os.X_OK):
                try:
                    os.chmod(file_path, 0o755)
                except Exception as e:
                    msg = (f"El archivo no tiene permisos de ejecución y no se pudo otorgar automáticamente.\n"
                           f"Por favor, otorga permisos manualmente con:\n"
                           f"chmod +x '{file_path}'\n"
                           f"Error: {e}")
                    print(msg)
                    return {"error": msg}
            
            # Extraer información del AppImage
            app_info = self._extract_app_info(file_path)
            if not isinstance(app_info, dict):
                return {"error": f"Error extrayendo información del AppImage: {app_info}"}
            if 'error' in app_info:
                return app_info
            app_name = app_info.get('name', self._get_app_name_from_filename(file_path))
            if not app_name:
                return {"error": f"No se pudo obtener el nombre de la aplicación del AppImage: {file_path}"}
            
            # Copiar AppImage al directorio de aplicaciones
            dest_path = os.path.join(self.appimage_dir, os.path.basename(file_path))
            shutil.copy2(file_path, dest_path)
            
            # Asegurar permisos de ejecución en el archivo copiado
            os.chmod(dest_path, 0o755)
            
            # Crear archivo .desktop
            desktop_file = self._create_desktop_file(dest_path, app_info)
            
            # Actualizar caché de aplicaciones
            self._update_desktop_database()
            
            print(f"AppImage instalado: {app_name} en {dest_path}")
            return True
            
        except Exception as e:
            print(f"Error instalando AppImage: {e}")
            return {"error": f"Error instalando AppImage: {e}"}

    def _is_valid_appimage(self, file_path):
        """Verifica si el archivo es un AppImage válido"""
        try:
            # Verificar magic bytes del AppImage
            with open(file_path, 'rb') as f:
                # Leer los primeros bytes
                header = f.read(4)
                if header[:2] == b'\x7fELF':  # ELF header
                    # Verificar permisos de ejecución
                    if not os.access(file_path, os.X_OK):
                        print("AppImage no tiene permisos de ejecución, añadiendo...")
                        os.chmod(file_path, 0o755)
                    return True
                
                # Buscar signature de AppImage
                f.seek(0)
                content = f.read(1024)
                if b'AppImage' in content or b'appimage' in content:
                    # Verificar permisos de ejecución
                    if not os.access(file_path, os.X_OK):
                        print("AppImage no tiene permisos de ejecución, añadiendo...")
                        os.chmod(file_path, 0o755)
                    return True
                    
            return False
        except Exception as e:
            print(f"Error verificando AppImage: {e}")
            return False

    def _extract_app_info(self, appimage_path):
        """Extrae información del AppImage sin depender de AppImageLauncher"""
        try:
            # Intentar extraer información usando diferentes métodos
            info = {}
            
            # Método 1: Intentar extraer archivos directamente
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    # Intentar extraer archivos usando --appimage-extract
                    env = os.environ.copy()
                    env['APPIMAGE_EXTRACT_AND_RUN'] = '1'
                    
                    result = subprocess.run([appimage_path, '--appimage-extract'], 
                                         cwd=temp_dir, capture_output=True, 
                                         text=True, timeout=30, env=env)
                    
                    if result.returncode == 0:
                        # Buscar archivo .desktop
                        squashfs_root = os.path.join(temp_dir, 'squashfs-root')
                        if os.path.exists(squashfs_root):
                            desktop_files = []
                            for root, dirs, files in os.walk(squashfs_root):
                                for file in files:
                                    if file.endswith('.desktop'):
                                        desktop_files.append(os.path.join(root, file))
                            
                            if desktop_files:
                                # Usar el primer archivo .desktop encontrado
                                desktop_file = desktop_files[0]
                                info = self._parse_desktop_file(desktop_file)
                                print(f"Información extraída del archivo .desktop: {info}")
                        
                except subprocess.TimeoutExpired:
                    print("Timeout al extraer información del AppImage")
                except Exception as e:
                    print(f"Error extrayendo archivos del AppImage: {e}")
            
            # Si no se pudo extraer información, usar el nombre del archivo
            if not info or not info.get('name'):
                app_name = self._get_app_name_from_filename(appimage_path)
                info['name'] = app_name
                info['comment'] = f"{app_name} (AppImage)"
                info['categories'] = 'Application;'
            
            return info
            
        except Exception as e:
            print(f"Error obteniendo información del AppImage: {e}")
            return {"error": f"Error obteniendo información del AppImage: {e}"}

    def _parse_desktop_file(self, desktop_file_path):
        """Parsea un archivo .desktop y extrae información relevante"""
        info = {}
        try:
            with open(desktop_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            for line in content.split('\n'):
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    if key == 'Name':
                        info['name'] = value
                    elif key == 'Comment':
                        info['comment'] = value
                    elif key == 'Icon':
                        info['icon'] = value
                    elif key == 'Categories':
                        info['categories'] = value
                    elif key == 'MimeType':
                        info['mimetype'] = value
                    elif key == 'GenericName':
                        info['generic_name'] = value
                        
        except Exception as e:
            print(f"Error parseando archivo .desktop: {e}")
            
        return info

    def _get_app_name_from_filename(self, appimage_path):
        """Extrae el nombre de la aplicación del nombre del archivo"""
        try:
            base_name = os.path.basename(appimage_path)
            app_name = os.path.splitext(base_name)[0]
            
            # Limpiar el nombre
            app_name = app_name.replace('-', ' ').replace('_', ' ').replace('.', ' ')
            app_name = ' '.join(app_name.split())  # Normalizar espacios
            app_name = app_name.title()  # Capitalizar palabras
            
            return app_name
            
        except Exception as e:
            print(f"Error obteniendo nombre del archivo: {e}")
            return "Unknown App"

    def _extract_icon(self, appimage_path, app_name):
        """Extrae el icono del AppImage"""
        try:
            safe_name = self._make_safe_name(app_name)
            icon_path = os.path.join(self.icon_dir, f"{safe_name}.png")
            
            # Intentar extraer icono
            with tempfile.TemporaryDirectory() as temp_dir:
                try:
                    env = os.environ.copy()
                    env['APPIMAGE_EXTRACT_AND_RUN'] = '1'
                    
                    result = subprocess.run([appimage_path, '--appimage-extract'], 
                                         cwd=temp_dir, capture_output=True, 
                                         text=True, timeout=30, env=env)
                    
                    if result.returncode == 0:
                        squashfs_root = os.path.join(temp_dir, 'squashfs-root')
                        if os.path.exists(squashfs_root):
                            # Buscar iconos comunes
                            icon_extensions = ['.png', '.svg', '.ico', '.xpm']
                            icon_names = ['icon', 'app', app_name.lower(), safe_name.lower()]
                            
                            found_icon = None
                            for root, dirs, files in os.walk(squashfs_root):
                                for file in files:
                                    file_lower = file.lower()
                                    if any(file_lower.endswith(ext) for ext in icon_extensions):
                                        for icon_name in icon_names:
                                            if icon_name in file_lower:
                                                found_icon = os.path.join(root, file)
                                                break
                                        if found_icon:
                                            break
                                if found_icon:
                                    break
                            
                            # Si no se encontró un icono específico, usar el primer icono encontrado
                            if not found_icon:
                                for root, dirs, files in os.walk(squashfs_root):
                                    for file in files:
                                        if any(file.lower().endswith(ext) for ext in icon_extensions):
                                            found_icon = os.path.join(root, file)
                                            break
                                    if found_icon:
                                        break
                            
                            if found_icon:
                                # Verificar que el ícono es válido antes de copiarlo
                                try:
                                    # Intentar abrir el ícono para verificar que es válido
                                    if found_icon.endswith('.png'):
                                        from PIL import Image
                                        with Image.open(found_icon) as img:
                                            img.verify()
                                    # Si llegamos aquí, el ícono es válido
                                    shutil.copy2(found_icon, icon_path)
                                    print(f"Icono extraído: {icon_path}")
                                    return icon_path
                                except Exception as icon_error:
                                    print(f"Ícono inválido encontrado, usando fallback: {icon_error}")
                                
                except Exception as e:
                    print(f"Error extrayendo icono: {e}")
            
            # Si no se pudo extraer un ícono válido, usar un ícono del sistema
            print("Usando ícono del sistema como fallback")
            return None
            
        except Exception as e:
            print(f"Error procesando icono: {e}")
            return None

    def _make_safe_name(self, name):
        """Convierte un nombre en un nombre seguro para archivos"""
        safe_name = name.replace(' ', '-').replace('(', '').replace(')', '').replace('.', '')
        safe_name = ''.join(c for c in safe_name if c.isalnum() or c in '-_')
        return safe_name.lower()

    def _create_desktop_file(self, appimage_path, app_info, icon_path=None):
        """Crea un archivo .desktop mínimo y funcional para el AppImage"""
        app_name = app_info.get('name', self._get_app_name_from_filename(appimage_path)) if isinstance(app_info, dict) else self._get_app_name_from_filename(appimage_path)
        safe_name = self._make_safe_name(app_name)
        name = app_info.get('name', app_name) if isinstance(app_info, dict) else app_name
        comment = app_info.get('comment', f"{app_name} (AppImage)") if isinstance(app_info, dict) else f"{app_name} (AppImage)"
        categories = app_info.get('categories', 'Game;') if isinstance(app_info, dict) else 'Game;'
        icon = safe_name if icon_path else 'application-x-executable'
        
        # Verificar si AppImageLauncher está disponible
        appimagelauncher_available = shutil.which('appimagelauncher-lite') is not None
        
        if appimagelauncher_available:
            # Usar AppImageLauncher para mejor integración
            exec_line = f'Exec=appimagelauncher-lite "{appimage_path}" %U'
        else:
            # Configuración manual con variables de entorno necesarias
            # Usar un script wrapper para mejor compatibilidad
            wrapper_script = self._create_wrapper_script(appimage_path)
            if wrapper_script:
                exec_line = f'Exec="{wrapper_script}" %U'
            else:
                # Fallback: configuración directa con variables de entorno
                exec_line = f'Exec=env APPIMAGE="{appimage_path}" APPIMAGE_EXTRACT_AND_RUN=1 DESKTOPINTEGRATION=0 "{appimage_path}" %U'
        
        desktop_content = f"""[Desktop Entry]
Name={name}
Comment={comment}
{exec_line}
Icon={icon}
Type=Application
Categories={categories}
Terminal=false
StartupWMClass={safe_name}
MimeType=application/x-executable;
X-AppImage-Version=1.0
Keywords=appimage;application;
"""
        desktop_file = os.path.join(self.desktop_dir, f"{safe_name}.desktop")
        try:
            with open(desktop_file, 'w', encoding='utf-8') as f:
                f.write(desktop_content)
            os.chmod(desktop_file, 0o755)
            print(f"Archivo .desktop creado: {desktop_file}")
            return desktop_file
        except Exception as e:
            print(f"Error creando archivo .desktop: {e}")
            return None

    def _create_wrapper_script(self, appimage_path):
        """Crea un script wrapper para ejecutar AppImages con el entorno correcto"""
        try:
            safe_name = self._make_safe_name(os.path.basename(appimage_path))
            wrapper_path = os.path.join(self.appimage_dir, f"{safe_name}-wrapper.sh")
            
            wrapper_content = f"""#!/bin/bash
# Wrapper script for {os.path.basename(appimage_path)}
# This ensures proper environment variables are set

export APPIMAGE="{appimage_path}"
export APPIMAGE_EXTRACT_AND_RUN=1
export DESKTOPINTEGRATION=0

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
            print(f"Script wrapper creado: {wrapper_path}")
            return wrapper_path
            
        except Exception as e:
            print(f"Error creando script wrapper: {e}")
            return None

    def _update_desktop_database(self):
        """Actualiza la base de datos de aplicaciones del sistema"""
        try:
            # Actualizar base de datos de aplicaciones
            subprocess.run(['update-desktop-database', self.desktop_dir], 
                         capture_output=True, timeout=30, check=False)
            
            # Actualizar caché de iconos
            subprocess.run(['gtk-update-icon-cache', '-f', '-t', self.icon_dir], 
                         capture_output=True, timeout=30, check=False)
            
            print("Base de datos de aplicaciones actualizada")
            
        except Exception as e:
            print(f"Advertencia: No se pudo actualizar la base de datos: {e}")

    def uninstall(self, file_path):
        """Desinstala un AppImage del sistema y limpia archivos relacionados"""
        resumen = []
        try:
            # Obtener información del AppImage
            app_info = self._extract_app_info(file_path)
            app_name = app_info.get('name', self._get_app_name_from_filename(file_path))
            safe_name = self._make_safe_name(app_name)
            basename = os.path.basename(file_path)
            # Eliminar el archivo AppImage
            if os.path.exists(file_path):
                os.remove(file_path)
                resumen.append(f"AppImage eliminado: {file_path}")
            else:
                resumen.append(f"AppImage no encontrado: {file_path}")
            # Eliminar archivo .desktop
            desktop_file = os.path.join(self.desktop_dir, f"{safe_name}.desktop")
            if os.path.exists(desktop_file):
                os.remove(desktop_file)
                resumen.append(f"Archivo .desktop eliminado: {desktop_file}")
            else:
                resumen.append("Archivo .desktop no encontrado")
            # Eliminar icono
            icon_file = os.path.join(self.icon_dir, f"{safe_name}.png")
            if os.path.exists(icon_file):
                os.remove(icon_file)
                resumen.append(f"Icono eliminado: {icon_file}")
            else:
                resumen.append("Icono no encontrado")
            # Actualizar caché de aplicaciones
            self._update_desktop_database()
            resumen.append("Base de datos de aplicaciones actualizada")
            # Eliminar registro de la base de datos si existe (por basename)
            try:
                from src.data.database import list_installed, remove_app
                for app in list_installed():
                    _id, name, db_file_path, type_, _ = app
                    if type_ == 'appimage' and os.path.basename(db_file_path) == basename:
                        remove_app(_id)
                        resumen.append(f"Registro de base de datos eliminado: id={_id}")
            except Exception as e:
                resumen.append(f"Error eliminando registro de base de datos: {e}")
            print("\n".join(resumen))
            return True, resumen
        except Exception as e:
            resumen.append(f"Error desinstalando AppImage: {e}")
            print("\n".join(resumen))
            return False, resumen

    def list_installed(self):
        """Lista los AppImages instalados"""
        try:
            installed = []
            if os.path.exists(self.appimage_dir):
                for file in os.listdir(self.appimage_dir):
                    if file.endswith('.AppImage'):
                        file_path = os.path.join(self.appimage_dir, file)
                        app_info = self._extract_app_info(file_path)
                        app_name = app_info.get('name', self._get_app_name_from_filename(file_path))
                        installed.append({
                            'name': app_name,
                            'path': file_path,
                            'info': app_info
                        })
            return installed
        except Exception as e:
            print(f"Error listando AppImages instalados: {e}")
            return []

    def check_appimagelauncher(self):
        """Verifica si AppImageLauncher está disponible y sugiere instalación si no lo está"""
        appimagelauncher_available = shutil.which('appimagelauncher-lite') is not None
        
        if not appimagelauncher_available:
            print("⚠️  AppImageLauncher no está instalado.")
            print("   Para mejor integración de AppImages, considera instalar AppImageLauncher:")
            print("   sudo apt install appimagelauncher")
            print("   o")
            print("   sudo apt install appimagelauncher-lite")
            return False
        else:
            print("✅ AppImageLauncher detectado - usando integración mejorada")
            return True

# Ejemplo de uso
if __name__ == "__main__":
    handler = AppImageHandler()
    
    # Ejemplo de instalación
    # handler.install("/path/to/your/app.AppImage")
    
    # Ejemplo de listado
    # installed = handler.list_installed()
    # for app in installed:
    #     print(f"- {app['name']}: {app['path']}")