import gi
# Especificar versión de GTK antes de importar
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk, Pango  # type: ignore
from src.data.database import list_installed, remove_app
import os
import subprocess
import datetime

class SettingsPanel(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        self.set_margin_top(32)
        self.set_margin_bottom(32)
        self.set_margin_start(64)
        self.set_margin_end(64)
        
        header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        header_box.set_halign(Gtk.Align.CENTER)
        header_box.set_margin_bottom(24)
        
        title_icon = Gtk.Label(label="⚙️")
        title_icon.set_name("settings-icon")
        
        title_label = Gtk.Label(label="Configuración y Registros de la Base de Datos")
        title_label.set_name("settings-title")
        
        header_box.append(title_icon)
        header_box.append(title_label)
        self.append(header_box)
        
        # Descripción
        description = Gtk.Label()
        description.set_markup("<span size='small'>Gestiona los registros de aplicaciones instaladas. Utiliza el menú contextual (clic derecho) para más opciones.</span>")
        description.set_name("settings-description")
        description.set_halign(Gtk.Align.CENTER)
        description.set_margin_bottom(16)
        self.append(description)
        
        # Cargar registros
        self.load_registry_data()
    
    def load_registry_data(self):
        """Cargar datos de la base de datos"""
        registros = list_installed()
        
        if not registros:
            # Mensaje cuando no hay registros
            empty_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            empty_box.set_valign(Gtk.Align.CENTER)
            empty_box.set_vexpand(True)
            
            empty_icon = Gtk.Label(label="📂")
            empty_icon.set_name("empty-icon")
            
            empty_label = Gtk.Label(label="No hay registros en la base de datos")
            empty_label.set_name("empty-label")
            
            empty_desc = Gtk.Label()
            empty_desc.set_markup("<span size='small'>Las aplicaciones instaladas aparecerán aquí</span>")
            empty_desc.set_name("empty-description")
            
            empty_box.append(empty_icon)
            empty_box.append(empty_label)
            empty_box.append(empty_desc)
            self.append(empty_box)
        else:
            # Contenedor con borde y sombra
            frame = Gtk.Frame()
            frame.set_name("settings-frame")
            
            # Lista de registros con scroll
            scroll = Gtk.ScrolledWindow()
            scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            scroll.set_vexpand(True)
            scroll.set_margin_top(0)
            
            # Lista con separación entre elementos
            listbox = Gtk.ListBox()
            listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
            listbox.set_name("settings-listbox")
            
            # Encabezado de columnas
            header_row = Gtk.ListBoxRow()
            header_row.set_selectable(False)
            header_row.set_name("settings-header-row")
            
            header_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
            header_box.set_margin_top(12)
            header_box.set_margin_bottom(12)
            header_box.set_margin_start(16)
            header_box.set_margin_end(16)
            
            name_header = Gtk.Label(label="Nombre")
            name_header.set_name("column-header")
            name_header.set_hexpand(True)
            name_header.set_xalign(0)
            
            type_header = Gtk.Label(label="Tipo")
            type_header.set_name("column-header")
            type_header.set_width_chars(15)
            type_header.set_xalign(0)
            
            path_header = Gtk.Label(label="Ruta")
            path_header.set_name("column-header")
            path_header.set_hexpand(True)
            path_header.set_xalign(0)
            
            date_header = Gtk.Label(label="Fecha")
            date_header.set_name("column-header")
            date_header.set_width_chars(20)
            date_header.set_xalign(0)
            
            header_box.append(name_header)
            header_box.append(type_header)
            header_box.append(path_header)
            header_box.append(date_header)
            
            header_row.set_child(header_box)
            listbox.append(header_row)
            
            # Filas de registros
            for reg in registros:
                _id, name, file_path, type_, install_date = reg
                row = self.create_settings_row(reg)
                listbox.append(row)
            
            scroll.set_child(listbox)
            frame.set_child(scroll)
            self.append(frame)
    
    def create_settings_row(self, reg):
        """Crear fila para registro de configuración con diseño mejorado y menú contextual"""
        _id, name, file_path, type_, install_date = reg
        
        row = Gtk.ListBoxRow()
        row.set_name("settings-row")
        
        # Contenedor principal
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        main_box.set_margin_top(12)
        main_box.set_margin_bottom(12)
        main_box.set_margin_start(16)
        main_box.set_margin_end(16)
        
        # Nombre de la aplicación
        name_label = Gtk.Label(label=name or "Sin nombre")
        name_label.set_name("settings-app-name")
        name_label.set_hexpand(True)
        name_label.set_xalign(0)
        name_label.set_ellipsize(Pango.EllipsizeMode.END)
        
        # Tipo de aplicación
        type_label = Gtk.Label(label=type_ or "Desconocido")
        type_label.set_name("settings-app-type")
        type_label.set_width_chars(15)
        type_label.set_xalign(0)
        
        # Ruta del archivo
        path_label = Gtk.Label(label=file_path or "N/A")
        path_label.set_name("settings-app-path")
        path_label.set_hexpand(True)
        path_label.set_xalign(0)
        path_label.set_ellipsize(Pango.EllipsizeMode.MIDDLE)
        
        # Fecha de instalación
        date_str = "Desconocida"
        if install_date:
            try:
                date_obj = datetime.datetime.fromisoformat(install_date)
                date_str = date_obj.strftime("%d/%m/%Y %H:%M")
            except:
                date_str = install_date
        
        date_label = Gtk.Label(label=date_str)
        date_label.set_name("settings-app-date")
        date_label.set_width_chars(20)
        date_label.set_xalign(0)
        
        # Añadir elementos al contenedor
        main_box.append(name_label)
        main_box.append(type_label)
        main_box.append(path_label)
        main_box.append(date_label)
        
        row.set_child(main_box)
        
        # Configurar menú contextual (clic derecho)
        gesture = Gtk.GestureClick.new()
        gesture.set_button(3)  # Botón derecho
        gesture.connect("pressed", self.on_settings_row_right_click, reg)
        row.add_controller(gesture)
        
        return row
    
    def on_settings_row_right_click(self, gesture, n_press, x, y, reg):
        """Mostrar menú contextual al hacer clic derecho en un registro"""
        _id, name, file_path, type_, install_date = reg
        
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
        details_btn.connect("clicked", lambda b: self.on_settings_menu_item_clicked(popover, lambda: self.show_registry_details(reg)))
        
        # Opción: Eliminar registro
        delete_btn = Gtk.Button()
        delete_btn.set_name("context-menu-item")
        delete_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        delete_icon = Gtk.Label(label="🗑️")
        delete_label = Gtk.Label(label="Eliminar registro", xalign=0)
        delete_label.set_hexpand(True)
        delete_box.append(delete_icon)
        delete_box.append(delete_label)
        delete_btn.set_child(delete_box)
        delete_btn.connect("clicked", lambda b: self.on_settings_menu_item_clicked(popover, lambda: self.delete_registry(_id)))
        
        # Opción: Abrir ubicación (si existe)
        if file_path and os.path.exists(os.path.dirname(file_path)):
            open_btn = Gtk.Button()
            open_btn.set_name("context-menu-item")
            open_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            open_icon = Gtk.Label(label="📂")
            open_label = Gtk.Label(label="Abrir ubicación", xalign=0)
            open_label.set_hexpand(True)
            open_box.append(open_icon)
            open_box.append(open_label)
            open_btn.set_child(open_box)
            open_btn.connect("clicked", lambda b: self.on_settings_menu_item_clicked(popover, lambda: self.open_file_location(file_path)))
            menu_box.append(open_btn)
        
        # Añadir opciones al menú
        menu_box.append(details_btn)
        menu_box.append(delete_btn)
        
        popover.set_child(menu_box)
        popover.set_parent(gesture.get_widget())
        popover.popup()
    
    def on_settings_menu_item_clicked(self, popover, callback):
        """Manejar clic en elemento del menú contextual de configuración"""
        popover.popdown()
        callback()
    
    def show_registry_details(self, reg):
        """Mostrar detalles completos del registro en un diálogo"""
        _id, name, file_path, type_, install_date = reg
        
        dialog = Gtk.Dialog(
            title="Detalles del Registro",
            transient_for=self.get_root(),
            modal=True,
            destroy_with_parent=True
        )
        dialog.set_default_size(500, 300)
        
        content_area = dialog.get_content_area()
        content_area.set_margin_top(20)
        content_area.set_margin_bottom(20)
        content_area.set_margin_start(20)
        content_area.set_margin_end(20)
        content_area.set_spacing(16)
        
        # Título
        title_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        title_icon = Gtk.Label(label="📋")
        title_icon.set_name("details-icon")
        title_label = Gtk.Label()
        title_label.set_markup(f"<span size='x-large' weight='bold'>{name or 'Sin nombre'}</span>")
        title_box.append(title_icon)
        title_box.append(title_label)
        content_area.append(title_box)
        
        # Separador
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        content_area.append(separator)
        
        # Detalles
        details_grid = Gtk.Grid()
        details_grid.set_column_spacing(12)
        details_grid.set_row_spacing(8)
        
        # ID
        id_label = Gtk.Label(label="ID:")
        id_label.set_halign(Gtk.Align.START)
        id_label.set_name("detail-label")
        id_value = Gtk.Label(label=str(_id))
        id_value.set_halign(Gtk.Align.START)
        id_value.set_selectable(True)
        details_grid.attach(id_label, 0, 0, 1, 1)
        details_grid.attach(id_value, 1, 0, 1, 1)
        
        # Nombre
        name_label = Gtk.Label(label="Nombre:")
        name_label.set_halign(Gtk.Align.START)
        name_label.set_name("detail-label")
        name_value = Gtk.Label(label=name or "Sin nombre")
        name_value.set_halign(Gtk.Align.START)
        name_value.set_selectable(True)
        details_grid.attach(name_label, 0, 1, 1, 1)
        details_grid.attach(name_value, 1, 1, 1, 1)
        
        # Tipo
        type_label = Gtk.Label(label="Tipo:")
        type_label.set_halign(Gtk.Align.START)
        type_label.set_name("detail-label")
        type_value = Gtk.Label(label=type_ or "Desconocido")
        type_value.set_halign(Gtk.Align.START)
        type_value.set_selectable(True)
        details_grid.attach(type_label, 0, 2, 1, 1)
        details_grid.attach(type_value, 1, 2, 1, 1)
        
        # Ruta
        path_label = Gtk.Label(label="Ruta:")
        path_label.set_halign(Gtk.Align.START)
        path_label.set_name("detail-label")
        path_value = Gtk.Label(label=file_path or "N/A")
        path_value.set_halign(Gtk.Align.START)
        path_value.set_selectable(True)
        path_value.set_wrap(True)
        path_value.set_max_width_chars(50)
        details_grid.attach(path_label, 0, 3, 1, 1)
        details_grid.attach(path_value, 1, 3, 1, 1)
        
        # Fecha
        date_label = Gtk.Label(label="Instalación:")
        date_label.set_halign(Gtk.Align.START)
        date_label.set_name("detail-label")
        
        date_str = "Desconocida"
        if install_date:
            try:
                date_obj = datetime.datetime.fromisoformat(install_date)
                date_str = date_obj.strftime("%d/%m/%Y %H:%M:%S")
            except:
                date_str = install_date
        
        date_value = Gtk.Label(label=date_str)
        date_value.set_halign(Gtk.Align.START)
        date_value.set_selectable(True)
        details_grid.attach(date_label, 0, 4, 1, 1)
        details_grid.attach(date_value, 1, 4, 1, 1)
        
        content_area.append(details_grid)
        
        # Botones
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        button_box.set_halign(Gtk.Align.END)
        button_box.set_margin_top(16)
        
        close_button = Gtk.Button(label="Cerrar")
        close_button.connect("clicked", lambda b: dialog.destroy())
        button_box.append(close_button)
        
        content_area.append(button_box)
        
        dialog.show()
    
    def delete_registry(self, reg_id):
        """Eliminar registro con confirmación"""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.YES_NO,
            text="¿Eliminar registro?"
        )
        dialog.format_secondary_text(
            "Esta acción eliminará el registro de la base de datos. " +
            "Los archivos de la aplicación no serán eliminados."
        )
        
        response = dialog.run()
        dialog.destroy()
        
        if response == Gtk.ResponseType.YES:
            remove_app(reg_id)
            # Recargar datos
            self.clear_content()
            self.load_registry_data()
    
    def open_file_location(self, file_path):
        """Abrir la ubicación del archivo en el explorador de archivos"""
        directory = os.path.dirname(file_path)
        try:
            subprocess.Popen(['xdg-open', directory])
        except Exception as e:
            print(f"Error al abrir la ubicación: {e}")
            dialog = Gtk.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                message_type=Gtk.MessageType.ERROR,
                buttons=Gtk.ButtonsType.OK,
                text="Error al abrir la ubicación"
            )
            dialog.format_secondary_text(str(e))
            dialog.run()
            dialog.destroy()
    
    def clear_content(self):
        """Limpiar contenido del panel para recargar"""
        # Remover todos los widgets excepto el header y descripción
        while self.get_last_child() and self.get_last_child() != self.get_first_child().get_next_sibling():
            self.remove(self.get_last_child()) 