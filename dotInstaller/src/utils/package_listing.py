import subprocess
import os
import glob
import configparser
import shlex

def list_installed_packages():
    # Obtiene la lista de paquetes instalados usando dpkg-query
    result = subprocess.run([
        'dpkg-query', '-W', '-f=${Package}\n'
    ], capture_output=True, text=True)
    packages = result.stdout.strip().split('\n')
    return packages

def get_desktop_entries():
    # Busca archivos .desktop en ubicaciones estándar
    desktop_dirs = [
        os.path.expanduser('~/.local/share/applications/'),
        '/usr/share/applications/'
    ]
    entries = []
    for d in desktop_dirs:
        entries.extend(glob.glob(os.path.join(d, '*.desktop')))
    return entries

def parse_desktop_entry(path):
    config = configparser.ConfigParser(interpolation=None)
    config.read(path)
    if 'Desktop Entry' in config:
        entry = config['Desktop Entry']
        return {
            'name': entry.get('Name', ''),
            'exec': entry.get('Exec', ''),
            'icon': entry.get('Icon', ''),
            'categories': entry.get('Categories', ''),
            'comment': entry.get('Comment', ''),
            'path': path
        }
    return None

def get_package_name_from_exec(exec_path):
    # Quitar argumentos y buscar el ejecutable real
    exec_bin = shlex.split(exec_path)[0] if exec_path else ''
    if not exec_bin:
        return None
    # Buscar el paquete usando dpkg -S
    result = subprocess.run(['dpkg', '-S', exec_bin], capture_output=True, text=True)
    if result.returncode == 0:
        # Salida: paquete: ruta
        pkg = result.stdout.split(':')[0].strip()
        return pkg
    return None

def get_package_critical_info(package):
    # Verifica si el paquete es esencial o requerido (más rápido)
    result = subprocess.run([
        'dpkg-query', '-W', '-f=${Essential} ${Priority}\n', package
    ], capture_output=True, text=True)
    essential = False
    priority_required = False
    if result.returncode == 0:
        fields = result.stdout.strip().split()
        if len(fields) >= 2:
            essential = (fields[0].lower() == 'yes')
            priority_required = (fields[1].lower() == 'required')
    # Solo verificar dependencias reverse para paquetes críticos
    reverse_deps = []
    if essential or priority_required:
        result_r = subprocess.run([
            'apt-cache', 'rdepends', '--installed', package
        ], capture_output=True, text=True)
        if result_r.returncode == 0:
            lines = result_r.stdout.strip().split('\n')[1:]
            reverse_deps = [l.strip() for l in lines if l.strip() and l.strip() != package]
    return {
        'essential': essential,
        'priority_required': priority_required,
        'reverse_dependencies': reverse_deps
    }

def map_packages_to_desktop_entries():
    desktop_entries = get_desktop_entries()
    parsed_entries = [parse_desktop_entry(e) for e in desktop_entries]
    parsed_entries = [e for e in parsed_entries if e and e['exec']]
    seen = set()
    package_map = []
    for entry in parsed_entries:
        pkg = get_package_name_from_exec(entry['exec'])
        exec_bin = shlex.split(entry['exec'])[0] if entry['exec'] else ''
        is_appimage = exec_bin.endswith('.AppImage') or exec_bin.endswith('.appimage')
        # Detectar tipo wine/proton
        entry_type = ''
        if 'wine' in exec_bin:
            entry_type = 'wine'
        elif 'proton' in exec_bin:
            entry_type = 'proton'
        if (pkg and pkg not in seen) or is_appimage or entry_type:
            if pkg:
                seen.add(pkg)
            # Info crítica solo para paquetes dpkg
            critical_info = get_package_critical_info(pkg) if pkg else {'essential': False, 'priority_required': False, 'reverse_dependencies': []}
            package_map.append({
                'package': pkg if pkg else exec_bin,
                'name': entry['name'],
                'icon': entry['icon'],
                'categories': entry['categories'],
                'comment': entry['comment'],
                'desktop': entry['path'],
                'essential': critical_info['essential'],
                'priority_required': critical_info['priority_required'],
                'reverse_dependencies': critical_info['reverse_dependencies'],
                'type': entry_type
            })
    return package_map 