from cx_Freeze import setup, Executable
import sys
import os

# Inclui o arquivo de configuração JSON
include_files = ["config.json"]

# Dependências extras que o cx_Freeze pode não detectar automaticamente
build_exe_options = {
    "packages": ["tkinter", "pyautogui", "pynput", "keyboard", "json"],
    "include_files": include_files,
    "excludes": ["unittest", "email", "html", "http", "xmlrpc"],
}

# Define o caminho para o Python no Windows (apenas se necessário)
base = None
if sys.platform == "win32":
    base = "Win32GUI"  # remove o terminal (útil para apps com GUI)

setup(
    name="Clicador",
    version="1.0",
    description="App de clique automático com gravação de ações",
    options={"build_exe": build_exe_options},
    executables=[Executable("app.py", base=base)],
)
