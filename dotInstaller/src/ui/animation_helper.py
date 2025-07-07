"""
Animation Helper - Funciones auxiliares para animaciones y efectos visuales
Este módulo proporciona funciones para mejorar la experiencia visual del instalador manual.
"""

import gi
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, GLib, Gdk
import random
import math

class AnimationHelper:
    """Clase auxiliar para manejar animaciones y efectos visuales"""
    
    def __init__(self):
        self.active_animations = {}
        self.particle_systems = {}
    
    def apply_styles(self, widget, css_provider=None):
        """Aplica los estilos CSS al widget"""
        if css_provider is None:
            css_provider = Gtk.CssProvider()
            # Cargar el archivo CSS
            try:
                css_provider.load_from_path('manual_panel_styles.css')
            except:
                # Si no se puede cargar el archivo, usar estilos básicos
                css_provider.load_from_data(self.get_basic_styles().encode())
        
        # Aplicar al widget
        widget.get_style_context().add_provider(
            css_provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )
    
    def get_basic_styles(self):
        """Retorna estilos CSS básicos como fallback"""
        return """
        #drop-area {
            background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
            border: 3px dashed #dee2e6;
            border-radius: 16px;
            padding: 40px 20px;
            transition: all 0.3s ease;
        }
        
        #drop-area-active {
            background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
            border-color: #0066cc;
            border-style: solid;
            transform: scale(1.02);
        }
        
        #file-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 12px 32px;
            border-radius: 12px;
            font-weight: 600;
        }
        """
    
    def create_animated_progress_dialog(self, title, description, parent_window):
        """Crea un diálogo de progreso con animaciones mejoradas"""
        dialog = Gtk.Window()
        dialog.set_title(title)
        dialog.set_transient_for(parent_window)
        dialog.set_modal(True)
        dialog.set_default_size(500, 400)
        dialog.set_name("install-dialog")
        
        # Contenedor principal con clase para animación
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        main_box.set_margin_top(24)
        main_box.set_margin_bottom(24)
        main_box.set_margin_start(24)
        main_box.set_margin_end(24)
        main_box.add_css_class("fade-in")
        
        # Sección de animación
        animation_container = self.create_installation_animation()
        
        # Información
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        info_box.set_halign(Gtk.Align.CENTER)
        
        title_label = Gtk.Label(label=title)
        title_label.set_name("install-title")
        
        desc_label = Gtk.Label(label=description)
        desc_label.set_name("install-desc")
        
        info_box.append(title_label)
        info_box.append(desc_label)
        
        # Barra de progreso animada
        progress_bar = self.create_animated_progress_bar()
        
        # Estado
        status_label = Gtk.Label(label="Iniciando...")
        status_label.set_name("install-status")
        
        # Ensamblar
        main_box.append(animation_container)
        main_box.append(info_box)
        main_box.append(progress_bar)
        main_box.append(status_label)
        
        dialog.set_child(main_box)
        
        return dialog, status_label, progress_bar
    
    def create_installation_animation(self):
        """Crea el contenedor de animación de instalación"""
        animation_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        animation_box.set_halign(Gtk.Align.CENTER)
        
        # Contenedor para iconos
        icon_container = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        icon_container.set_halign(Gtk.Align.CENTER)
        
        # Icono de paquete
        package_icon = Gtk.Label(label="📦")
        package_icon.set_name("install-package-icon")
        
        # Flecha animada
        arrow_icon = Gtk.Label(label="⬇️")
        arrow_icon.set_name("install-arrow-icon")
        
        # Icono de sistema
        system_icon = Gtk.Label(label="💻")
        system_icon.set_name("install-system-icon")
        
        icon_container.append(package_icon)
        icon_container.append(arrow_icon)
        icon_container.append(system_icon)
        
        # Spinner
        spinner = Gtk.Spinner()
        spinner.set_size_request(32, 32)
        spinner.start()
        
        animation_box.append(icon_container)
        animation_box.append(spinner)
        
        return animation_box
    
    def create_animated_progress_bar(self):
        """Crea una barra de progreso con animación personalizada"""
        progress_bar = Gtk.ProgressBar()
        progress_bar.set_pulse_step(0.05)
        progress_bar.set_margin_top(8)
        progress_bar.set_margin_bottom(8)
        progress_bar.set_size_request(-1, 12)
        progress_bar.set_name("install-progress")
        
        return progress_bar
    
    def start_progress_animation(self, progress_bar):
        """Inicia la animación de la barra de progreso"""
        def pulse():
            progress_bar.pulse()
            return True
        
        animation_id = GLib.timeout_add(100, pulse)
        self.active_animations['progress'] = animation_id
        return animation_id
    
    def start_arrow_animation(self, arrow_icon):
        """Inicia la animación de la flecha"""
        arrow_icons = ["⬇️", "⬇️", "⬇️", "✨", "✨", "✨"]
        arrow_pos = 0
        
        def animate():
            nonlocal arrow_pos
            arrow_icon.set_label(arrow_icons[arrow_pos % len(arrow_icons)])
            arrow_pos += 1
            return True
        
        animation_id = GLib.timeout_add(500, animate)
        self.active_animations['arrow'] = animation_id
        return animation_id
    
    def create_status_updater(self, status_label, messages, interval=3000):
        """Crea un actualizador de estado con mensajes rotatorios"""
        status_index = 0
        
        def update_status():
            nonlocal status_index
            if status_index < len(messages):
                status_label.set_label(messages[status_index])
                status_index += 1
                return True
            return False
        
        animation_id = GLib.timeout_add(interval, update_status)
        self.active_animations['status'] = animation_id
        return animation_id
    
    def create_success_dialog(self, file_name, parent_window):
        """Crea un diálogo de éxito con animaciones"""
        dialog = Gtk.Window()
        dialog.set_title("Instalación Completada")
        dialog.set_transient_for(parent_window)
        dialog.set_modal(True)
        dialog.set_default_size(400, 300)
        dialog.set_name("install-dialog")
        
        # Contenedor principal
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        main_box.set_margin_top(32)
        main_box.set_margin_bottom(32)
        main_box.set_margin_start(32)
        main_box.set_margin_end(32)
        main_box.set_halign(Gtk.Align.CENTER)
        main_box.set_valign(Gtk.Align.CENTER)
        main_box.add_css_class("fade-in")
        
        # Icono de éxito
        success_icon = Gtk.Label(label="✅")
        success_icon.set_name("install-success-icon")
        
        # Mensaje
        success_label = Gtk.Label(label="¡Instalación Completada!")
        success_label.set_name("install-success-label")
        
        # Detalles
        details_label = Gtk.Label(label=f"Se instaló correctamente:\n{file_name}")
        details_label.set_name("install-details")
        details_label.set_justify(Gtk.Justification.CENTER)
        
        # Botón de cerrar
        close_btn = Gtk.Button(label="Cerrar")
        close_btn.set_name("install-close-button")
        close_btn.add_css_class("hover-lift")
        close_btn.connect("clicked", lambda b: dialog.destroy())
        
        main_box.append(success_icon)
        main_box.append(success_label)
        main_box.append(details_label)
        main_box.append(close_btn)
        
        dialog.set_child(main_box)
        
        # Auto-cerrar después de 5 segundos
        GLib.timeout_add_seconds(5, lambda: dialog.destroy() or False)
        
        return dialog
    
    def create_error_dialog(self, file_name, error_message, parent_window):
        """Crea un diálogo de error con animaciones"""
        dialog = Gtk.Window()
        dialog.set_title("Error en la Instalación")
        dialog.set_transient_for(parent_window)
        dialog.set_modal(True)
        dialog.set_default_size(500, 400)
        dialog.set_name("install-dialog")
        
        # Contenedor principal
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=24)
        main_box.set_margin_top(32)
        main_box.set_margin_bottom(32)
        main_box.set_margin_start(32)
        main_box.set_margin_end(32)
        main_box.set_halign(Gtk.Align.CENTER)
        main_box.set_valign(Gtk.Align.CENTER)
        main_box.add_css_class("fade-in")
        
        # Icono de error
        error_icon = Gtk.Label(label="❌")
        error_icon.set_name("install-error-icon")
        
        # Mensaje de error
        error_label = Gtk.Label(label="Error en la Instalación")
        error_label.set_name("install-error-label")
        
        # Detalles del error
        error_details = Gtk.Label(label=f"No se pudo instalar:\n{file_name}")
        error_details.set_name("install-error-details")
        error_details.set_justify(Gtk.Justification.CENTER)
        
        # Mostrar mensaje de error técnico
        error_text = Gtk.Label(label=str(error_message))
        error_text.set_name("install-error-text")
        error_text.set_wrap(True)
        error_text.set_max_width_chars(60)
        
        # Botón de cerrar
        close_btn = Gtk.Button(label="Cerrar")
        close_btn.set_name("install-close-button")
        close_btn.add_css_class("hover-lift")
        close_btn.connect("clicked", lambda b: dialog.destroy())
        
        main_box.append(error_icon)
        main_box.append(error_label)
        main_box.append(error_details)
        main_box.append(error_text)
        main_box.append(close_btn)
        
        dialog.set_child(main_box)
        
        return dialog
    
    def create_particle_system(self, widget, particle_count=10):
        """Crea un sistema de partículas para efectos visuales"""
        particles = []
        
        def create_particle():
            particle = Gtk.Label(label="✨")
            particle.set_name("particle")
            particle.set_halign(Gtk.Align.START)
            particle.set_valign(Gtk.Align.START)
            
            # Posición aleatoria
            x = random.randint(0, widget.get_allocated_width())
            y = random.randint(0, widget.get_allocated_height())
            
            particle.set_margin_start(x)
            particle.set_margin_top(y)
            
            return particle
        
        # Crear partículas
        for _ in range(particle_count):
            particle = create_particle()
            particles.append(particle)
            widget.append(particle)
        
        # Animación de partículas
        def animate_particles():
            for particle in particles:
                # Mover partícula
                current_x = particle.get_margin_start()
                current_y = particle.get_margin_top()
                
                new_x = current_x + random.randint(-5, 5)
                new_y = current_y - random.randint(1, 3)
                
                # Reiniciar si sale de la pantalla
                if new_y < -20:
                    new_y = widget.get_allocated_height() + 20
                    new_x = random.randint(0, widget.get_allocated_width())
                
                particle.set_margin_start(new_x)
                particle.set_margin_top(new_y)
            
            return True
        
        animation_id = GLib.timeout_add(100, animate_particles)
        self.particle_systems[widget] = animation_id
        
        return particles
    
    def create_confetti_effect(self, widget, duration=3000):
        """Crea un efecto de confeti para celebraciones"""
        confetti_colors = ["🔴", "🟢", "🔵", "🟡", "🟣", "🟠"]
        confetti_pieces = []
        
        def create_confetti_piece():
            piece = Gtk.Label(label=random.choice(confetti_colors))
            piece.set_halign(Gtk.Align.START)
            piece.set_valign(Gtk.Align.START)
            
            # Posición inicial aleatoria
            x = random.randint(0, widget.get_allocated_width())
            y = -20
            
            piece.set_margin_start(x)
            piece.set_margin_top(y)
            
            return piece
        
        # Crear confeti
        for _ in range(20):
            piece = create_confetti_piece()
            confetti_pieces.append(piece)
            widget.append(piece)
        
        # Animación de confeti
        start_time = GLib.get_monotonic_time()
        
        def animate_confetti():
            current_time = GLib.get_monotonic_time()
            elapsed = (current_time - start_time) / 1000.0  # Convertir a segundos
            
            if elapsed > duration / 1000.0:
                # Limpiar confeti
                for piece in confetti_pieces:
                    widget.remove(piece)
                return False
            
            for piece in confetti_pieces:
                # Mover confeti hacia abajo con efecto de gravedad
                current_x = piece.get_margin_start()
                current_y = piece.get_margin_top()
                
                # Simular gravedad
                new_y = current_y + 3 + (elapsed * 2)
                new_x = current_x + random.randint(-2, 2)
                
                piece.set_margin_start(new_x)
                piece.set_margin_top(new_y)
            
            return True
        
        animation_id = GLib.timeout_add(50, animate_confetti)
        self.active_animations['confetti'] = animation_id
        
        return confetti_pieces
    
    def create_ripple_effect(self, widget, x, y):
        """Crea un efecto de ondulación en el punto especificado"""
        ripple = Gtk.Label(label="🌊")
        ripple.set_halign(Gtk.Align.START)
        ripple.set_valign(Gtk.Align.START)
        ripple.set_margin_start(x - 10)
        ripple.set_margin_top(y - 10)
        ripple.set_name("ripple-effect")
        
        widget.append(ripple)
        
        # Animación de ondulación
        scale = 1.0
        opacity = 1.0
        
        def animate_ripple():
            nonlocal scale, opacity
            
            scale += 0.1
            opacity -= 0.05
            
            if opacity <= 0:
                widget.remove(ripple)
                return False
            
            # Aplicar transformación (simulada con márgenes)
            ripple.set_margin_start(x - (10 * scale))
            ripple.set_margin_top(y - (10 * scale))
            
            return True
        
        animation_id = GLib.timeout_add(50, animate_ripple)
        self.active_animations['ripple'] = animation_id
        
        return ripple
    
    def create_typing_effect(self, label, text, speed=50):
        """Crea un efecto de escritura en un label"""
        current_text = ""
        char_index = 0
        
        def type_char():
            nonlocal current_text, char_index
            
            if char_index < len(text):
                current_text += text[char_index]
                label.set_label(current_text)
                char_index += 1
                return True
            return False
        
        animation_id = GLib.timeout_add(speed, type_char)
        self.active_animations['typing'] = animation_id
        
        return animation_id
    
    def create_bounce_effect(self, widget, duration=1000):
        """Crea un efecto de rebote en un widget"""
        start_time = GLib.get_monotonic_time()
        original_y = widget.get_margin_top()
        
        def animate_bounce():
            current_time = GLib.get_monotonic_time()
            elapsed = (current_time - start_time) / 1000.0
            
            if elapsed > duration / 1000.0:
                widget.set_margin_top(original_y)
                return False
            
            # Función de rebote
            progress = elapsed / (duration / 1000.0)
            bounce_height = 20 * math.sin(progress * math.pi * 4) * math.exp(-progress * 3)
            
            widget.set_margin_top(original_y - bounce_height)
            
            return True
        
        animation_id = GLib.timeout_add(16, animate_bounce)  # ~60 FPS
        self.active_animations['bounce'] = animation_id
        
        return animation_id
    
    def create_shake_effect(self, widget, duration=500):
        """Crea un efecto de temblor en un widget"""
        start_time = GLib.get_monotonic_time()
        original_x = widget.get_margin_start()
        
        def animate_shake():
            current_time = GLib.get_monotonic_time()
            elapsed = (current_time - start_time) / 1000.0
            
            if elapsed > duration / 1000.0:
                widget.set_margin_start(original_x)
                return False
            
            # Función de temblor
            progress = elapsed / (duration / 1000.0)
            shake_intensity = 10 * (1 - progress) * math.sin(progress * math.pi * 20)
            
            widget.set_margin_start(original_x + shake_intensity)
            
            return True
        
        animation_id = GLib.timeout_add(16, animate_shake)  # ~60 FPS
        self.active_animations['shake'] = animation_id
        
        return animation_id
    
    def create_fade_in_effect(self, widget, duration=500):
        """Crea un efecto de aparición gradual"""
        start_time = GLib.get_monotonic_time()
        widget.set_opacity(0.0)
        
        def animate_fade():
            current_time = GLib.get_monotonic_time()
            elapsed = (current_time - start_time) / 1000.0
            
            if elapsed > duration / 1000.0:
                widget.set_opacity(1.0)
                return False
            
            progress = elapsed / (duration / 1000.0)
            opacity = progress
            
            widget.set_opacity(opacity)
            
            return True
        
        animation_id = GLib.timeout_add(16, animate_fade)  # ~60 FPS
        self.active_animations['fade_in'] = animation_id
        
        return animation_id
    
    def create_fade_out_effect(self, widget, duration=500, callback=None):
        """Crea un efecto de desaparición gradual"""
        start_time = GLib.get_monotonic_time()
        widget.set_opacity(1.0)
        
        def animate_fade():
            current_time = GLib.get_monotonic_time()
            elapsed = (current_time - start_time) / 1000.0
            
            if elapsed > duration / 1000.0:
                widget.set_opacity(0.0)
                if callback:
                    callback()
                return False
            
            progress = elapsed / (duration / 1000.0)
            opacity = 1.0 - progress
            
            widget.set_opacity(opacity)
            
            return True
        
        animation_id = GLib.timeout_add(16, animate_fade)  # ~60 FPS
        self.active_animations['fade_out'] = animation_id
        
        return animation_id
    
    def stop_all_animations(self):
        """Detiene todas las animaciones activas"""
        for animation_id in self.active_animations.values():
            try:
                GLib.source_remove(animation_id)
            except:
                pass
        
        for animation_id in self.particle_systems.values():
            try:
                GLib.source_remove(animation_id)
            except:
                pass
        
        self.active_animations.clear()
        self.particle_systems.clear()
    
    def stop_animation(self, animation_name):
        """Detiene una animación específica"""
        if animation_name in self.active_animations:
            try:
                GLib.source_remove(self.active_animations[animation_name])
                del self.active_animations[animation_name]
            except:
                pass
    
    def cleanup(self):
        """Limpia todos los recursos de animación"""
        self.stop_all_animations() 