import platform
import subprocess
from venv import logger

def compile_translates(if_compile):
    if if_compile:
        if platform.system() == "Windows":
            subprocess.run(["cmd", "/c", "pybabel compile -d locales -D vt-print"])
        else:
            subprocess.run(["sh", "./3_compile_translates.sh"])
        print("Translates compiled")
