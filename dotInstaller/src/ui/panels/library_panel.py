import gi
# Especificar versión de GTK antes de importar
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gio, Gdk  # type: ignore
from src.data.database import list_installed, get_app_details, remove_app
from src.utils.package_listing import map_packages_to_desktop_entries
import os
import threading
import subprocess
import html
import configparser

class LibraryPanel(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        
        # Header mejorado
        header = self.create_library_header()
        self.append(header)
        
        # Contenedor principal con scroll
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scrolled.set_vexpand(True)
        
        # Lista de aplicaciones
        self.library_listbox = Gtk.ListBox()
        self.library_listbox.set_name("library-listbox")
        self.library_listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        
        scrolled.set_child(self.library_listbox)
        self.append(scrolled)
        
        # Estado
        self.library_apps = []
        self.filtered_apps = []
        self.current_category = "Todas"
        
        # Cargar aplicaciones
        self.load_library_apps()

    def create_library_header(self):
        """Crear header de la biblioteca"""
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        header_box.set_margin_top(32)
        header_box.set_margin_bottom(24)
        header_box.set_margin_start(32)
        header_box.set_margin_end(32)
        
        # Título y estadísticas
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        title_box.set_halign(Gtk.Align.CENTER)
        
        title_label = Gtk.Label(label="📚 Biblioteca de Aplicaciones")
        title_label.set_name("library-title")
        
        self.stats_label = Gtk.Label(label="")
        self.stats_label.set_name("library-stats")
        self.stats_label.set_margin_start(16)
        
        title_box.append(title_label)
        title_box.append(self.stats_label)
        
        # Barra de búsqueda
        search_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        search_box.set_halign(Gtk.Align.CENTER)
        
        self.search_entry = Gtk.SearchEntry()
        self.search_entry.set_size_request(400, -1)
        if hasattr(self.search_entry, 'set_placeholder_text'):
            self.search_entry.set_placeholder_text("Buscar aplicaciones instaladas...")
        elif hasattr(self.search_entry, 'set_placeholder'):
            self.search_entry.set_placeholder("Buscar aplicaciones instaladas...")
        self.search_entry.connect("search-changed", self.on_library_search)
        
        search_box.append(self.search_entry)
        
        # Filtros por categoría
        self.category_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.category_box.set_halign(Gtk.Align.CENTER)
        
        header_box.append(title_box)
        header_box.append(search_box)
        header_box.append(self.category_box)
        
        return header_box

    def load_library_apps(self):
        """Cargar aplicaciones de la biblioteca"""
        # Mostrar loading
        self.show_library_loading()
        
        def load_apps():
            try:
                apps = map_packages_to_desktop_entries()
                # Extraer categorías
                categories = set()
                for app in apps:
                    cats = app.get('categories', '').split(';')
                    for cat in cats:
                        if cat.strip():
                            categories.add(cat.strip())
                
                categories = sorted(list(categories))
                
                GLib.idle_add(self.update_library_apps, apps, categories)
            except Exception as e:
                GLib.idle_add(self.show_library_error, str(e))
        
        threading.Thread(target=load_apps, daemon=True).start()

    def show_library_loading(self):
        """Mostrar indicador de carga"""
        # Limpiar listbox
        while True:
            child = self.library_listbox.get_first_child()
            if child is None:
                break
            self.library_listbox.remove(child)
        
        # Crear loading item
        loading_row = Gtk.ListBoxRow()
        loading_row.set_selectable(False)
        
        loading_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        loading_box.set_halign(Gtk.Align.CENTER)
        loading_box.set_margin_top(48)
        loading_box.set_margin_bottom(48)
        
        spinner = Gtk.Spinner()
        spinner.set_size_request(32, 32)
        spinner.start()
        
        loading_label = Gtk.Label(label="Cargando aplicaciones instaladas...")
        loading_label.set_name("loading-label")
        
        loading_box.append(spinner)
        loading_box.append(loading_label)
        
        loading_row.set_child(loading_box)
        self.library_listbox.append(loading_row)

    def show_library_error(self, error_msg):
        """Mostrar error en la biblioteca"""
        # Limpiar listbox
        while True:
            child = self.library_listbox.get_first_child()
            if child is None:
                break
            self.library_listbox.remove(child)
        
        error_row = Gtk.ListBoxRow()
        error_row.set_selectable(False)
        
        error_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        error_box.set_halign(Gtk.Align.CENTER)
        error_box.set_margin_top(48)
        error_box.set_margin_bottom(48)
        
        error_icon = Gtk.Label(label="⚠️")
        error_icon.set_name("error-icon")
        
        error_title = Gtk.Label(label="Error al cargar aplicaciones")
        error_title.set_name("error-title")
        
        error_detail = Gtk.Label(label=f"Detalles: {error_msg}")
        error_detail.set_name("error-detail")
        
        retry_btn = Gtk.Button(label="Reintentar")
        retry_btn.set_name("retry-button")
        retry_btn.connect("clicked", lambda b: self.load_library_apps())
        
        error_box.append(error_icon)
        error_box.append(error_title)
        error_box.append(error_detail)
        error_box.append(retry_btn)
        
        error_row.set_child(error_box)
        self.library_listbox.append(error_row)

    def update_library_apps(self, apps, categories):
        """Actualizar lista de aplicaciones"""
        self.library_apps = apps
        self.filtered_apps = apps
        
        # Actualizar estadísticas
        self.stats_label.set_label(f"({len(apps)} aplicaciones)")
        
        # Actualizar filtros de categoría
        self.update_category_filters(categories)
        
        # Mostrar aplicaciones
        self.display_library_apps()
        
        return False

    def update_category_filters(self, categories):
        """Actualizar filtros de categoría"""
        # Limpiar filtros actuales
        while True:
            child = self.category_box.get_first_child()
            if child is None:
                break
            self.category_box.remove(child)
        
        # Agregar filtro "Todas"
        all_btn = Gtk.Button(label="Todas")
        all_btn.set_name("category-filter-active" if self.current_category == "Todas" else "category-filter")
        all_btn.connect("clicked", lambda b: self.filter_by_category("Todas"))
        self.category_box.append(all_btn)
        
        # Agregar filtros por categoría
        for category in categories[:6]:  # Limitar a 6 categorías principales
            btn = Gtk.Button(label=category)
            btn.set_name("category-filter-active" if self.current_category == category else "category-filter")
            btn.connect("clicked", lambda b, c=category: self.filter_by_category(c))
            self.category_box.append(btn)

    def filter_by_category(self, category):
        """Filtrar por categoría"""
        self.current_category = category
        self.apply_filters()
        self.update_category_buttons()

    def update_category_buttons(self):
        """Actualizar estado visual de botones de categoría"""
        for child in self.category_box:
            if hasattr(child, 'get_label'):
                if child.get_label() == self.current_category:
                    child.set_name("category-filter-active")
                else:
                    child.set_name("category-filter")

    def on_library_search(self, entry):
        """Filtrar por búsqueda"""
        self.apply_filters()

    def apply_filters(self):
        """Aplicar filtros de búsqueda y categoría"""
        search_text = self.search_entry.get_text().lower()
        
        filtered = []
        for app in self.library_apps:
            # Filtro por texto
            name_match = search_text in app.get('name', '').lower()
            desc_match = search_text in app.get('comment', '').lower()
            text_match = name_match or desc_match
            
            # Filtro por categoría
            if self.current_category == "Todas":
                category_match = True
            else:
                app_categories = app.get('categories', '').split(';')
                category_match = self.current_category in app_categories
            
            if text_match and category_match:
                filtered.append(app)
        
        self.filtered_apps = filtered
        self.display_library_apps()

    def display_library_apps(self):
        """Mostrar aplicaciones en la lista"""
        # Limpiar listbox
        while True:
            child = self.library_listbox.get_first_child()
            if child is None:
                break
            self.library_listbox.remove(child)
        
        if not self.filtered_apps:
            # Mostrar mensaje de no resultados
            empty_row = Gtk.ListBoxRow()
            empty_row.set_selectable(False)
            
            empty_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
            empty_box.set_halign(Gtk.Align.CENTER)
            empty_box.set_margin_top(48)
            empty_box.set_margin_bottom(48)
            
            empty_icon = Gtk.Label(label="📭")
            empty_icon.set_name("empty-icon")
            
            empty_label = Gtk.Label(label="No se encontraron aplicaciones")
            empty_label.set_name("empty-label")
            
            empty_box.append(empty_icon)
            empty_box.append(empty_label)
            
            empty_row.set_child(empty_box)
            self.library_listbox.append(empty_row)
            return
        
        # Crear elementos de lista
        for app in self.filtered_apps:
            row = self.create_library_app_row(app)
            self.library_listbox.append(row)

    def create_library_app_row(self, app):
        """Crear fila para aplicación de biblioteca con diseño mejorado y menú contextual"""
        row = Gtk.ListBoxRow()
        row.set_name("library-app-row")
        
        # Contenedor principal con efecto de elevación
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        main_box.set_margin_top(14)
        main_box.set_margin_bottom(14)
        main_box.set_margin_start(28)
        main_box.set_margin_end(28)
        
        # Contenedor del icono con fondo circular
        icon_frame = Gtk.Box()
        icon_frame.set_size_request(64, 64)
        icon_frame.set_name("app-icon-frame")
        icon_frame.set_valign(Gtk.Align.CENTER)
        
        # Icono mejorado
        icon_path = app.get('icon')
        if icon_path and os.path.exists(icon_path):
            try:
                icon = Gtk.Image.new_from_file(icon_path)
                icon.set_pixel_size(48)
            except:
                icon = Gtk.Label(label="📱")
                icon.set_name("app-icon-fallback")
        else:
            icon = Gtk.Label(label="📱")
            icon.set_name("app-icon-fallback")
        
        icon_frame.append(icon)
        
        # Información de la aplicación con mejor espaciado
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        info_box.set_hexpand(True)
        info_box.set_valign(Gtk.Align.CENTER)
        info_box.set_margin_start(8)
        
        # Nombre con mejor tipografía
        safe_name = html.escape(app.get('name', 'Sin nombre'))
        name_label = Gtk.Label(label=safe_name, xalign=0)
        name_label.set_name("app-name")
        name_label.set_markup(f"<span weight='bold'>{safe_name}</span>")
        
        # Descripción con mejor formato
        desc_text = app.get('comment', 'Sin descripción')
        if len(desc_text) > 90:
            desc_text = desc_text[:90] + "..."
        desc_label = Gtk.Label(label=desc_text, xalign=0)
        desc_label.set_name("app-description")
        desc_label.set_wrap(True)
        desc_label.set_max_width_chars(60)
        
        # Contenedor para metadatos con iconos
        meta_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        meta_box.set_margin_top(4)
        
        # Paquete con icono
        package_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
        package_icon = Gtk.Label(label="📦")
        package_icon.set_name("meta-icon")
        package_text = Gtk.Label(label=app.get('package', 'N/A'))
        package_text.set_name("meta-text")
        package_box.append(package_icon)
        package_box.append(package_text)
        
        meta_box.append(package_box)
        
        # Categoría con icono
        categories = app.get('categories', '').split(';')
        if categories and categories[0]:
            category_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=4)
            category_icon = Gtk.Label(label="🏷️")
            category_icon.set_name("meta-icon")
            category_text = Gtk.Label(label=categories[0])
            category_text.set_name("meta-text")
            category_box.append(category_icon)
            category_box.append(category_text)
            meta_box.append(category_box)
        
        info_box.append(name_label)
        info_box.append(desc_label)
        info_box.append(meta_box)
        
        # Advertencias si es crítico con mejor diseño
        if app.get('essential') or app.get('priority_required'):
            warning_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
            warning_box.set_margin_top(4)
            warning_icon = Gtk.Label(label="⚠️")
            warning_text = Gtk.Label(label="Aplicación crítica del sistema", xalign=0)
            warning_text.set_name("app-warning")
            warning_box.append(warning_icon)
            warning_box.append(warning_text)
            info_box.append(warning_box)
        
        # Ensamblar contenido principal
        main_box.append(icon_frame)
        main_box.append(info_box)
        
        # Configurar menú contextual (clic derecho)
        gesture = Gtk.GestureClick.new()
        gesture.set_button(3)  # Botón derecho
        gesture.connect("pressed", self.on_app_right_click, app)
        row.add_controller(gesture)
        
        # Añadir evento de clic para mostrar detalles
        row.connect("activate", lambda row: self.show_app_info(app))
        
        row.set_child(main_box)
        return row
        
    def on_app_right_click(self, gesture, n_press, x, y, app):
        """Mostrar menú contextual al hacer clic derecho en una aplicación"""
        popover = Gtk.Popover()
        popover.set_autohide(True)
        
        # Crear menú vertical
        menu_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        menu_box.set_margin_top(8)
        menu_box.set_margin_bottom(8)
        menu_box.set_margin_start(8)
        menu_box.set_margin_end(8)
        
        # Opción: Ver detalles
        details_btn = Gtk.Button()
        details_btn.set_name("context-menu-item")
        details_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        details_icon = Gtk.Label(label="ℹ️")
        details_label = Gtk.Label(label="Ver detalles", xalign=0)
        details_label.set_hexpand(True)
        details_box.append(details_icon)
        details_box.append(details_label)
        details_btn.set_child(details_box)
        details_btn.connect("clicked", lambda b: self.on_context_menu_item_clicked(popover, lambda: self.show_app_info(app)))
        
        # Opción: Desinstalar
        uninstall_btn = Gtk.Button()
        uninstall_btn.set_name("context-menu-item")
        uninstall_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        uninstall_icon = Gtk.Label(label="🗑️")
        uninstall_label = Gtk.Label(label="Desinstalar", xalign=0)
        uninstall_label.set_hexpand(True)
        uninstall_box.append(uninstall_icon)
        uninstall_box.append(uninstall_label)
        uninstall_btn.set_child(uninstall_box)
        uninstall_btn.connect("clicked", lambda b: self.on_context_menu_item_clicked(popover, lambda: self.uninstall_app(app)))
        
        # Opción: Reparar (si aplica)
        package_name = app.get('package', '')
        app_type = app.get('type', '') or ''
        if (
            package_name.endswith('.AppImage') or package_name.endswith('.appimage') or
            app_type == 'wine' or app_type == 'proton' or
            (package_name.endswith('.exe'))
        ):
            repair_btn = Gtk.Button()
            repair_btn.set_name("context-menu-item")
            repair_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            repair_icon = Gtk.Label(label="🛠️")
            repair_label = Gtk.Label(label="Reparar", xalign=0)
            repair_label.set_hexpand(True)
            repair_box.append(repair_icon)
            repair_box.append(repair_label)
            repair_btn.set_child(repair_box)
            repair_btn.connect("clicked", lambda b: self.on_context_menu_item_clicked(popover, lambda: self.repair_app(app)))
            menu_box.append(repair_btn)
        
        # Añadir opciones al menú
        menu_box.append(details_btn)
        menu_box.append(uninstall_btn)
        
        popover.set_child(menu_box)
        popover.set_parent(gesture.get_widget())
        popover.popup()
    
    def on_context_menu_item_clicked(self, popover, callback):
        """Manejar clic en elemento del menú contextual"""
        popover.popdown()
        callback()

    def show_app_info(self, app):
        """Mostrar información detallada de la aplicación"""
        details = []
        details.append(f"📦 Paquete: {app.get('package', 'N/A')}")
        details.append(f"📝 Descripción: {app.get('comment', 'Sin descripción')}")
        details.append(f"🏷️ Categorías: {app.get('categories', 'N/A')}")
        details.append(f"📂 Ejecutable: {app.get('exec', 'N/A')}")
        
        if app.get('essential'):
            details.append("⚠️ Aplicación esencial del sistema")
        
        if app.get('reverse_dependencies'):
            deps = ", ".join(app['reverse_dependencies'][:3])
            if len(app['reverse_dependencies']) > 3:
                deps += f" y {len(app['reverse_dependencies']) - 3} más"
            details.append(f"🔗 Dependencias: {deps}")
        
        details_text = "\n".join(details)
        full_text = f"Información de {app.get('name', 'Aplicación')}\n\n{details_text}"
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text=full_text
        )
        
        def on_response(dialog, response):
            dialog.destroy()
        
        dialog.connect('response', on_response)
        dialog.show()

    def uninstall_app(self, app):
        """Desinstalar aplicación"""
        package_name = app.get('package')
        desktop_path = app.get('desktop')
        app_name = app.get('name', package_name)
        # Determinar tipo de aplicación
        if package_name and (package_name.endswith('.AppImage') or package_name.endswith('.appimage')):
            from src.handlers.appimage_handler import AppImageHandler
            handler = AppImageHandler()
            exec_path = package_name if os.path.exists(package_name) else None
            if not exec_path and desktop_path:
                config = configparser.ConfigParser(interpolation=None)
                config.read(desktop_path)
                if 'Desktop Entry' in config:
                    exec_line = config['Desktop Entry'].get('Exec', '').split()[0]
                    if os.path.exists(exec_line):
                        exec_path = exec_line
            if exec_path:
                # Mostrar animación de desinstalación
                progress_dialog = Gtk.Window()
                progress_dialog.set_title("Desinstalando aplicación")
                progress_dialog.set_transient_for(self.get_root())
                progress_dialog.set_modal(True)
                progress_dialog.set_default_size(400, 200)
                main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
                main_box.set_margin_top(24)
                main_box.set_margin_bottom(24)
                main_box.set_margin_start(24)
                main_box.set_margin_end(24)
                spinner = Gtk.Spinner()
                spinner.set_size_request(32, 32)
                spinner.start()
                label = Gtk.Label(label=f"Desinstalando {app_name}...")
                main_box.append(spinner)
                main_box.append(label)
                progress_dialog.set_child(main_box)
                progress_dialog.show()
                def do_uninstall():
                    handler.uninstall(exec_path)
                    # Eliminar registro de la base de datos
                    for reg in list_installed():
                        _id, name, file_path, type_, _ = reg
                        if file_path == exec_path and type_ == 'appimage':
                            remove_app(_id)
                    GLib.idle_add(self.on_uninstall_complete, progress_dialog, True, None, app_name)
                threading.Thread(target=do_uninstall, daemon=True).start()
            else:
                self.show_library_error("No se pudo encontrar el archivo AppImage para desinstalar.")
            return
        elif package_name and (package_name.endswith('.sh') or package_name.endswith('.run')):
            from src.handlers.script_handler import ScriptHandler
            handler = ScriptHandler()
            progress_dialog = Gtk.Window()
            progress_dialog.set_title("Desinstalando aplicación")
            progress_dialog.set_transient_for(self.get_root())
            progress_dialog.set_modal(True)
            progress_dialog.set_default_size(400, 200)
            main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
            main_box.set_margin_top(24)
            main_box.set_margin_bottom(24)
            main_box.set_margin_start(24)
            main_box.set_margin_end(24)
            spinner = Gtk.Spinner()
            spinner.set_size_request(32, 32)
            spinner.start()
            label = Gtk.Label(label=f"Desinstalando {app_name}...")
            main_box.append(spinner)
            main_box.append(label)
            progress_dialog.set_child(main_box)
            progress_dialog.show()
            def do_uninstall():
                handler.uninstall(package_name)
                # Eliminar registro de la base de datos
                for reg in list_installed():
                    _id, name, file_path, type_, _ = reg
                    if file_path == package_name and type_ == 'script':
                        remove_app(_id)
                GLib.idle_add(self.on_uninstall_complete, progress_dialog, True, None, app_name)
            threading.Thread(target=do_uninstall, daemon=True).start()
            return
        else:
            # Paquete deb: flujo original
            warning_text = "Esta acción no se puede deshacer."
            if app.get('essential') or app.get('priority_required'):
                warning_text += "\n\n⚠️ ADVERTENCIA: Esta es una aplicación crítica del sistema. Desinstalarla puede causar problemas."
            if app.get('reverse_dependencies'):
                warning_text += f"\n\n🔗 Otras aplicaciones dependen de este paquete: {', '.join(app['reverse_dependencies'][:3])}"
            full_text = f"¿Desinstalar {app.get('name', package_name)}?\n\n{warning_text}"
            dialog = Gtk.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text=full_text
            )
            def on_response(dialog, response):
                dialog.destroy()
                if response == Gtk.ResponseType.YES:
                    self.perform_uninstall(package_name)
            dialog.connect('response', on_response)
            dialog.show()

    def perform_uninstall(self, package_name):
        """Realizar desinstalación con animación"""
        # Crear diálogo de progreso mejorado
        progress_dialog = Gtk.Window()
        progress_dialog.set_title("Desinstalando aplicación")
        progress_dialog.set_transient_for(self.get_root())
        progress_dialog.set_modal(True)
        progress_dialog.set_default_size(400, 300)
        
        # Contenedor principal
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)
        
        # Icono animado de desinstalación
        icon_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        icon_box.set_halign(Gtk.Align.CENTER)
        
        # Usamos un spinner grande y visible
        spinner = Gtk.Spinner()
        spinner.set_size_request(64, 64)
        spinner.start()
        
        # Icono de paquete que se desvanece
        package_icon = Gtk.Label(label="📦")
        package_icon.set_name("uninstall-package-icon")
        
        icon_box.append(spinner)
        icon_box.append(package_icon)
        
        # Título y descripción
        title_label = Gtk.Label(label="Desinstalando aplicación")
        title_label.set_name("uninstall-title")
        title_label.set_halign(Gtk.Align.CENTER)
        
        desc_label = Gtk.Label(label=f"Eliminando {package_name} del sistema...")
        desc_label.set_name("uninstall-desc")
        desc_label.set_halign(Gtk.Align.CENTER)
        
        # Barra de progreso pulsante
        progress_bar = Gtk.ProgressBar()
        progress_bar.set_pulse_step(0.1)
        progress_bar.set_margin_top(12)
        progress_bar.set_margin_bottom(12)
        progress_bar.set_size_request(-1, 10)
        progress_bar.set_name("uninstall-progress")
        
        # Texto de estado
        status_label = Gtk.Label(label="Preparando desinstalación...")
        status_label.set_name("uninstall-status")
        status_label.set_halign(Gtk.Align.CENTER)
        
        # Ensamblar interfaz
        main_box.append(icon_box)
        main_box.append(title_label)
        main_box.append(desc_label)
        main_box.append(progress_bar)
        main_box.append(status_label)
        
        progress_dialog.set_child(main_box)
        progress_dialog.show()
        
        # Animar la barra de progreso
        def pulse_progress():
            progress_bar.pulse()
            return True
        
        # Actualizar el estado con mensajes
        status_messages = [
            "Preparando desinstalación...",
            "Verificando dependencias...",
            "Eliminando archivos...",
            "Limpiando configuración...",
            "Actualizando base de datos...",
            "Finalizando desinstalación..."
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
        pulse_id = GLib.timeout_add(100, pulse_progress)
        status_id = GLib.timeout_add(3000, update_status)
        
        def uninstall_task():
            try:
                result = subprocess.run([
                    'pkexec', 'apt-get', 'autoremove', '--purge', '-y', package_name
                ], capture_output=True, text=True, timeout=300)
                
                success = result.returncode == 0
                error_msg = result.stderr if not success else None
                
                # Detener animaciones de forma segura
                try:
                    if pulse_id > 0:
                        GLib.source_remove(pulse_id)
                except:
                    pass
                try:
                    if status_id > 0:
                        GLib.source_remove(status_id)
                except:
                    pass
                
                GLib.idle_add(self.on_uninstall_complete, progress_dialog, success, error_msg, package_name)
            except subprocess.TimeoutExpired:
                GLib.idle_add(self.on_uninstall_complete, progress_dialog, False, "Timeout", package_name)
            except Exception as e:
                GLib.idle_add(self.on_uninstall_complete, progress_dialog, False, str(e), package_name)
        
        threading.Thread(target=uninstall_task, daemon=True).start()

    def on_uninstall_complete(self, progress_dialog, success, error_msg, package_name):
        """Manejar la finalización de la desinstalación con animación"""
        # Obtener el contenedor principal
        main_box = progress_dialog.get_child()
        
        # Limpiar el contenido actual
        while True:
            child = main_box.get_first_child()
            if child is None:
                break
            main_box.remove(child)
        
        if success:
            # Crear animación de éxito
            success_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
            success_box.set_halign(Gtk.Align.CENTER)
            success_box.set_valign(Gtk.Align.CENTER)
            
            # Icono de éxito
            success_icon = Gtk.Label(label="✅")
            success_icon.set_name("uninstall-success-icon")
            
            # Mensaje de éxito
            success_label = Gtk.Label(label="Desinstalación completada")
            success_label.set_name("uninstall-success-label")
            
            # Detalles
            details_label = Gtk.Label(label=f"El paquete {package_name} se ha desinstalado correctamente")
            details_label.set_name("uninstall-details")
            
            # Botón para cerrar
            close_btn = Gtk.Button(label="Cerrar")
            close_btn.set_name("uninstall-close-button")
            close_btn.connect("clicked", lambda b: progress_dialog.destroy())
            
            success_box.append(success_icon)
            success_box.append(success_label)
            success_box.append(details_label)
            success_box.append(close_btn)
            
            main_box.append(success_box)
            
            # Recargar la biblioteca
            self.load_library_apps()
            
            # Cerrar automáticamente después de 5 segundos
            GLib.timeout_add_seconds(5, lambda: progress_dialog.destroy() or False)
        else:
            # Crear animación de error
            error_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
            error_box.set_halign(Gtk.Align.CENTER)
            error_box.set_valign(Gtk.Align.CENTER)
            
            # Icono de error
            error_icon = Gtk.Label(label="❌")
            error_icon.set_name("uninstall-error-icon")
            
            # Mensaje de error
            error_label = Gtk.Label(label="Error en la desinstalación")
            error_label.set_name("uninstall-error-label")
            
            # Detalles del error
            error_details = Gtk.Label(label=f"No se pudo desinstalar {package_name}")
            error_details.set_name("uninstall-error-details")
            
            # Mostrar mensaje de error técnico
            error_text = Gtk.Label(label=str(error_msg))
            error_text.set_name("uninstall-error-text")
            error_text.set_wrap(True)
            error_text.set_max_width_chars(60)
            
            # Botón para cerrar
            close_btn = Gtk.Button(label="Cerrar")
            close_btn.set_name("uninstall-close-button")
            close_btn.connect("clicked", lambda b: progress_dialog.destroy())
            
            error_box.append(error_icon)
            error_box.append(error_label)
            error_box.append(error_details)
            error_box.append(error_text)
            error_box.append(close_btn)
            
            main_box.append(error_box)

    def repair_app(self, app):
        """Mostrar diálogo de reparación para apps Wine/Proton/AppImage (placeholder)."""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.OK,
            text="Herramienta de reparación (en desarrollo)"
        )
        dialog.set_secondary_text(
            "Aquí podrás reinstalar dependencias, cambiar la versión de Windows (para Wine), o ver logs de errores recientes.\n\nPróximamente más opciones."
        )
        def on_response(dialog, response):
            dialog.destroy()
        dialog.connect('response', on_response)
        dialog.show() 