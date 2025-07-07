import subprocess
import shutil
import os

class ScriptHandler:
    def install(self, file_path):
        try:
            # Hacer ejecutable el script
            os.chmod(file_path, 0o755)
            # Usar firejail si está disponible
            if shutil.which('firejail'):
                cmd = ['firejail', '--noprofile', file_path]
            else:
                cmd = [file_path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            print(result.stdout)
            print(result.stderr)
            return result.returncode == 0
        except Exception as e:
            print(f"Error ejecutando script: {e}")
            return False

    def uninstall(self, file_path):
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
            # Eliminar .desktop si existe
            desktop_name = os.path.splitext(os.path.basename(file_path))[0] + ".desktop"
            desktop_path = os.path.expanduser(f"~/.local/share/applications/{desktop_name}")
            if os.path.exists(desktop_path):
                os.remove(desktop_path)
            return True
        except Exception as e:
            print(f"Error desinstalando script: {e}")
            return False 