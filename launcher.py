import subprocess, sys, os

bat_file = r"C:\Users\frntl\Documents\Path-Of-Exile-2-RPC\launch_poe2_with_rpc.bat"
subprocess.Popen(["cmd", "/c", bat_file], creationflags=subprocess.CREATE_NEW_CONSOLE)
