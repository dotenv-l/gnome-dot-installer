import gi
# Especificar versión de GTK antes de importar
gi.require_version('Gtk', '4.0')
from gi.repository import Gtk, Gio, Gdk, GLib  # type: ignore
from src.ui.sidebar import Sidebar
from src.ui.panels.store_panel import StorePanel
from src.ui.panels.library_panel import LibraryPanel
from src.ui.panels.manual_panel import ManualPanel
from src.ui.panels.settings_panel import SettingsPanel

# Paleta Material Design mejorada
PRIMARY_COLOR = "#1976D2"
PRIMARY_DARK = "#1565C0"
SECONDARY_COLOR = "#42A5F5"
ACCENT_COLOR = "#4CAF50"
CARD_BG = "#FFFFFF"
CARD_HOVER = "#F5F5F5"
TEXT_PRIMARY = "#212121"
TEXT_SECONDARY = "#757575"
SIDEBAR_BG = "#263238"
SIDEBAR_HOVER = "#37474F"

class MainWindow(Gtk.ApplicationWindow):
    def __init__(self, app):
        super().__init__(application=app)
        self.set_title("Epic Package Store")
        self.set_default_size(1400, 900)
        self.sidebar_expanded = True
        self.current_section = "store"
        
        # Crear sidebar usando el nuevo componente
        self.sidebar = Sidebar(self.show_panel, expanded=True)
        
        # Stack para panel central
        self.main_stack = Gtk.Stack()
        self.main_stack.set_transition_type(Gtk.StackTransitionType.SLIDE_LEFT_RIGHT)
        self.main_stack.set_transition_duration(200)
        self.main_stack.set_hexpand(True)
        
        # Crear paneles usando los nuevos componentes
        self.store_panel = StorePanel()
        self.library_panel = LibraryPanel()
        self.manual_panel = ManualPanel()
        self.settings_panel = SettingsPanel()
        
        self.main_stack.add_titled(self.store_panel, "store", "Tienda")
        self.main_stack.add_titled(self.library_panel, "library", "Biblioteca")
        self.main_stack.add_titled(self.manual_panel, "manual", "Instalador")
        self.main_stack.add_titled(self.settings_panel, "settings", "Configuración")
        
        # Layout principal
        main_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=0)
        main_box.append(self.sidebar)
        main_box.append(self.main_stack)
        
        self.set_child(main_box)
        
        # Inicializar
        self.show_panel("store")
        self.sidebar.update_sidebar_buttons()

    def show_panel(self, section_id):
        """Mostrar panel específico"""
        self.current_section = section_id
        self.main_stack.set_visible_child_name(section_id)
        self.sidebar.current_section = section_id
        self.sidebar.update_sidebar_buttons()

    def apply_styles(self):
        """Aplicar estilos CSS a la aplicación"""
        css = f"""
        /* Estilos generales */
        window {{
            background-color: #f5f5f5;
            font-family: 'Roboto', sans-serif;
        }}
        
        /* Sidebar */
        #sidebar {{
            background-color: {SIDEBAR_BG};
            color: white;
            transition: all 0.3s ease;
        }}
        
        .sidebar-title {{
            font-size: 18px;
            font-weight: bold;
            color: white;
        }}
        
        .sidebar-logo {{
            font-size: 24px;
        }}
        
        .sidebar-button {{
            background: transparent;
            color: white;
            border-radius: 8px;
            padding: 8px;
            border: none;
            text-align: left;
            transition: all 0.2s ease;
        }}
        
        .sidebar-button:hover {{
            background: {SIDEBAR_HOVER};
        }}
        
        .sidebar-button-active {{
            background: {PRIMARY_COLOR};
        }}
        
        .sidebar-button-title {{
            font-size: 14px;
            font-weight: bold;
            color: white;
        }}
        
        .sidebar-button-subtitle {{
            font-size: 12px;
            color: rgba(255, 255, 255, 0.7);
        }}
        
        /* Biblioteca */
        .library-title {{
            font-size: 24px;
            font-weight: bold;
            color: {TEXT_PRIMARY};
        }}
        
        .library-stats {{
            font-size: 14px;
            color: {TEXT_SECONDARY};
        }}
        
        .library-app-row {{
            background: {CARD_BG};
            border-radius: 12px;
            margin: 8px 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            transition: all 0.2s ease;
        }}
        
        .library-app-row:hover {{
            background: {CARD_HOVER};
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }}
        
        .app-name {{
            font-size: 16px;
            font-weight: bold;
            color: {TEXT_PRIMARY};
        }}
        
        .app-description {{
            font-size: 14px;
            color: {TEXT_SECONDARY};
        }}
        
        .app-meta {{
            font-size: 12px;
            color: {TEXT_SECONDARY};
            margin-top: 8px;
        }}
        
        .app-warning {{
            font-size: 12px;
            color: #D32F2F;
            margin-top: 8px;
        }}
        
        .app-info-button, .app-uninstall-button {{
            background: transparent;
            border: none;
            font-size: 18px;
            padding: 8px;
            border-radius: 50%;
            transition: all 0.2s ease;
        }}
        
        .app-info-button:hover {{
            background: {SECONDARY_COLOR};
            color: white;
        }}
        
        .app-uninstall-button:hover {{
            background: #D32F2F;
            color: white;
        }}
        
        /* Categorías */
        .category-filter {{
            background: transparent;
            border: 1px solid {TEXT_SECONDARY};
            color: {TEXT_SECONDARY};
            border-radius: 16px;
            padding: 4px 12px;
            font-size: 12px;
            transition: all 0.2s ease;
        }}
        
        .category-filter:hover {{
            border-color: {PRIMARY_COLOR};
            color: {PRIMARY_COLOR};
        }}
        
        .category-filter-active {{
            background: {PRIMARY_COLOR};
            color: white;
            border-color: {PRIMARY_COLOR};
        }}
        
        /* Menú contextual */
        #context-menu-item {{
            padding: 8px 12px;
            border-radius: 8px;
            background-color: transparent;
            border: none;
            transition: all 0.2s ease;
            margin: 2px 0;
        }}
        
        #context-menu-item:hover {{
            background-color: rgba(0,0,0,0.05);
        }}
        
        /* ===============================================
           MANUAL PANEL STYLES - Instalador Manual
           =============================================== */

        /* Variables CSS para consistencia */
        :root {{
          --primary-color: #0066cc;
          --primary-dark: #0052a3;
          --success-color: #28a745;
          --error-color: #dc3545;
          --warning-color: #ffc107;
          --info-color: #17a2b8;
          --background-dark: #1a1a1a;
          --background-light: #f8f9fa;
          --text-dark: #333333;
          --text-light: #666666;
          --border-color: #dee2e6;
          --shadow-light: rgba(0, 0, 0, 0.1);
          --shadow-medium: rgba(0, 0, 0, 0.15);
          --shadow-heavy: rgba(0, 0, 0, 0.25);
          --gradient-primary: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          --gradient-success: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
          --gradient-error: linear-gradient(135deg, #ff6b6b 0%, #ee5a24 100%);
          --gradient-warning: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
          --border-radius: 12px;
          --border-radius-small: 8px;
          --border-radius-large: 16px;
          --transition-fast: 0.2s ease;
          --transition-medium: 0.3s ease;
          --transition-slow: 0.5s ease;
        }}

        /* ===============================================
           TÍTULOS Y DESCRIPCIÓN PRINCIPAL
           =============================================== */

        #manual-title {{
          font-size: 32px;
          font-weight: 700;
          color: var(--text-dark);
          margin-bottom: 16px;
          text-shadow: 0 2px 4px var(--shadow-light);
          background: var(--gradient-primary);
          -webkit-background-clip: text;
          -webkit-text-fill-color: transparent;
          background-clip: text;
          animation: titlePulse 3s ease-in-out infinite;
        }}

        #manual-desc {{
          font-size: 16px;
          color: var(--text-light);
          margin-bottom: 24px;
          max-width: 600px;
          line-height: 1.6;
          font-weight: 400;
        }}

        #manual-compat {{
          font-size: 14px;
          color: var(--text-light);
          background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
          padding: 16px 24px;
          border-radius: var(--border-radius);
          border-left: 4px solid var(--info-color);
          margin-bottom: 32px;
          box-shadow: 0 2px 8px var(--shadow-light);
          line-height: 1.5;
        }}

        /* ===============================================
           ÁREA DE ARRASTRAR Y SOLTAR
           =============================================== */

        #drop-area {{
          background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
          border: 3px dashed var(--border-color);
          border-radius: var(--border-radius-large);
          padding: 40px 20px;
          margin: 24px 0;
          transition: all var(--transition-medium);
          position: relative;
          overflow: hidden;
          box-shadow: 0 4px 16px var(--shadow-light);
        }}

        #drop-area::before {{
          content: '';
          position: absolute;
          top: -50%;
          left: -50%;
          width: 200%;
          height: 200%;
          background: radial-gradient(circle, rgba(102, 126, 234, 0.1) 0%, transparent 70%);
          opacity: 0;
          transition: opacity var(--transition-medium);
          pointer-events: none;
        }}

        #drop-area:hover {{
          border-color: var(--primary-color);
          background: linear-gradient(135deg, #ffffff 0%, #f0f8ff 100%);
          transform: translateY(-2px);
          box-shadow: 0 8px 24px var(--shadow-medium);
        }}

        #drop-area:hover::before {{
          opacity: 1;
        }}

        #drop-area-active {{
          background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
          border-color: var(--primary-color);
          border-style: solid;
          transform: scale(1.02);
          box-shadow: 0 8px 32px var(--shadow-medium);
          animation: dropAreaPulse 1s ease-in-out infinite;
        }}

        #drop-area-active::before {{
          opacity: 1;
        }}

        #drop-icon {{
          font-size: 48px;
          margin-bottom: 16px;
          animation: dropIconBounce 2s ease-in-out infinite;
          filter: drop-shadow(0 4px 8px var(--shadow-light));
        }}

        #drop-label {{
          font-size: 16px;
          color: var(--text-light);
          font-weight: 500;
        }}

        /* ===============================================
           BOTÓN DE SELECCIÓN DE ARCHIVO
           =============================================== */

        #file-button {{
          background: var(--gradient-primary);
          color: white;
          border: none;
          padding: 12px 32px;
          border-radius: var(--border-radius);
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: all var(--transition-medium);
          box-shadow: 0 4px 16px var(--shadow-light);
          position: relative;
          overflow: hidden;
        }}

        #file-button::before {{
          content: '';
          position: absolute;
          top: 0;
          left: -100%;
          width: 100%;
          height: 100%;
          background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
          transition: left var(--transition-medium);
        }}

        #file-button:hover {{
          transform: translateY(-2px);
          box-shadow: 0 8px 24px var(--shadow-medium);
        }}

        #file-button:hover::before {{
          left: 100%;
        }}

        #file-button:active {{
          transform: translateY(0);
        }}

        /* ===============================================
           ESTADO DE INSTALACIÓN
           =============================================== */

        #install-status {{
          font-size: 14px;
          font-weight: 500;
          margin-top: 16px;
          padding: 12px 20px;
          border-radius: var(--border-radius);
          transition: all var(--transition-medium);
          min-height: 44px;
          display: flex;
          align-items: center;
          justify-content: center;
        }}

        /* ===============================================
           DIÁLOGO DE INSTALACIÓN
           =============================================== */

        #install-dialog {{
          background: rgba(255, 255, 255, 0.95);
          backdrop-filter: blur(10px);
          border-radius: var(--border-radius-large);
          box-shadow: 0 20px 60px var(--shadow-heavy);
          border: 1px solid rgba(255, 255, 255, 0.2);
        }}

        /* ===============================================
           ICONOS DE INSTALACIÓN
           =============================================== */

        #install-package-icon,
        #install-app-icon {{
          font-size: 64px;
          margin-bottom: 8px;
          animation: packageIconRotate 3s ease-in-out infinite;
          filter: drop-shadow(0 4px 12px var(--shadow-medium));
        }}

        #install-arrow-icon {{
          font-size: 32px;
          margin: 8px 0;
          animation: arrowBounce 1s ease-in-out infinite;
          filter: drop-shadow(0 2px 8px var(--shadow-light));
        }}

        #install-system-icon {{
          font-size: 48px;
          margin-top: 8px;
          animation: systemIconPulse 2s ease-in-out infinite;
          filter: drop-shadow(0 4px 12px var(--shadow-medium));
        }}

        #install-success-icon {{
          font-size: 80px;
          color: var(--success-color);
          animation: successIconScale 0.6s ease-out;
          filter: drop-shadow(0 4px 16px rgba(40, 167, 69, 0.3));
        }}

        #install-error-icon {{
          font-size: 80px;
          color: var(--error-color);
          animation: errorIconShake 0.6s ease-out;
          filter: drop-shadow(0 4px 16px rgba(220, 53, 69, 0.3));
        }}

        /* ===============================================
           TEXTO DE INSTALACIÓN
           =============================================== */

        #install-title {{
          font-size: 24px;
          font-weight: 700;
          color: var(--text-dark);
          margin-bottom: 8px;
          text-align: center;
        }}

        #install-desc {{
          font-size: 16px;
          color: var(--text-light);
          text-align: center;
          margin-bottom: 16px;
        }}

        #install-status {{
          font-size: 14px;
          color: var(--text-light);
          text-align: center;
          font-weight: 500;
          animation: statusFade 2s ease-in-out infinite;
        }}

        #install-success-label {{
          font-size: 28px;
          font-weight: 700;
          color: var(--success-color);
          text-align: center;
          margin-bottom: 16px;
          animation: successTextGlow 2s ease-in-out infinite;
        }}

        #install-error-label {{
          font-size: 28px;
          font-weight: 700;
          color: var(--error-color);
          text-align: center;
          margin-bottom: 16px;
        }}

        #install-details,
        #install-error-details {{
          font-size: 16px;
          color: var(--text-light);
          text-align: center;
          margin-bottom: 16px;
          line-height: 1.5;
        }}

        #install-error-text {{
          font-size: 14px;
          color: var(--text-light);
          background: rgba(220, 53, 69, 0.1);
          padding: 12px 16px;
          border-radius: var(--border-radius-small);
          border-left: 4px solid var(--error-color);
          margin-bottom: 20px;
          font-family: monospace;
          line-height: 1.4;
        }}

        /* ===============================================
           BARRA DE PROGRESO
           =============================================== */

        #install-progress {{
          background: rgba(102, 126, 234, 0.1);
          border-radius: var(--border-radius-small);
          overflow: hidden;
          position: relative;
          height: 8px;
        }}

        #install-progress::before {{
          content: '';
          position: absolute;
          top: 0;
          left: 0;
          height: 100%;
          background: var(--gradient-primary);
          border-radius: var(--border-radius-small);
          animation: progressPulse 2s ease-in-out infinite;
          width: 100%;
        }}

        /* ===============================================
           BOTÓN DE CERRAR
           =============================================== */

        #install-close-button {{
          background: var(--gradient-primary);
          color: white;
          border: none;
          padding: 12px 24px;
          border-radius: var(--border-radius);
          font-size: 16px;
          font-weight: 600;
          cursor: pointer;
          transition: all var(--transition-medium);
          box-shadow: 0 4px 16px var(--shadow-light);
          margin-top: 16px;
        }}

        #install-close-button:hover {{
          transform: translateY(-2px);
          box-shadow: 0 8px 24px var(--shadow-medium);
        }}

        /* ===============================================
           ANIMACIONES KEYFRAMES
           =============================================== */

        @keyframes titlePulse {{
          0%, 100% {{ opacity: 1; }}
          50% {{ opacity: 0.8; }}
        }}

        @keyframes dropAreaPulse {{
          0%, 100% {{ transform: scale(1.02); }}
          50% {{ transform: scale(1.05); }}
        }}

        @keyframes dropIconBounce {{
          0%, 100% {{ transform: translateY(0); }}
          25% {{ transform: translateY(-10px); }}
          50% {{ transform: translateY(0); }}
          75% {{ transform: translateY(-5px); }}
        }}

        @keyframes packageIconRotate {{
          0% {{ transform: rotate(0deg) scale(1); }}
          25% {{ transform: rotate(5deg) scale(1.05); }}
          50% {{ transform: rotate(0deg) scale(1); }}
          75% {{ transform: rotate(-5deg) scale(1.05); }}
          100% {{ transform: rotate(0deg) scale(1); }}
        }}

        @keyframes arrowBounce {{
          0%, 100% {{ transform: translateY(0) scale(1); }}
          50% {{ transform: translateY(-8px) scale(1.1); }}
        }}

        @keyframes systemIconPulse {{
          0%, 100% {{ transform: scale(1); opacity: 1; }}
          50% {{ transform: scale(1.1); opacity: 0.8; }}
        }}

        @keyframes successIconScale {{
          0% {{ transform: scale(0); opacity: 0; }}
          50% {{ transform: scale(1.2); opacity: 0.8; }}
          100% {{ transform: scale(1); opacity: 1; }}
        }}

        @keyframes errorIconShake {{
          0%, 100% {{ transform: translateX(0); }}
          25% {{ transform: translateX(-5px); }}
          75% {{ transform: translateX(5px); }}
        }}

        @keyframes statusFade {{
          0%, 100% {{ opacity: 1; }}
          50% {{ opacity: 0.7; }}
        }}

        @keyframes successTextGlow {{
          0%, 100% {{ text-shadow: 0 0 10px rgba(40, 167, 69, 0.5); }}
          50% {{ text-shadow: 0 0 20px rgba(40, 167, 69, 0.8); }}
        }}

        @keyframes progressPulse {{
          0% {{ transform: translateX(-100%); }}
          100% {{ transform: translateX(100%); }}
        }}

        /* ===============================================
           EFECTOS DE HOVER MEJORADOS
           =============================================== */

        .hover-lift {{
          transition: all var(--transition-medium);
        }}

        .hover-lift:hover {{
          transform: translateY(-4px);
          box-shadow: 0 12px 32px var(--shadow-medium);
        }}

        .hover-glow {{
          transition: all var(--transition-medium);
        }}

        .hover-glow:hover {{
          box-shadow: 0 0 20px rgba(102, 126, 234, 0.4);
        }}

        /* ===============================================
           UTILIDADES ADICIONALES
           =============================================== */

        .fade-in {{
          animation: fadeIn 0.5s ease-in-out;
        }}

        .fade-out {{
          animation: fadeOut 0.5s ease-in-out;
        }}

        .slide-in-up {{
          animation: slideInUp 0.5s ease-out;
        }}

        .slide-out-down {{
          animation: slideOutDown 0.5s ease-in;
        }}

        @keyframes fadeIn {{
          from {{ opacity: 0; }}
          to {{ opacity: 1; }}
        }}

        @keyframes fadeOut {{
          from {{ opacity: 1; }}
          to {{ opacity: 0; }}
        }}

        @keyframes slideInUp {{
          from {{ transform: translateY(30px); opacity: 0; }}
          to {{ transform: translateY(0); opacity: 1; }}
        }}

        @keyframes slideOutDown {{
          from {{ transform: translateY(0); opacity: 1; }}
          to {{ transform: translateY(30px); opacity: 0; }}
        }}

        /* ===============================================
           ESTADOS RESPONSIVOS
           =============================================== */

        @media (max-width: 768px) {{
          #manual-title {{
            font-size: 24px;
          }}
          
          #drop-area {{
            padding: 24px 16px;
          }}
          
          #drop-icon {{
            font-size: 36px;
          }}
          
          #install-package-icon,
          #install-app-icon {{
            font-size: 48px;
          }}
          
          #install-success-icon,
          #install-error-icon {{
            font-size: 64px;
          }}
        }}

        /* ===============================================
           TEMA OSCURO (OPCIONAL)
           =============================================== */

        @media (prefers-color-scheme: dark) {{
          :root {{
            --text-dark: #ffffff;
            --text-light: #cccccc;
            --background-light: #2a2a2a;
            --border-color: #444444;
          }}
          
          #drop-area {{
            background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
            border-color: #444444;
          }}
          
          #drop-area:hover {{
            background: linear-gradient(135deg, #333333 0%, #1a1a2e 100%);
          }}
          
          #manual-compat {{
            background: linear-gradient(135deg, #2a2a2a 0%, #1a1a1a 100%);
            border-left-color: var(--info-color);
          }}
          
          #install-dialog {{
            background: rgba(42, 42, 42, 0.95);
          }}
        }}
        
        /* Diálogo de instalación */
        #install-dialog {{
            background-color: #ffffff;
            border-radius: 16px;
        }}
        
        #install-title {{
            font-size: 20px;
            font-weight: bold;
            color: {TEXT_PRIMARY};
        }}
        
        #install-desc {{
            font-size: 14px;
            color: {TEXT_SECONDARY};
        }}
        
        #install-package-icon {{
            font-size: 48px;
        }}
        
        #install-arrow-icon {{
            font-size: 32px;
            color: {PRIMARY_COLOR};
        }}
        
        #install-system-icon {{
            font-size: 48px;
        }}
        
        #install-progress {{
            min-height: 6px;
            border-radius: 3px;
        }}
        
        #install-status {{
            font-size: 14px;
            color: {TEXT_SECONDARY};
        }}
        
        #install-success-icon {{
            font-size: 64px;
        }}
        
        #install-success-label {{
            font-size: 24px;
            font-weight: bold;
            color: #4CAF50;
        }}
        
        #install-details {{
            font-size: 14px;
            color: {TEXT_SECONDARY};
        }}
        
        #install-close-button {{
            background: {PRIMARY_COLOR};
            color: white;
            border-radius: 8px;
            padding: 8px 16px;
            border: none;
            font-weight: bold;
            transition: all 0.2s ease;
        }}
        
        #install-close-button:hover {{
            background: {PRIMARY_DARK};
        }}
        
        #install-error-icon {{
            font-size: 64px;
        }}
        
        #install-error-label {{
            font-size: 24px;
            font-weight: bold;
            color: #D32F2F;
        }}
        
        #install-error-details {{
            font-size: 14px;
            color: {TEXT_SECONDARY};
        }}
        
        #install-error-text {{
            font-size: 12px;
            color: #D32F2F;
            background: rgba(211, 47, 47, 0.1);
            padding: 8px;
            border-radius: 4px;
            margin: 8px 0;
         }}
         
         #install-app-icon {{
            font-size: 48px;
         }}
         
         /* Panel de configuración */
         #settings-icon {{
            font-size: 24px;
         }}
         
         #settings-title {{
            font-size: 20px;
            font-weight: bold;
            color: {TEXT_PRIMARY};
         }}
         
         #settings-description {{
            color: {TEXT_SECONDARY};
            margin-bottom: 16px;
         }}
         
         #empty-icon {{
            font-size: 48px;
            color: #d0d0d0;
            margin-bottom: 8px;
         }}
         
         #empty-label {{
            font-size: 18px;
            font-weight: bold;
            color: {TEXT_PRIMARY};
         }}
         
         #empty-description {{
            color: {TEXT_SECONDARY};
         }}
         
         #settings-frame {{
            border-radius: 12px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            background-color: white;
            overflow: hidden;
         }}
         
         #settings-listbox {{
            background-color: white;
         }}
         
         #settings-header-row {{
            background-color: #f5f5f5;
            border-bottom: 1px solid rgba(0,0,0,0.1);
         }}
         
         #column-header {{
            font-weight: bold;
            font-size: 14px;
            color: {TEXT_SECONDARY};
         }}
         
         #settings-row {{
            border-bottom: 1px solid rgba(0,0,0,0.05);
            transition: all 0.2s ease;
         }}
         
         #settings-row:hover {{
            background-color: rgba(53, 132, 228, 0.05);
         }}
         
         #settings-app-name {{
            font-weight: bold;
            color: {TEXT_PRIMARY};
         }}
         
         #settings-app-type {{
            color: {TEXT_SECONDARY};
         }}
         
         #settings-app-path {{
            color: {TEXT_SECONDARY};
            font-size: 13px;
         }}
         
         #settings-app-date {{
            color: {TEXT_SECONDARY};
            font-size: 13px;
         }}
         
         #detail-label {{
            font-weight: bold;
            color: {TEXT_SECONDARY};
         }}
         
         #details-icon {{
            font-size: 24px;
         }}
        """
        
        provider = Gtk.CssProvider()
        provider.load_from_data(css.encode())
        
        Gtk.StyleContext.add_provider_for_display(
            Gdk.Display.get_default(),
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

class EpicPackageStore(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="com.epic.packagestore",
            flags=Gio.ApplicationFlags.DEFAULT_FLAGS
        )
        
    def do_activate(self):
        win = MainWindow(self)
        win.apply_styles()
        win.present()

if __name__ == "__main__":
    import sys
    
    app = EpicPackageStore()
    exit_status = app.run(sys.argv)
    sys.exit(exit_status)