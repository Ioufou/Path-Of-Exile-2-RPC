import logging
import sys
import subprocess
from pathlib import Path

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

def create_launch_bat():
    bat_path = Path("launch_poe2_with_rpc.bat")

    pythonw_path = str(Path(sys.executable).parent / "pythonw.exe")
    script_path = Path(__file__).resolve().parent / "main.py"
    steam_path = r"C:\Program Files (x86)\Steam\steam.exe"
    poe2_appid = "2694490"

    content = f'''@echo off
start "" "{pythonw_path}" "{script_path}"
start "" "{steam_path}" -applaunch {poe2_appid}
exit
'''

    with open(bat_path, "w", encoding="utf-8") as f:
        f.write(content)

    logging.info(f".bat file generated : {bat_path}")
    return bat_path


def build_exe_from_bat(bat_path: Path):
    launcher_code = f"""import subprocess, sys, os

bat_file = r"{bat_path.resolve()}"
subprocess.Popen(["cmd", "/c", bat_file], creationflags=subprocess.CREATE_NEW_CONSOLE)
"""

    launcher_py = Path("launcher.py")
    launcher_py.write_text(launcher_code, encoding="utf-8")

    logging.info("Building exe with PyInstaller...")

    subprocess.run([
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--noconsole",
        "--distpath", str(Path().resolve()),
        str(launcher_py)
    ], check=True)

    logging.info("✅ Executable generated : launcher.exe")


if __name__ == "__main__":
    bat_file = create_launch_bat()
    build_exe_from_bat(bat_file)
