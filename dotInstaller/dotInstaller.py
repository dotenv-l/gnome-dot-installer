"""
Punto de entrada principal para dotInstaller
"""
import gi
from src.ui import MainWindow
from src.core.installer import Installer
from src.data.database import init_db
from gi.repository import Gtk, GLib, Gio, Gdk  # type: ignore
import os

# Hook: Detección de tema del sistema (puedes expandir para cargar CSS oscuro si el sistema lo usa)
def get_system_theme():
    settings = Gtk.Settings.get_default()
    theme_name = settings.get_property('gtk-theme-name') if settings else ''
    return theme_name

# Cargar CSS Material Design mejorado
css_provider = Gtk.CssProvider()
css_path = os.path.join(os.path.dirname(__file__), 'resources', 'material.css')
if os.path.exists(css_path):
    css_provider.load_from_path(css_path)
    Gtk.StyleContext.add_provider_for_display(
        Gdk.Display.get_default(),
        css_provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )

class DotInstallerApp(Gtk.Application):
    def __init__(self):
        super().__init__()
        self.installer = Installer()
        init_db()

    def do_activate(self):
        self.win = MainWindow(self)
        self.win.on_file_dropped = self.on_file_dropped  # Sobrescribir handler
        self.win.on_file_selected = self.on_file_selected
        self.win.present()

    def on_file_dropped(self, drop_target, file, x, y):
        if isinstance(file, Gio.File):
            file_path = file.get_path()
            if file_path and (file_path.endswith('.deb') or file_path.endswith('.sh') or file_path.endswith('.run') or file_path.endswith('.AppImage') or file_path.endswith('.appimage')):
                self._start_install(file_path)
        return True

    def on_file_selected(self, file_path):
        if file_path and (file_path.endswith('.deb') or file_path.endswith('.sh') or file_path.endswith('.run') or file_path.endswith('.AppImage') or file_path.endswith('.appimage')):
            self._start_install(file_path)

    def _start_install(self, file_path):
        self.win.reset_drop_label(f"Instalando: {file_path}")
        self.win.select_button.set_sensitive(False)
        spinner = Gtk.Spinner()
        spinner.start()
        self.win.set_drop_content(spinner)
        GLib.idle_add(self._install_file, file_path, spinner)

    def _install_file(self, file_path, spinner):
        result = self.installer.install_file(file_path)
        spinner.stop()
        self.win.set_drop_content(self.win.drop_label)
        self.win.select_button.set_sensitive(True)
        if result == 'already_installed':
            self._show_notification("El archivo ya está instalado.")
            self.win.reset_drop_label("Ya instalado")
        elif result:
            self._show_notification("Instalación exitosa")
            self.win.reset_drop_label("¡Instalación exitosa!")
            self.win.refresh_apps_list()
        else:
            self._show_notification("Error en la instalación")
            self.win.reset_drop_label("Error en la instalación")
        return False

    def _show_notification(self, message):
        dialog = Gtk.MessageDialog(
            transient_for=self.win,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.show()
        dialog.connect("response", lambda d, r: d.destroy())


def main():
    app = DotInstallerApp()
    app.run()

if __name__ == "__main__":
    main() 