import os
import shutil
import stat
import subprocess
import sys


def sync_oci_config() -> None:
    source_dir = "/oci-host"
    target_dir = "/root/.oci"

    if not os.path.isdir(source_dir):
        return

    os.makedirs(target_dir, exist_ok=True)
    try:
        os.chmod(target_dir, 0o700)
    except OSError:
        pass

    for name in os.listdir(source_dir):
        src = os.path.join(source_dir, name)
        dst = os.path.join(target_dir, name)

        if os.path.isdir(src):
            if os.path.exists(dst):
                shutil.rmtree(dst)
            shutil.copytree(src, dst)
            for root, dirs, files in os.walk(dst):
                for d in dirs:
                    try:
                        os.chmod(os.path.join(root, d), 0o700)
                    except OSError:
                        pass
                for f in files:
                    try:
                        os.chmod(os.path.join(root, f), 0o600)
                    except OSError:
                        pass
            continue

        shutil.copy2(src, dst)
        try:
            os.chmod(dst, 0o600)
        except OSError:
            pass


def main() -> int:
    sync_oci_config()
    cmd = sys.argv[1:] or ["python", "run_server.py"]
    completed = subprocess.run(cmd)
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
