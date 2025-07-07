import gi
# Especificar versión de GTK antes de importar
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, Gdk, GLib, Pango  # type: ignore
from src.core.installer import Installer
from src.ui.animation_helper import AnimationHelper
import os
import threading
import subprocess

class ManualPanel(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        self.set_margin_top(32)
        self.set_margin_bottom(32)
        self.set_margin_start(64)
        self.set_margin_end(64)
        
        # Inicializar el helper de animaciones
        self.animation_helper = AnimationHelper()
        
        title_label = Gtk.Label(label="📦 Instalador Manual de Paquetes")
        title_label.set_name("manual-title")
        title_label.set_halign(Gtk.Align.CENTER)
        title_label.add_css_class("fade-in")
        
        desc_label = Gtk.Label(label="Instala paquetes .deb, aplicaciones AppImage y ejecutables de Windows (.exe) descargados manualmente.")
        desc_label.set_name("manual-desc")
        desc_label.set_halign(Gtk.Align.CENTER)
        desc_label.add_css_class("slide-in-up")

        compat_label = Gtk.Label(label="Puedes instalar archivos .deb, AppImage y ejecutables de Windows (.exe).\nPara .exe, se recomienda que sean compatibles con Windows 7 o superior.\nNo todas las aplicaciones de Windows funcionarán correctamente bajo Wine o Proton.")
        compat_label.set_name("manual-compat")
        compat_label.set_halign(Gtk.Align.CENTER)
        compat_label.set_justify(Gtk.Justification.CENTER)
        compat_label.set_wrap(True)
        compat_label.set_max_width_chars(60)
        compat_label.add_css_class("hover-lift")
        
        # Sección de arrastrar y soltar
        self.drop_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        self.drop_box.set_halign(Gtk.Align.CENTER)
        self.drop_box.set_valign(Gtk.Align.CENTER)
        self.drop_box.set_size_request(400, 200)
        self.drop_box.set_name("drop-area")
        self.drop_box.add_css_class("hover-glow")
        
        drop_icon = Gtk.Label(label="⬇️")
        drop_icon.set_name("drop-icon")
        
        drop_label = Gtk.Label(label="Arrastra archivos .deb, .AppImage, .exe, .sh o .run aquí")
        drop_label.set_name("drop-label")
        
        self.drop_box.append(drop_icon)
        self.drop_box.append(drop_label)
        
        # Configurar como destino de arrastre
        drop_target = Gtk.DropTarget.new(Gio.File, Gdk.DragAction.COPY)
        drop_target.set_gtypes([Gio.File])
        drop_target.connect("drop", self.on_file_dropped)
        drop_target.connect("enter", self.on_drag_enter)
        drop_target.connect("leave", self.on_drag_leave)
        drop_target.connect("motion", self.on_drag_motion)
        self.drop_box.add_controller(drop_target)
        
        # O botón para seleccionar archivo
        file_btn = Gtk.Button(label="Seleccionar archivo...")
        file_btn.set_name("file-button")
        file_btn.set_halign(Gtk.Align.CENTER)
        file_btn.add_css_class("hover-lift")
        file_btn.connect("clicked", self.on_select_file)
        
        # Estado de instalación
        self.install_status = Gtk.Label(label="")
        self.install_status.set_name("install-status")
        self.install_status.set_halign(Gtk.Align.CENTER)
        
        self.append(title_label)
        self.append(desc_label)
        self.append(compat_label)
        self.append(self.drop_box)
        self.append(file_btn)
        self.append(self.install_status)

    def on_drag_enter(self, drop_target, x, y):
        """Manejar entrada del drag"""
        self.drop_box.set_name("drop-area-active")
        return Gdk.DragAction.COPY

    def on_drag_leave(self, drop_target):
        """Manejar salida del drag"""
        self.drop_box.set_name("drop-area")

    def on_drag_motion(self, drop_target, x, y):
        """Manejar movimiento del drag"""
        return Gdk.DragAction.COPY

    def on_file_dropped(self, drop_target, file, x, y):
        """Manejar archivo soltado"""
        path = file.get_path()
        print(f"Archivo soltado: {path}")  # Debug
        
        if path.endswith('.deb'):
            self.install_deb_file(path)
        elif path.endswith('.AppImage') or path.endswith('.appimage'):
            self.install_appimage_file(path)
        elif path.endswith('.exe'):
            self.install_exe_file(path)
        elif path.endswith('.sh') or path.endswith('.run'):
            self.install_script_file(path)
        else:
            self.install_status.set_label("❌ Solo se admiten archivos .deb, .AppImage, .exe, .sh o .run")
        
        # Restaurar estilo normal
        self.drop_box.set_name("drop-area")
        return True

    def install_script_file(self, file_path):
        """Instalar archivo script (.sh, .run)"""
        if not os.path.exists(file_path):
            self.install_status.set_label("❌ El archivo no existe")
            return
        
        # Usar el AnimationHelper para crear el diálogo
        script_name = os.path.basename(file_path)
        install_dialog, status_label, progress_bar = self.animation_helper.create_animated_progress_dialog(
            f"Instalando {script_name}",
            "El script se está ejecutando...",
            self.get_root()
        )
        
        # Mostrar el diálogo
        install_dialog.show()
        
        # Iniciar animaciones
        self.animation_helper.start_progress_animation(progress_bar)
        
        # Obtener el contenedor de animación para la flecha
        main_box = install_dialog.get_child()
        animation_container = main_box.get_first_child()
        icon_container = animation_container.get_first_child()
        arrow_icon = icon_container.get_first_child().get_next_sibling()
        
        self.animation_helper.start_arrow_animation(arrow_icon)
        
        # Mensajes de estado para scripts
        status_messages = [
            "Preparando instalación...",
            "Verificando permisos...",
            "Ejecutando script...",
            "Configurando aplicación...",
            "Finalizando instalación..."
        ]
        
        self.animation_helper.create_status_updater(status_label, status_messages, 3000)
        
        # Animar la barra de progreso
        def pulse_progress():
            progress_bar.pulse()
            return True
        
        # Animar la flecha
        arrow_pos = 0
        arrow_icons = ["⬇️", "⬇️", "⬇️", "✨", "✨", "✨"]
        
        def animate_arrow():
            nonlocal arrow_pos
            arrow_icon.set_label(arrow_icons[arrow_pos % len(arrow_icons)])
            arrow_pos += 1
            return True
        
        # Actualizar mensajes de estado
        status_messages = [
            "Preparando instalación...",
            "Verificando permisos...",
            "Ejecutando script...",
            "Configurando aplicación...",
            "Finalizando instalación..."
        ]
        
        status_index = 0
        
        def update_status():
            nonlocal status_index
            if status_index < len(status_messages):
                status_label.set_label(status_messages[status_index])
                status_index += 1
                return True
            return False
        
        # Iniciar animaciones
        progress_id = GLib.timeout_add(100, pulse_progress)
        arrow_id = GLib.timeout_add(500, animate_arrow)
        status_id = GLib.timeout_add(3000, update_status)
        
        def install_task():
            try:
                # Actualizar estado
                GLib.idle_add(lambda: status_label.set_label("Ejecutando script...") or False)
                
                # Hacer el script ejecutable
                os.chmod(file_path, 0o755)
                
                # Ejecutar el script
                result = subprocess.run(
                    [file_path],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                # Detener animaciones usando el helper
                self.animation_helper.stop_all_animations()
                
                if result.returncode == 0:
                    # Mostrar resultado exitoso usando el helper
                    GLib.idle_add(self.show_installation_result, True, None, file_path, install_dialog)
                else:
                    # Mostrar error
                    error_msg = result.stderr if result.stderr else "Error desconocido"
                    GLib.idle_add(self.show_installation_result, False, error_msg, file_path, install_dialog)
                    
            except Exception as e:
                # Detener animaciones en caso de error
                self.animation_helper.stop_all_animations()
                GLib.idle_add(self.show_installation_result, False, str(e), file_path, install_dialog)
        
        threading.Thread(target=install_task, daemon=True).start()

    def on_select_file(self, button):
        dialog = Gtk.FileChooserNative(
            title="Seleccionar paquete .deb, AppImage o ejecutable .exe",
            transient_for=self.get_root(),
            action=Gtk.FileChooserAction.OPEN
        )
        filter_deb = Gtk.FileFilter()
        filter_deb.set_name("Paquetes Debian")
        filter_deb.add_pattern("*.deb")
        dialog.add_filter(filter_deb)
        filter_appimage = Gtk.FileFilter()
        filter_appimage.set_name("AppImages")
        filter_appimage.add_pattern("*.AppImage")
        filter_appimage.add_pattern("*.appimage")
        dialog.add_filter(filter_appimage)
        filter_exe = Gtk.FileFilter()
        filter_exe.set_name("Ejecutables de Windows")
        filter_exe.add_pattern("*.exe")
        dialog.add_filter(filter_exe)
        filter_script = Gtk.FileFilter()
        filter_script.set_name("Scripts")
        filter_script.add_pattern("*.sh")
        filter_script.add_pattern("*.run")
        dialog.add_filter(filter_script)
        def on_response(dialog, response):
            if response == Gtk.ResponseType.ACCEPT:
                file = dialog.get_file()
                file_path = file.get_path()
                if file_path.endswith('.deb'):
                    self.install_deb_file(file_path)
                elif file_path.endswith('.AppImage') or file_path.endswith('.appimage'):
                    self.install_appimage_file(file_path)
                elif file_path.endswith('.exe'):
                    self.install_exe_file(file_path)
                elif file_path.endswith('.sh') or file_path.endswith('.run'):
                    self.install_script_file(file_path)
            dialog.destroy()
        dialog.connect('response', on_response)
        dialog.show()

    def install_exe_file(self, exe_path, use_proton=None):
        """Instala un .exe usando Wine o Proton con detección automática y mensajes inteligentes."""
        # Detección automática de tipo de instalador
        exe_lower = exe_path.lower()
        if 'user' in exe_lower and 'vscode' in exe_lower:
            # Detectar instalador User Installer de VSCode
            dialog = Gtk.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Instalador no compatible\n\nEl instalador seleccionado es la versión 'User Installer' de VSCode, que no es compatible con Wine/Proton.\n\nPor favor, descarga la 'System Installer' desde https://code.visualstudio.com/Download y vuelve a intentarlo."
            )
            dialog.connect('response', lambda d, r: d.destroy())
            dialog.show()
            self.install_status.set_label("❌ Instalador User Installer de VSCode no soportado. Usa la System Installer.")
            return
        # Heurística para juegos: si el nombre contiene palabras clave
        game_keywords = ['game', 'launcher', 'steam', 'gog', 'epic', 'setup', 'play', 'run']
        is_game = any(word in exe_lower for word in game_keywords)
        # Selección automática de Proton o Wine
        auto_use_proton = is_game
        # Crear diálogo de progreso
        progress_dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.CANCEL,
            text="Instalando aplicación...\n\nInstalando dependencias y aplicación, por favor espera..."
        )
        cancel_requested = {"value": False}
        def on_cancel(dialog, response):
            cancel_requested["value"] = True
            dialog.destroy()
            self.install_status.set_label("Instalación cancelada por el usuario.")
        progress_dialog.connect('response', on_cancel)
        progress_dialog.show()
        
        def do_install():
            try:
                installer = Installer()
                import io, sys
                old_stdout, old_stderr = sys.stdout, sys.stderr
                sys.stdout = io.StringIO()
                sys.stderr = io.StringIO()
                result = None
                try:
                    result = installer.install_file(exe_path, use_proton=auto_use_proton)
                except Exception as e:
                    result = e
                output = sys.stdout.getvalue() + '\n' + sys.stderr.getvalue()
                sys.stdout, sys.stderr = old_stdout, old_stderr
                if cancel_requested["value"]:
                    return
                def show_result():
                    progress_dialog.destroy()
                    # Manejo especial para Proton: sugerir instalar Steam
                    if result == 'install_steam_needed':
                        dialog = Gtk.MessageDialog(
                            transient_for=self.get_root(),
                            modal=True,
                            message_type=Gtk.MessageType.QUESTION,
                            buttons=Gtk.ButtonsType.YES_NO,
                            text="Se requiere Steam y Proton para instalar juegos de Windows.\n\n¿Deseas instalar Steam automáticamente? Después deberás abrir Steam, ir a la Biblioteca > Herramientas y descargar Proton. Cuando Proton esté instalado, vuelve a intentar la instalación."
                        )
                        def on_response(dialog, response):
                            dialog.destroy()
                            if response == Gtk.ResponseType.YES:
                                import subprocess
                                subprocess.run(['pkexec', 'apt', 'update'])
                                subprocess.run(['pkexec', 'apt', 'install', '-y', 'steam'])
                                info_dialog = Gtk.MessageDialog(
                                    transient_for=self.get_root(),
                                    modal=True,
                                    message_type=Gtk.MessageType.INFO,
                                    buttons=Gtk.ButtonsType.OK,
                                    text="Steam instalado\n\nAbre Steam, ve a la Biblioteca > Herramientas y descarga Proton. Luego vuelve a intentar la instalación del juego."
                                )
                                info_dialog.connect('response', lambda d, r: d.destroy())
                                info_dialog.show()
                                self.install_status.set_label("Steam instalado. Descarga Proton desde Steam y vuelve a intentar.")
                            else:
                                self.install_status.set_label("Instalación cancelada. No se instaló Steam.")
                        dialog.connect('response', on_response)
                        dialog.show()
                        return
                    if result is True:
                        if auto_use_proton:
                            self.install_status.set_label(f"✅ Juego instalado con Proton: {os.path.basename(exe_path)}")
                        else:
                            self.install_status.set_label(f"✅ Aplicación instalada con Wine: {os.path.basename(exe_path)}")
                    else:
                        version_error = False
                        userpf_error = False
                        if output:
                            for line in output.splitlines():
                                if "no es compatible con la versión de Windows" in line or "This program is not compatible with the version of Windows" in line:
                                    version_error = True
                                if "Failed to expand shell folder constant" in line or "userpf" in line:
                                    userpf_error = True
                        error_msg = f"❌ Error al instalar {os.path.basename(exe_path)}: {result}\n\n"
                        if version_error:
                            error_msg += "\nLa aplicación parece requerir una versión diferente de Windows. Puedes intentar cambiar la versión de Windows en Wine usando 'winecfg' y seleccionando Windows 7, 8 o 10."
                        if userpf_error:
                            error_msg += "\nEl instalador de Windows requiere rutas especiales (como 'Program Files') que no están disponibles en Wine por defecto. Puedes intentar instalar winetricks o probar con otra versión de Wine."
                        error_msg += f"\n\nLog de instalación:\n{output[-2000:] if len(output) > 2000 else output}"
                        error_dialog = Gtk.MessageDialog(
                            transient_for=self.get_root(),
                            modal=True,
                            message_type=Gtk.MessageType.ERROR,
                            buttons=Gtk.ButtonsType.OK,
                            text="Error durante la instalación\n\n" + error_msg
                        )
                        def on_response(dialog, response):
                            dialog.destroy()
                        error_dialog.connect('response', on_response)
                        error_dialog.show()
                        self.install_status.set_label(error_msg)
                GLib.idle_add(show_result)
            except Exception as e:
                def show_error():
                    progress_dialog.destroy()
                    self.install_status.set_label(f"❌ Error inesperado: {e}")
                GLib.idle_add(show_error)
        threading.Thread(target=do_install, daemon=True).start()

    def install_deb_file(self, file_path):
        """Instalar archivo .deb con animación"""
        if not os.path.exists(file_path):
            self.install_status.set_label("❌ El archivo no existe")
            return
        
        # Crear ventana de instalación con animación
        install_dialog = Gtk.Window()
        install_dialog.set_title("Instalando paquete")
        install_dialog.set_transient_for(self.get_root())
        install_dialog.set_modal(True)
        install_dialog.set_default_size(450, 350)
        
        # Contenedor principal
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)
        
        # Sección de animación
        animation_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        animation_box.set_halign(Gtk.Align.CENTER)
        
        # Animación de instalación
        package_name = os.path.basename(file_path)
        
        # Contenedor para la animación de paquete
        package_animation = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        package_animation.set_halign(Gtk.Align.CENTER)
        
        # Icono de paquete
        package_icon = Gtk.Label(label="��")
        package_icon.set_name("install-package-icon")
        
        # Flecha animada
        arrow_icon = Gtk.Label(label="⬇️")
        arrow_icon.set_name("install-arrow-icon")
        
        # Icono de sistema
        system_icon = Gtk.Label(label="💻")
        system_icon.set_name("install-system-icon")
        
        package_animation.append(package_icon)
        package_animation.append(arrow_icon)
        package_animation.append(system_icon)
        
        # Spinner para mostrar actividad
        spinner = Gtk.Spinner()
        spinner.set_size_request(32, 32)
        spinner.start()
        
        animation_box.append(package_animation)
        animation_box.append(spinner)
        
        # Información de instalación
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        info_box.set_halign(Gtk.Align.CENTER)
        
        # Título
        title_label = Gtk.Label(label=f"Instalando {package_name}")
        title_label.set_name("install-title")
        
        # Descripción
        desc_label = Gtk.Label(label="El paquete se está instalando en el sistema...")
        desc_label.set_name("install-desc")
        
        info_box.append(title_label)
        info_box.append(desc_label)
        
        # Barra de progreso
        progress_bar = Gtk.ProgressBar()
        progress_bar.set_pulse_step(0.05)
        progress_bar.set_margin_top(8)
        progress_bar.set_margin_bottom(8)
        progress_bar.set_size_request(-1, 10)
        progress_bar.set_name("install-progress")
        
        # Estado actual
        status_label = Gtk.Label(label="Preparando instalación...")
        status_label.set_name("install-status")
        
        # Ensamblar interfaz
        main_box.append(animation_box)
        main_box.append(info_box)
        main_box.append(progress_bar)
        main_box.append(status_label)
        
        install_dialog.set_child(main_box)
        install_dialog.show()
        
        # Animar la barra de progreso
        def pulse_progress():
            progress_bar.pulse()
            return True
        
        # Animar la flecha
        arrow_pos = 0
        arrow_icons = ["⬇️", "⬇️", "⬇️", "✨", "✨", "✨"]
        
        def animate_arrow():
            nonlocal arrow_pos
            arrow_icon.set_label(arrow_icons[arrow_pos % len(arrow_icons)])
            arrow_pos += 1
            return True
        
        # Actualizar mensajes de estado
        status_messages = [
            "Preparando instalación...",
            "Extrayendo archivos...",
            "Configurando paquete...",
            "Instalando dependencias...",
            "Registrando aplicación...",
            "Finalizando instalación..."
        ]
        
        status_index = 0
        
        def update_status():
            nonlocal status_index
            if status_index < len(status_messages):
                status_label.set_label(status_messages[status_index])
                status_index += 1
                return True
            return False
        
        # Iniciar animaciones
        progress_id = GLib.timeout_add(100, pulse_progress)
        arrow_id = GLib.timeout_add(500, animate_arrow)
        status_id = GLib.timeout_add(3500, update_status)
        
        def install_task():
            try:
                # Actualizar estado
                GLib.idle_add(lambda: status_label.set_label("Instalando paquete...") or False)
                
                result = subprocess.run(
                    ['pkexec', 'dpkg', '-i', file_path],
                    capture_output=True,
                    text=True,
                    timeout=300
                )
                
                if result.returncode == 0:
                    # Actualizar estado
                    GLib.idle_add(lambda: status_label.set_label("Resolviendo dependencias...") or False)
                    
                    # Resolver dependencias
                    subprocess.run(
                        ['pkexec', 'apt-get', 'install', '-f', '-y'],
                        capture_output=True,
                        text=True,
                        timeout=300
                    )
                    
                    # Detener animaciones de forma segura
                    try:
                        if progress_id > 0:
                            GLib.source_remove(progress_id)
                    except:
                        pass
                    try:
                        if arrow_id > 0:
                            GLib.source_remove(arrow_id)
                    except:
                        pass
                    try:
                        if status_id > 0:
                            GLib.source_remove(status_id)
                    except:
                        pass
                    
                    # Mostrar resultado
                    GLib.idle_add(self.on_install_complete, True, None, file_path, install_dialog)
                else:
                    # Detener animaciones de forma segura
                    try:
                        if progress_id > 0:
                            GLib.source_remove(progress_id)
                    except:
                        pass
                    try:
                        if arrow_id > 0:
                            GLib.source_remove(arrow_id)
                    except:
                        pass
                    try:
                        if status_id > 0:
                            GLib.source_remove(status_id)
                    except:
                        pass
                    
                    GLib.idle_add(self.on_install_complete, False, result.stderr, file_path, install_dialog)
            except Exception as e:
                # Detener animaciones en caso de error de forma segura
                try:
                    if progress_id > 0:
                        GLib.source_remove(progress_id)
                except:
                    pass
                try:
                    if arrow_id > 0:
                        GLib.source_remove(arrow_id)
                except:
                    pass
                try:
                    if status_id > 0:
                        GLib.source_remove(status_id)
                except:
                    pass
                
                GLib.idle_add(self.on_install_complete, False, str(e), file_path, install_dialog)
        
        threading.Thread(target=install_task, daemon=True).start()

    def install_appimage_file(self, file_path):
        """Instalar archivo AppImage con animación"""
        if not os.path.exists(file_path):
            self.install_status.set_label("❌ El archivo no existe")
            return

        # Crear ventana de instalación con animación mejorada
        install_dialog = Gtk.Window()
        install_dialog.set_title("Instalando AppImage")
        install_dialog.set_transient_for(self.get_root())
        install_dialog.set_modal(True)
        install_dialog.set_default_size(500, 400)
        install_dialog.set_name("install-dialog")

        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)

        animation_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        animation_box.set_halign(Gtk.Align.CENTER)

        app_name = os.path.basename(file_path)
        app_animation = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        app_animation.set_halign(Gtk.Align.CENTER)
        app_icon = Gtk.Label(label="📱")
        app_icon.set_name("install-app-icon")
        arrow_icon = Gtk.Label(label="⬇️")
        arrow_icon.set_name("install-arrow-icon")
        system_icon = Gtk.Label(label="💻")
        system_icon.set_name("install-system-icon")
        app_animation.append(app_icon)
        app_animation.append(arrow_icon)
        app_animation.append(system_icon)
        spinner = Gtk.Spinner()
        spinner.set_size_request(32, 32)
        spinner.start()
        animation_box.append(app_animation)
        animation_box.append(spinner)

        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        info_box.set_halign(Gtk.Align.CENTER)
        title_label = Gtk.Label(label=f"Instalando {app_name}")
        title_label.set_name("install-title")
        desc_label = Gtk.Label(label="La aplicación AppImage se está instalando...")
        desc_label.set_name("install-desc")
        info_box.append(title_label)
        info_box.append(desc_label)

        progress_bar = Gtk.ProgressBar()
        progress_bar.set_pulse_step(0.05)
        progress_bar.set_margin_top(8)
        progress_bar.set_margin_bottom(8)
        progress_bar.set_size_request(-1, 10)
        progress_bar.set_name("install-progress")
        status_label = Gtk.Label(label="Preparando instalación...")
        status_label.set_name("install-status")

        main_box.append(animation_box)
        main_box.append(info_box)
        main_box.append(progress_bar)
        main_box.append(status_label)
        install_dialog.set_child(main_box)
        install_dialog.show()

        def pulse_progress():
            progress_bar.pulse()
            return True
        arrow_pos = 0
        arrow_icons = ["⬇️", "⬇️", "⬇️", "✨", "✨", "✨"]
        def animate_arrow():
            nonlocal arrow_pos
            arrow_icon.set_label(arrow_icons[arrow_pos % len(arrow_icons)])
            arrow_pos += 1
            return True
        status_messages = [
            "Preparando instalación...",
            "Extrayendo AppImage...",
            "Copiando archivos...",
            "Creando acceso directo...",
            "Extrayendo icono...",
            "Finalizando instalación..."
        ]
        status_index = 0
        def update_status():
            nonlocal status_index
            if status_index < len(status_messages):
                status_label.set_label(status_messages[status_index])
                status_index += 1
                return True
            return False
        progress_id = GLib.timeout_add(100, pulse_progress)
        arrow_id = GLib.timeout_add(500, animate_arrow)
        status_id = GLib.timeout_add(3000, update_status)

        def do_install():
            def install_task():
                try:
                    GLib.idle_add(lambda: status_label.set_label("Instalando AppImage...") or False)
                    installer = Installer()
                    result = installer.install_file(file_path)
                    print('DEBUG RESULT:', result)
                    # Detener animaciones de forma segura
                    try:
                        if progress_id > 0:
                            GLib.source_remove(progress_id)
                    except:
                        pass
                    try:
                        if arrow_id > 0:
                            GLib.source_remove(arrow_id)
                    except:
                        pass
                    try:
                        if status_id > 0:
                            GLib.source_remove(status_id)
                    except:
                        pass
                    if isinstance(result, dict):
                        if result.get("status") == "huérfano_detectado":
                            GLib.idle_add(self.confirm_orphan_cleanup, result, file_path, install_dialog)
                            return
                        # Si es un dict pero no es huérfano, lo tratamos como error
                        GLib.idle_add(self.on_install_complete, False, str(result), file_path, install_dialog)
                    elif result == True:
                        GLib.idle_add(self.on_install_complete, True, None, file_path, install_dialog)
                    else:
                        GLib.idle_add(self.on_install_complete, False, result, file_path, install_dialog)
                except Exception as e:
                    # Detener animaciones de forma segura
                    try:
                        if progress_id > 0:
                            GLib.source_remove(progress_id)
                    except:
                        pass
                    try:
                        if arrow_id > 0:
                            GLib.source_remove(arrow_id)
                    except:
                        pass
                    try:
                        if status_id > 0:
                            GLib.source_remove(status_id)
                    except:
                        pass
                    GLib.idle_add(self.on_install_complete, False, str(e), file_path, install_dialog)
            threading.Thread(target=install_task, daemon=True).start()
        do_install()

    def show_installation_result(self, success, error_msg, file_path, install_dialog=None):
        """Manejar finalización de instalación usando AnimationHelper"""
        # Actualizar el estado en el panel de instalación manual
        if success:
            self.install_status.set_label(f"✅ {os.path.basename(file_path)} instalado correctamente")
            
            # Mostrar notificación
            notification = Gio.Notification.new("Instalación completada")
            notification.set_body(f"El paquete {os.path.basename(file_path) or 'paquete'} se instaló correctamente")
            self.get_root().get_application().send_notification("install-complete", notification)
            
            # Si tenemos diálogo de instalación, mostrar animación de éxito usando el helper
            if install_dialog:
                install_dialog.destroy()  # Cerrar diálogo de progreso
                success_dialog = self.animation_helper.create_success_dialog(
                    os.path.basename(file_path),
                    self.get_root()
                )
                success_dialog.show()
                
                # Agregar efecto de confeti
                self.animation_helper.create_confetti_effect(success_dialog.get_child())
        else:
            self.install_status.set_label(f"❌ Error al instalar: {error_msg}")
            
            # Si tenemos diálogo de instalación, mostrar error usando el helper
            if install_dialog:
                install_dialog.destroy()  # Cerrar diálogo de progreso
                error_dialog = self.animation_helper.create_error_dialog(
                    os.path.basename(file_path),
                    error_msg,
                    self.get_root()
                )
                error_dialog.show()
    
    def on_install_complete(self, success, error_msg, file_path, install_dialog=None):
        """Método legacy para compatibilidad - redirige a show_installation_result"""
        self.show_installation_result(success, error_msg, file_path, install_dialog)

    def confirm_orphan_cleanup(self, orphan_info, file_path, install_dialog):
        """Mostrar diálogo de confirmación para limpiar registro huérfano"""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.YES_NO,
            text=f"Se detectó un registro huérfano para '{os.path.basename(file_path)}'.\n\n¿Deseas limpiar la base de datos y archivos relacionados para poder reinstalar?"
        )
        def on_response(dialog, response):
            dialog.destroy()
            if response == Gtk.ResponseType.YES:
                # Limpiar registro y archivos huérfanos
                from src.data.database import remove_app
                from src.handlers.appimage_handler import AppImageHandler
                remove_app(orphan_info["id"])
                handler = AppImageHandler()
                handler.uninstall(file_path)
                self.install_status.set_label("Registro y archivos huérfanos eliminados. Intenta instalar de nuevo.")
                # Cerrar el diálogo de instalación si existe
                if install_dialog:
                    install_dialog.destroy()
            else:
                self.install_status.set_label("Instalación cancelada por el usuario.")
                if install_dialog:
                    install_dialog.destroy()
        dialog.connect('response', on_response)
        dialog.show()
    
    def cleanup(self):
        """Limpia las animaciones cuando se destruye el panel"""
        if hasattr(self, 'animation_helper'):
            self.animation_helper.cleanup()
    
    def do_destroy(self):
        """Método llamado cuando se destruye el widget"""
        self.cleanup()
        super().do_destroy() 