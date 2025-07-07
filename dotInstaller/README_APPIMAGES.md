# Soporte de AppImages en dotInstaller

## ¿Qué son las AppImages?

Las AppImages son aplicaciones portables que contienen todo lo necesario para ejecutarse en cualquier distribución Linux. Son similares a los archivos .exe en Windows o .app en macOS.

## ¿Dónde se instalan las AppImages?

Cuando instalas una AppImage con dotInstaller, se realiza lo siguiente:

### 1. **Directorio de instalación**
- **Ubicación**: `~/Applications/`
- **Propósito**: Almacena todos los archivos AppImage instalados
- **Ejemplo**: `~/Applications/mi-aplicacion.AppImage`

### 2. **Archivos .desktop**
- **Ubicación**: `~/.local/share/applications/`
- **Propósito**: Crea accesos directos en el menú de aplicaciones
- **Ejemplo**: `~/.local/share/applications/mi-aplicacion.desktop`

### 3. **Iconos**
- **Ubicación**: `~/.local/share/icons/`
- **Propósito**: Iconos de las aplicaciones para el menú
- **Ejemplo**: `~/.local/share/icons/mi-aplicacion.png`

## ¿Por qué no aparecen en la lista de aplicaciones?

Si una AppImage no aparece en la lista de aplicaciones después de la instalación, puede deberse a:

### 1. **Problemas de permisos**
```bash
# Verificar permisos del AppImage
ls -la ~/Applications/mi-aplicacion.AppImage

# Si no es ejecutable, hacerlo ejecutable
chmod +x ~/Applications/mi-aplicacion.AppImage
```

### 2. **Archivo .desktop no creado**
```bash
# Verificar si existe el archivo .desktop
ls -la ~/.local/share/applications/mi-aplicacion.desktop

# Si no existe, puede ser un problema de instalación
```

### 3. **Base de datos de aplicaciones no actualizada**
```bash
# Actualizar la base de datos de aplicaciones
update-desktop-database ~/.local/share/applications

# O reiniciar el shell
killall plasmashell && plasmashell &  # Para KDE
# O
gnome-shell --replace &  # Para GNOME
```

## Cómo desinstalar AppImages

### Desde dotInstaller:
1. Ve a la pestaña "Biblioteca"
2. Busca la aplicación AppImage
3. Haz clic en el botón de desinstalar (🗑️)

### Manualmente:
```bash
# Eliminar el archivo AppImage
rm ~/Applications/mi-aplicacion.AppImage

# Eliminar el archivo .desktop
rm ~/.local/share/applications/mi-aplicacion.desktop

# Eliminar el icono
rm ~/.local/share/icons/mi-aplicacion.png

# Actualizar base de datos
update-desktop-database ~/.local/share/applications
```

## Solución de problemas

### AppImage no se ejecuta:
```bash
# Verificar permisos
chmod +x ~/Applications/mi-aplicacion.AppImage

# Ejecutar desde terminal para ver errores
~/Applications/mi-aplicacion.AppImage
```

### AppImage no aparece en el menú:
```bash
# Verificar archivo .desktop
cat ~/.local/share/applications/mi-aplicacion.desktop

# Actualizar base de datos
update-desktop-database ~/.local/share/applications

# Reiniciar el shell de escritorio
```

### Error de dependencias:
```bash
# Instalar librerías necesarias
sudo apt-get install libfuse2

# O usar AppImageLauncher
sudo apt-get install appimagelauncher
```

## Estructura de directorios

```
~/
├── Applications/                    # AppImages instalados
│   ├── mi-app1.AppImage
│   └── mi-app2.AppImage
├── .local/
│   └── share/
│       ├── applications/           # Archivos .desktop
│       │   ├── mi-app1.desktop
│       │   └── mi-app2.desktop
│       └── icons/                  # Iconos
│           ├── mi-app1.png
│           └── mi-app2.png
└── .local/share/dotInstaller/      # Base de datos de dotInstaller
    └── dotinstaller.db
```

## Comandos útiles

```bash
# Listar AppImages instalados
ls ~/Applications/*.AppImage

# Listar archivos .desktop
ls ~/.local/share/applications/*.desktop

# Ver base de datos de dotInstaller
sqlite3 ~/.local/share/dotInstaller/dotinstaller.db "SELECT * FROM installed_apps WHERE type='appimage';"

# Actualizar caché de aplicaciones
update-desktop-database ~/.local/share/applications
```

## Notas importantes

1. **Portabilidad**: Las AppImages son portables y no requieren instalación tradicional
2. **Aislamiento**: Cada AppImage contiene sus propias dependencias
3. **Actualizaciones**: Las AppImages se actualizan descargando la nueva versión
4. **Seguridad**: Algunas AppImages pueden requerir permisos especiales

## Soporte

Si tienes problemas con AppImages específicas:

1. Verifica que el AppImage sea compatible con tu distribución
2. Revisa los logs de error ejecutando el AppImage desde terminal
3. Consulta la documentación oficial del AppImage
4. Reporta el problema en el repositorio de dotInstaller

# Mejoras Visuales y Animaciones en el Instalador Manual

A partir de la versión más reciente, el instalador manual de dotInstaller incluye:

- **Animaciones avanzadas** en los diálogos de instalación, éxito y error.
- **Efectos visuales** como confeti, partículas, rebote, temblor y desvanecimiento.
- **Helper de animaciones** (`src/ui/animation_helper.py`) para centralizar y facilitar la gestión de animaciones y efectos visuales.
- **UX/UI modernizada** con transiciones suaves, feedback visual inmediato y soporte para tema oscuro.
- **Código modular y fácil de extender**: puedes agregar nuevos efectos visuales reutilizando el helper.

## ¿Cómo funciona el AnimationHelper?

- El helper permite crear diálogos animados, efectos de confeti, partículas, rebote, fade, shake, ripple, typing y más.
- Todas las animaciones se gestionan y limpian automáticamente para optimizar recursos.
- Puedes usar el helper en cualquier panel o componente de la UI para mejorar la experiencia visual.

## Ejemplo de uso

```python
from src.ui.animation_helper import AnimationHelper
helper = AnimationHelper()
dialog, status_label, progress_bar = helper.create_animated_progress_dialog(
    "Instalando paquete", "Espere mientras se instala...", parent_window)
helper.start_progress_animation(progress_bar)
``` 