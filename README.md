# 🚀 GNOME Dot Installer

**Un instalador moderno y elegante para paquetes .deb, AppImages y ejecutables de Windows en sistemas Linux con GNOME.**

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![GTK](https://img.shields.io/badge/GTK-4.0-green.svg)](https://gtk.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Descripción

GNOME Dot Installer es una aplicación de escritorio moderna desarrollada en Python con GTK4 que proporciona una interfaz gráfica intuitiva para instalar y gestionar diferentes tipos de paquetes en sistemas Linux con GNOME. La aplicación combina funcionalidad avanzada con una experiencia de usuario excepcional.

## ✨ Características Principales

### 🎯 **Instalación Multi-Formato**
- **Paquetes .deb**: Instalación nativa de paquetes Debian/Ubuntu
- **AppImages**: Gestión completa de aplicaciones portables
- **Ejecutables Windows (.exe)**: Instalación mediante Wine/Proton
- **Scripts (.sh, .run)**: Ejecución de scripts de instalación

### 🎨 **Interfaz Moderna y Animada**
- **Diseño Material Design** con gradientes y efectos visuales
- **Animaciones fluidas** durante la instalación y navegación
- **Efectos visuales avanzados**: confeti, partículas, rebote, fade
- **Soporte para tema oscuro** automático
- **Diseño responsivo** que se adapta a diferentes tamaños de pantalla

### 🔧 **Funcionalidades Avanzadas**
- **Drag & Drop** intuitivo para archivos
- **Gestión de dependencias** automática
- **Base de datos local** para seguimiento de instalaciones
- **Sistema de notificaciones** integrado
- **Manejo de errores** con feedback visual detallado

### 🛠 **Herramientas de Desarrollo**
- **AnimationHelper**: Sistema modular de animaciones
- **Handlers especializados** para cada tipo de paquete
- **Arquitectura modular** y extensible
- **Gestión automática de recursos** de memoria

## 🏗 Arquitectura del Proyecto

```
gnome-dot-installer/
├── dotInstaller/                 # Directorio principal de la aplicación
│   ├── src/                     # Código fuente
│   │   ├── core/               # Lógica principal del instalador
│   │   ├── data/               # Gestión de base de datos
│   │   ├── handlers/           # Manejadores específicos por tipo
│   │   ├── ui/                 # Interfaz de usuario
│   │   │   ├── panels/         # Paneles modulares
│   │   │   ├── widgets/        # Componentes reutilizables
│   │   │   └── animation_helper.py  # Sistema de animaciones
│   │   └── utils/              # Utilidades y helpers
│   ├── resources/              # Recursos estáticos (CSS, iconos)
│   ├── tests/                  # Tests unitarios y de integración
│   ├── docs/                   # Documentación técnica
│   └── packaging/              # Scripts de empaquetado
└── README.md                   # Este archivo
```

## 🚀 Instalación y Uso

### Requisitos del Sistema
- **Sistema Operativo**: Linux con GNOME
- **Python**: 3.8 o superior
- **GTK**: 4.0 o superior
- **Dependencias**: Wine (para .exe), AppImageLauncher (opcional)

### Instalación Rápida
```bash
# Clonar el repositorio
git clone https://github.com/dotenv-l/gnome-dot-installer.git
cd gnome-dot-installer

# Instalar dependencias
cd dotInstaller
pip install -r requirements.txt

# Ejecutar la aplicación
python3 dotInstaller.py
```

### Instalación desde Fuentes
```bash
# Instalar dependencias del sistema
sudo apt update
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-4.0

# Instalar dependencias de Python
pip install -r requirements.txt

# Ejecutar
python3 dotInstaller.py
```

## 🎯 Módulos Principales

### 📦 **Core Installer** (`src/core/installer.py`)
- Orquestador principal de instalaciones
- Detección automática de tipos de paquete
- Gestión de dependencias y conflictos

### 🎨 **Animation Helper** (`src/ui/animation_helper.py`)
- Sistema centralizado de animaciones
- Efectos visuales: confeti, partículas, rebote
- Gestión automática de recursos de memoria

### 🖥 **UI Components** (`src/ui/`)
- **Main Window**: Ventana principal refactorizada
- **Sidebar**: Navegación lateral elegante
- **Panels**: Módulos independientes para cada funcionalidad
  - Store Panel: Tienda de aplicaciones
  - Library Panel: Gestión de instalaciones
  - Manual Panel: Instalador manual con drag & drop
  - Settings Panel: Configuración y registros

### 🔧 **Handlers Especializados** (`src/handlers/`)
- **AppImage Handler**: Gestión completa de AppImages
- **Deb Handler**: Instalación de paquetes .deb
- **Wine Handler**: Instalación de ejecutables Windows
- **Proton Handler**: Soporte para juegos con Proton
- **Script Handler**: Ejecución de scripts de instalación

## 🎨 Características de UX/UI

### **Diseño Visual**
- Paleta de colores Material Design
- Gradientes modernos y efectos de sombra
- Tipografía optimizada para legibilidad
- Iconografía consistente y clara

### **Animaciones y Efectos**
- Transiciones suaves entre paneles
- Animaciones de progreso durante instalación
- Efectos de celebración para instalaciones exitosas
- Feedback visual inmediato para todas las acciones

### **Accesibilidad**
- Soporte para tema oscuro automático
- Diseño responsivo para diferentes resoluciones
- Navegación por teclado completa
- Mensajes de error claros y útiles

## 🔧 Desarrollo y Extensión

### **Agregar Nuevos Tipos de Paquete**
1. Crear un nuevo handler en `src/handlers/`
2. Implementar la interfaz `BaseHandler`
3. Registrar el handler en `src/core/installer.py`
4. Actualizar la UI para soportar el nuevo tipo

### **Personalizar Animaciones**
```python
from src.ui.animation_helper import AnimationHelper

helper = AnimationHelper()
# Crear efectos personalizados
helper.create_custom_effect(widget, effect_type)
```

### **Agregar Nuevos Paneles**
1. Crear el panel en `src/ui/panels/`
2. Heredar de `Gtk.Box`
3. Registrar en `src/ui/main_window.py`
4. Agregar navegación en el sidebar

## 🧪 Testing

```bash
# Ejecutar tests unitarios
python -m pytest tests/

# Ejecutar tests de integración
python -m pytest tests/integration/

# Ejecutar tests de UI
python -m pytest tests/ui/
```

## 📚 Documentación

- **[README_APPIMAGES.md](dotInstaller/README_APPIMAGES.md)**: Documentación específica de AppImages
- **[APPIMAGE_IMPROVEMENTS.md](dotInstaller/APPIMAGE_IMPROVEMENTS.md)**: Mejoras y optimizaciones
- **[docs/](dotInstaller/docs/)**: Documentación técnica detallada

## 🤝 Contribución

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### **Guías de Contribución**
- Sigue las convenciones de código Python (PEP 8)
- Agrega tests para nuevas funcionalidades
- Actualiza la documentación según sea necesario
- Mantén la cobertura de código alta

## 📄 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- **GTK Team** por el framework de UI
- **GNOME Project** por el entorno de escritorio
- **Python Community** por el lenguaje de programación
- **Contribuidores** que han ayudado a mejorar el proyecto

## 📞 Soporte

- **Issues**: [GitHub Issues](https://github.com/dotenv-l/gnome-dot-installer/issues)
- **Discussions**: [GitHub Discussions](https://github.com/dotenv-l/gnome-dot-installer/discussions)
- **Email**: [Contacto del proyecto]

---

**Desarrollado con ❤️ para la comunidad Linux y GNOME**

[![GitHub stars](https://img.shields.io/github/stars/dotenv-l/gnome-dot-installer?style=social)](https://github.com/dotenv-l/gnome-dot-installer)
[![GitHub forks](https://img.shields.io/github/forks/dotenv-l/gnome-dot-installer?style=social)](https://github.com/dotenv-l/gnome-dot-installer)
[![GitHub issues](https://img.shields.io/github/issues/dotenv-l/gnome-dot-installer)](https://github.com/dotenv-l/gnome-dot-installer/issues)
