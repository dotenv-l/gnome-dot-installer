import gi
# Especificar versión de GTK antes de importar
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gdk

PRIMARY_COLOR = "#1976D2"
SIDEBAR_BG = "#263238"
SIDEBAR_HOVER = "#37474F"

class Sidebar(Gtk.Box):
    def __init__(self, on_section_change, expanded=True):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_size_request(240 if expanded else 64, -1)
        self.set_name("sidebar")
        self.on_section_change = on_section_change
        self.expanded = expanded
        self.current_section = "store"
        self.sidebar_buttons = {}
        self._build_sidebar()

    def _build_sidebar(self):
        # Header
        header_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        header_box.set_margin_top(24)
        header_box.set_margin_bottom(24)
        header_box.set_margin_start(20)
        header_box.set_margin_end(20)
        logo_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        logo_box.set_halign(Gtk.Align.CENTER)
        logo_label = Gtk.Label(label="🚀")
        logo_label.set_name("sidebar-logo")
        title_label = Gtk.Label(label="Epic Store")
        title_label.set_name("sidebar-title")
        logo_box.append(logo_label)
        logo_box.append(title_label)
        header_box.append(logo_box)
        separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
        separator.set_margin_top(12)
        header_box.append(separator)
        self.append(header_box)
        # Botones
        buttons_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        buttons_box.set_margin_start(12)
        buttons_box.set_margin_end(12)
        sections = [
            ("store", "🛒", "Tienda", "Descubre nuevas aplicaciones"),
            ("library", "📚", "Biblioteca", "Tus aplicaciones instaladas"),
            ("manual", "📦", "Instalador", "Instala archivos manualmente"),
            ("settings", "⚙️", "Configuración", "Ajustes y registros")
        ]
        for section_id, icon, title, subtitle in sections:
            btn = Gtk.Button()
            btn.set_name(f"sidebar-btn-{section_id}")
            btn.set_tooltip_text(subtitle)
            btn.set_halign(Gtk.Align.FILL)
            btn.set_valign(Gtk.Align.CENTER)
            btn.set_hexpand(True)
            btn.set_margin_bottom(4)
            btn_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            btn_icon = Gtk.Label(label=icon)
            btn_icon.set_name("sidebar-btn-icon")
            btn_title = Gtk.Label(label=title)
            btn_title.set_name("sidebar-btn-title")
            btn_box.append(btn_icon)
            btn_box.append(btn_title)
            btn.set_child(btn_box)
            btn.connect("clicked", lambda b, sid=section_id: self._on_section_clicked(sid))
            btn.text_box = btn_box
            self.sidebar_buttons[section_id] = btn
            buttons_box.append(btn)
        self.append(buttons_box)
        # Botón de colapso
        collapse_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        collapse_box.set_margin_top(24)
        collapse_box.set_margin_start(12)
        collapse_box.set_margin_end(12)
        self.collapse_btn = Gtk.Button(label="⏪" if self.expanded else "⏩")
        self.collapse_btn.set_halign(Gtk.Align.START)
        self.collapse_btn.set_name("sidebar-collapse")
        self.collapse_btn.connect("clicked", self.toggle_sidebar)
        collapse_box.append(self.collapse_btn)
        self.append(collapse_box)
        self.update_sidebar_buttons()
        self._update_text_visibility()

    def _on_section_clicked(self, section_id):
        self.current_section = section_id
        self.update_sidebar_buttons()
        if self.on_section_change:
            self.on_section_change(section_id)

    def toggle_sidebar(self, button=None):
        self.expanded = not self.expanded
        self.set_size_request(240 if self.expanded else 64, -1)
        self.collapse_btn.set_label("⏪" if self.expanded else "⏩")
        self._update_text_visibility()

    def _update_text_visibility(self):
        for btn in self.sidebar_buttons.values():
            if hasattr(btn, 'text_box'):
                btn.text_box.set_visible(self.expanded)

    def update_sidebar_buttons(self):
        for section_id, btn in self.sidebar_buttons.items():
            if section_id == self.current_section:
                btn.set_name("sidebar-button-active")
            else:
                btn.set_name("sidebar-button") 