import subprocess
import os

class WineHandler:
    def __init__(self):
        self.wine_bin = 'wine'
        self.prefix_base = os.path.expanduser('~/.wine-prefixes')
        os.makedirs(self.prefix_base, exist_ok=True)

    def is_wine_installed(self):
        return subprocess.call(['which', self.wine_bin], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0

    def install_wine(self):
        print('Instalando Wine estable...')
        subprocess.run(['pkexec', 'apt', 'update'])
        subprocess.run(['pkexec', 'apt', 'install', '-y', 'wine'], check=True)
        # Intentar instalar winetricks, pero no fallar si no está disponible
        result = subprocess.run(['pkexec', 'apt', 'install', '-y', 'winetricks'])
        if result.returncode != 0:
            print('[WineHandler] winetricks no está disponible en los repositorios. Puedes instalarlo manualmente si lo necesitas.')

    def prepare_prefix(self, app_name):
        prefix_path = os.path.join(self.prefix_base, app_name)
        os.makedirs(prefix_path, exist_ok=True)
        return prefix_path

    def set_windows_version(self, prefix, version):
        # version: win10, win7, win8, etc.
        # Cambia la versión de Windows en el prefix usando winecfg en modo no interactivo
        subprocess.run([self.wine_bin, 'winecfg', '-v', version], env={**os.environ, 'WINEPREFIX': prefix}, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def run_exe(self, exe_path, app_name):
        prefix = self.prepare_prefix(app_name)
        env = os.environ.copy()
        env['WINEPREFIX'] = prefix
        # Intentar con diferentes versiones de Windows si hay error de versión
        versions = ['win10', 'win7', 'win8']
        for version in versions:
            self.set_windows_version(prefix, version)
            print(f'[WineHandler] Probando con versión de Windows: {version}')
            proc = subprocess.run([self.wine_bin, exe_path], env=env, capture_output=True, text=True)
            if 'no es compatible con la versión de Windows' not in proc.stdout + proc.stderr and 'not compatible with the version of Windows' not in proc.stdout + proc.stderr:
                print(f'[WineHandler] Instalación exitosa con versión: {version}')
                return proc
        print('[WineHandler] Ninguna versión de Windows fue compatible. Considera probar manualmente con winecfg.')
        return proc  # Devuelve el último intento

    def create_desktop_entry(self, exe_path, app_name):
        prefix = self.prepare_prefix(app_name)
        desktop_dir = os.path.expanduser('~/.local/share/applications')
        os.makedirs(desktop_dir, exist_ok=True)
        desktop_file = os.path.join(desktop_dir, f'{app_name}-wine.desktop')
        content = f'''[Desktop Entry]
Name={app_name} (Wine)
Exec=env WINEPREFIX={prefix} wine "{exe_path}"
Type=Application
Icon=application-x-executable
Categories=Wine;Application;
Terminal=false
'''
        with open(desktop_file, 'w') as f:
            f.write(content)
        os.chmod(desktop_file, 0o755)
        return desktop_file

    def install(self, exe_path, app_name):
        if not self.is_wine_installed():
            self.install_wine()
        proc = self.run_exe(exe_path, app_name)
        self.create_desktop_entry(exe_path, app_name)
        if proc.returncode == 0:
            print(f'Instalación de {app_name} con Wine completada.')
        else:
            print(f'[WineHandler] Error al instalar {app_name} con Wine. Log:\n{proc.stdout}\n{proc.stderr}')
        return proc.returncode == 0 