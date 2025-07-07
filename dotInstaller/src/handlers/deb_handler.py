import subprocess

class DebHandler:
    def install(self, file_path):
        try:
            # Instalar el paquete .deb usando pkexec para diálogo gráfico
            result = subprocess.run([
                'pkexec', 'dpkg', '-i', file_path
            ], capture_output=True, text=True)
            if result.returncode != 0:
                # Intentar corregir dependencias
                subprocess.run(['pkexec', 'apt-get', '-f', 'install', '-y'])
                return False
            # Corregir dependencias si es necesario
            subprocess.run(['pkexec', 'apt-get', '-f', 'install', '-y'])
            return True
        except Exception as e:
            print(f"Error instalando .deb: {e}")
            return False

    def uninstall(self, package_name):
        try:
            # Desinstalar el paquete usando pkexec para diálogo gráfico
            result = subprocess.run([
                'pkexec', 'apt-get', 'remove', '--purge', '-y', package_name
            ], capture_output=True, text=True)
            print(result.stdout)
            print(result.stderr)
            return result.returncode == 0
        except Exception as e:
            print(f"Error desinstalando .deb: {e}")
            return False 