#!/usr/bin/env python3
"""
FrameWorkers 环境安装脚本。
默认会：
1) 创建 conda 环境 ``frameworkers``（已存在则跳过创建）
2) 在该环境内 pip 安装根目录 ``requirements.txt`` + 测试依赖（pytest）

兼容性：
- 优先使用 ``conda run --no-banner``；若 conda 版本不支持该参数，自动回退为不带 ``--no-banner``。

用法（推荐先激活目标环境，再执行脚本；此时无需 ``conda`` 在 PATH 上）::

    conda activate frameworkers
    python install_requirements.py

说明：
- 默认会安装 ``pytest``，无需额外参数。
- 若当前已 ``conda activate frameworkers``，直接用当前解释器执行 ``pip install``，不依赖 ``conda run``。
- 否则使用环境变量 ``CONDA_EXE`` 或 PATH 中的 ``conda`` 做 ``conda run`` / ``conda create``。
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

ENV_NAME = "frameworkers"
PYTHON_VERSION = "3.11"
TEST_PACKAGES = ["pytest"]


def _conda_executable() -> str | None:
    """``conda`` binary: ``CONDA_EXE`` (set after ``conda activate``) or PATH."""
    exe = os.environ.get("CONDA_EXE")
    if exe and Path(exe).is_file():
        return exe
    return shutil.which("conda")


def _running_inside_conda_env(env_name: str) -> bool:
    """True if the current interpreter is already that named conda env."""
    if os.environ.get("CONDA_DEFAULT_ENV") == env_name:
        return True
    prefix = os.environ.get("CONDA_PREFIX")
    if prefix and Path(prefix).name == env_name:
        return True
    return False


def conda_env_exists(env_name: str) -> bool:
    """Return True if a conda environment already exists (or we are already inside it)."""
    if _running_inside_conda_env(env_name):
        return True
    conda_exe = _conda_executable()
    if not conda_exe:
        return False
    try:
        result = subprocess.run(
            [conda_exe, "env", "list", "--json"],
            check=True,
            capture_output=True,
            text=True,
        )
        data = json.loads(result.stdout or "{}")
        envs = data.get("envs", [])
        for raw in envs:
            if Path(str(raw)).name == env_name:
                return True
            if str(raw).replace("\\", "/").endswith(f"/envs/{env_name}"):
                return True
        return False
    except Exception:
        return False


def install_requirements_into_target_env(env_name: str, args: list[str]) -> None:
    """
    Run ``pip install <args>`` inside ``env_name``.

    If the active interpreter is already that env (e.g. after ``conda activate frameworkers``),
    use ``sys.executable -m pip`` so we never need ``conda`` on PATH.

    Otherwise use ``conda run -n <env> pip install ...`` with ``CONDA_EXE`` or ``conda``.
    """
    if _running_inside_conda_env(env_name):
        subprocess.run([sys.executable, "-m", "pip", "install", *args], check=True)
        return

    conda_exe = _conda_executable()
    if not conda_exe:
        print(
            "找不到 conda（且当前不在目标环境中）。请先执行：\n"
            f"  conda activate {env_name}\n"
            "或确保已安装 conda 并加入 PATH，或设置环境变量 CONDA_EXE。",
            file=sys.stderr,
        )
        raise SystemExit(1)

    cmd_with_banner_flag = [
        conda_exe,
        "run",
        "-n",
        env_name,
        "--no-banner",
        "pip",
        "install",
        *args,
    ]
    try:
        subprocess.run(
            cmd_with_banner_flag,
            check=True,
            capture_output=True,
            text=True,
        )
        return
    except subprocess.CalledProcessError as exc:
        err = (exc.stderr or "") + (exc.stdout or "")
        if "--no-banner" not in err:
            raise
        print("Detected older conda: retrying pip install without --no-banner ...")

    subprocess.run(
        [conda_exe, "run", "-n", env_name, "pip", "install", *args],
        check=True,
    )


def main() -> int:
    if "--help" in sys.argv or "-h" in sys.argv:
        print(
            "Usage:\n"
            "  python install_requirements.py    # one-click install (env + deps + pytest)\n"
        )
        return 0

    requirements_file = Path(__file__).resolve().parent / "requirements.txt"
    if not requirements_file.is_file():
        print(f"requirements.txt not found at {requirements_file}", file=sys.stderr)
        return 1

    if conda_env_exists(ENV_NAME):
        print(f"Conda env '{ENV_NAME}' already exists, skipping create.")
    else:
        conda_exe = _conda_executable()
        if not conda_exe:
            print(
                "目标环境不存在，且找不到 conda 可执行文件。请先：\n"
                f"  conda create -n {ENV_NAME} python={PYTHON_VERSION} -y\n"
                f"  conda activate {ENV_NAME}\n"
                "然后重新运行本脚本。",
                file=sys.stderr,
            )
            return 1
        print(f"\nCreating conda env '{ENV_NAME}' (python={PYTHON_VERSION}) …")
        try:
            subprocess.run(
                [conda_exe, "create", "-n", ENV_NAME, f"python={PYTHON_VERSION}", "-y"],
                check=True,
            )
        except subprocess.CalledProcessError as exc:
            print(f"conda create failed (exit {exc.returncode})", file=sys.stderr)
            return 1

    if _running_inside_conda_env(ENV_NAME):
        print(f"\nInstalling from {requirements_file.name} into current env (active: {ENV_NAME}) …")
    else:
        print(f"\nInstalling from {requirements_file.name} into '{ENV_NAME}' …")
    try:
        install_requirements_into_target_env(ENV_NAME, ["-r", str(requirements_file)])
    except subprocess.CalledProcessError as exc:
        print(f"pip install failed (exit {exc.returncode})", file=sys.stderr)
        return 1

    print(f"\nInstalling test packages into '{ENV_NAME}' …")
    try:
        install_requirements_into_target_env(ENV_NAME, TEST_PACKAGES)
    except subprocess.CalledProcessError as exc:
        print(f"test package install failed (exit {exc.returncode})", file=sys.stderr)
        return 1

    print(f"\nDone! Run:\n  conda activate {ENV_NAME}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
