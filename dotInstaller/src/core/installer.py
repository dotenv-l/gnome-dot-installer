from src.handlers.deb_handler import DebHandler
from src.handlers.script_handler import ScriptHandler
from src.data.database import is_installed, register_install, get_app_details, remove_app, list_installed
from src.handlers.appimage_handler import AppImageHandler
from src.handlers.wine_handler import WineHandler
from src.handlers.proton_handler import ProtonHandler
import os

class Installer:
    def __init__(self):
        self.deb_handler = DebHandler()
        self.script_handler = ScriptHandler()
        self.appimage_handler = AppImageHandler()
        self.wine_handler = WineHandler()
        self.proton_handler = ProtonHandler()

    def install_file(self, file_path, use_proton=None):
        # Verificar si ya está registrado
        if is_installed(file_path):
            # Buscar en la base de datos el registro
            installed = list_installed()
            for app in installed:
                _id, name, db_file_path, type_, _ = app
                if db_file_path == file_path and type_ == 'appimage':
                    # Si el archivo no existe, retornar mensaje especial para que la UI pregunte al usuario
                    if not os.path.exists(file_path):
                        return {"status": "huérfano_detectado", "id": _id, "file_path": file_path, "name": name}
                    else:
                        return 'already_installed'
        if file_path.endswith('.deb'):
            success = self.deb_handler.install(file_path)
            if success:
                name = os.path.basename(file_path)
                register_install(name, file_path, 'deb')
            return success
        elif file_path.endswith('.sh') or file_path.endswith('.run'):
            success = self.script_handler.install(file_path)
            if success:
                name = os.path.basename(file_path)
                register_install(name, file_path, 'script')
            return success
        elif file_path.endswith('.AppImage') or file_path.endswith('.appimage'):
            success = self.appimage_handler.install(file_path)
            if success == True:
                name = os.path.basename(file_path)
                register_install(name, file_path, 'appimage')
            return success
        elif file_path.endswith('.exe'):
            name = os.path.splitext(os.path.basename(file_path))[0]
            if use_proton:
                self.proton_handler.install(file_path, name)
                register_install(name, file_path, 'proton')
                return True
            else:
                self.wine_handler.install(file_path, name)
                register_install(name, file_path, 'wine')
                return True
        else:
            raise NotImplementedError("Solo se soportan archivos .deb, .sh, .run, .AppImage y .exe en esta versión.")

    def uninstall_file(self, app_id):
        app = get_app_details(app_id)
        if not app:
            return False
        _id, name, file_path, type_, install_date = app
        success = False
        if type_ == 'deb':
            # Se asume que el nombre del paquete es el nombre sin extensión
            package_name = os.path.splitext(name)[0]
            success = self.deb_handler.uninstall(package_name)
        elif type_ == 'script':
            success = self.script_handler.uninstall(file_path)
        elif type_ == 'appimage':
            success = self.appimage_handler.uninstall(file_path)
        if success:
            remove_app(app_id)
        return success 