#!/usr/bin/env python3
"""
Build Graham's Multiplication Blast as a standalone desktop app.

Usage:
    /home/owendoyaladastra/game-env/bin/python build_graham_math_app.py

Output:
    dist/GrahamsMultiplicationBlast
"""

import os
import shutil
import sys

import PyInstaller.__main__

APP_NAME = "GrahamsMultiplicationBlast"
APP_VERSION = "1.0.0"
MAIN_SCRIPT = "graham_multiplication_game.py"
ICON_FILE = "graham_math_icon.png"


def get_paths():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return {
        "script_dir": script_dir,
        "main_script": os.path.join(script_dir, MAIN_SCRIPT),
        "icon": os.path.join(script_dir, ICON_FILE),
        "dist_dir": os.path.join(script_dir, "dist"),
        "build_dir": os.path.join(script_dir, "build"),
    }


def clean(paths):
    for folder in (paths["build_dir"], paths["dist_dir"]):
        if os.path.exists(folder):
            print(f"Cleaning {folder}...")
            shutil.rmtree(folder)


def build():
    paths = get_paths()
    print("=" * 60)
    print(f"Building {APP_NAME} v{APP_VERSION}")
    print("=" * 60)

    if not os.path.exists(paths["main_script"]):
        print(f"Missing main script: {paths['main_script']}")
        sys.exit(1)

    clean(paths)

    args = [
        paths["main_script"],
        f"--name={APP_NAME}",
        "--onefile",
        "--windowed",
        "--clean",
        "--noconfirm",
        "--hidden-import=pygame",
        "--collect-submodules=pygame",
    ]

    if os.path.exists(paths["icon"]):
        args.append(f"--icon={paths['icon']}")
        print(f"Using icon: {paths['icon']}")
    else:
        print("No custom icon found; using default app icon.")

    print("\nRunning PyInstaller...")
    PyInstaller.__main__.run(args)

    exe_path = os.path.join(paths["dist_dir"], APP_NAME)
    print("\n" + "=" * 60)
    print("Build successful!")
    print("=" * 60)
    print(f"\nApp: {exe_path}")
    print("Progress saves to: ~/.graham_multiplication/progress.json")
    print("\nDouble-click the app, or run:")
    print(f"  {exe_path}")
    print("\nTo make it a login startup app, run:")
    print(f"  {os.path.join(paths['script_dir'], 'install_graham_startup.sh')}")


if __name__ == "__main__":
    build()