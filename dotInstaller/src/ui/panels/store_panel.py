import gi
# Especificar versión de GTK antes de importar
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib  # type: ignore

class StorePanel(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL)
        self.set_halign(Gtk.Align.CENTER)
        self.set_valign(Gtk.Align.CENTER)
        message_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        message_box.set_halign(Gtk.Align.CENTER)
        message_box.set_valign(Gtk.Align.CENTER)
        icon_label = Gtk.Label(label="🚧")
        icon_label.set_name("development-icon")
        title_label = Gtk.Label(label="Tienda en Desarrollo")
        title_label.set_name("development-title")
        subtitle_label = Gtk.Label(label="Esta sección estará disponible próximamente.\nMientras tanto, puedes usar la Biblioteca para gestionar tus aplicaciones.")
        subtitle_label.set_name("development-subtitle")
        subtitle_label.set_justify(Gtk.Justification.CENTER)
        progress = Gtk.ProgressBar()
        progress.set_size_request(300, 4)
        progress.set_name("development-progress")
        progress.pulse()
        def animate_progress():
            progress.pulse()
            return True
        GLib.timeout_add(100, animate_progress)
        message_box.append(icon_label)
        message_box.append(title_label)
        message_box.append(subtitle_label)
        message_box.append(progress)
        self.append(message_box) 