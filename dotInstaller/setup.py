from setuptools import setup, find_packages

setup(
    name="dotInstaller",
    version="0.1.0",
    description="Instalador universal para sistemas Debian con interfaz GNOME",
    author="Tu Nombre",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=["PyGObject"],
    entry_points={
        "gui_scripts": [
            "dotInstaller = dotInstaller:main"
        ]
    },
) 