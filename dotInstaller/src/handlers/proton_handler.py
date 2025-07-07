import subprocess
import os

class ProtonHandler:
    def __init__(self):
        self.proton_bin = self.find_proton()
        self.prefix_base = os.path.expanduser('~/.proton-prefixes')
        os.makedirs(self.prefix_base, exist_ok=True)
        self.warned_no_proton = False

    def find_proton(self):
        steam_root = os.path.expanduser('~/.steam/steam/steamapps/common')
        if not os.path.exists(steam_root):
            return None
        for d in os.listdir(steam_root):
            if d.lower().startswith('proton'):
                return os.path.join(steam_root, d, 'proton')
        return None

    def is_proton_installed(self):
        return self.proton_bin and os.path.exists(self.proton_bin)

    def install_steam(self):
        print('[ProtonHandler] Instalando Steam...')
        subprocess.run(['pkexec', 'apt', 'update'])
        subprocess.run(['pkexec', 'apt', 'install', '-y', 'steam'])

    def install_proton(self, ask_user=True):
        # Si no hay Steam/Proton, sugerir instalar Steam y mostrar instrucciones
        if ask_user:
            print('[ProtonHandler] Steam y Proton no detectados. Solicitar al usuario instalar.')
            return 'install_steam_needed'
        self.install_steam()
        return 'steam_installed'

    def prepare_prefix(self, app_name):
        prefix_path = os.path.join(self.prefix_base, app_name)
        os.makedirs(prefix_path, exist_ok=True)
        return prefix_path

    def run_exe(self, exe_path, app_name):
        prefix = self.prepare_prefix(app_name)
        env = os.environ.copy()
        env['STEAM_COMPAT_DATA_PATH'] = prefix
        if not self.proton_bin:
            print('[ProtonHandler] No se encontró Proton. Abortando.')
            return None
        subprocess.run([self.proton_bin, 'run', exe_path], env=env)

    def create_desktop_entry(self, exe_path, app_name):
        prefix = self.prepare_prefix(app_name)
        desktop_dir = os.path.expanduser('~/.local/share/applications')
        os.makedirs(desktop_dir, exist_ok=True)
        desktop_file = os.path.join(desktop_dir, f'{app_name}-proton.desktop')
        content = f'''[Desktop Entry]
Name={app_name} (Proton)
Exec=env STEAM_COMPAT_DATA_PATH={prefix} {self.proton_bin} run "{exe_path}"
Type=Application
Icon=application-x-executable
Categories=Game;Proton;Application;
Terminal=false
'''
        with open(desktop_file, 'w') as f:
            f.write(content)
        os.chmod(desktop_file, 0o755)
        return desktop_file

    def install(self, exe_path, app_name):
        if not self.is_proton_installed():
            return self.install_proton(ask_user=True)
        self.run_exe(exe_path, app_name)
        self.create_desktop_entry(exe_path, app_name)
        print(f'Instalación de {app_name} con Proton completada.')
        return True 