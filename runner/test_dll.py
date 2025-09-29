import ctypes
import os

# Caminho absoluto da DLL
dll_path = os.path.join(os.path.dirname(__file__), "dll_commands", "hello.dll")

# Carrega a DLL
hello_dll = ctypes.CDLL(dll_path)

# Chama a função run() da DLL
hello_dll.run()
