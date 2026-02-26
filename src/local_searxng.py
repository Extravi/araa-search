import json
import os
import secrets
import shutil
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

import _config as config


LOCAL_SEARXNG_ENABLED = getattr(config, "LOCAL_SEARXNG_ENABLED", True)
LOCAL_SEARXNG_IMAGE = getattr(config, "LOCAL_SEARXNG_IMAGE", "docker.io/searxng/searxng:latest")
LOCAL_SEARXNG_CONTAINER_NAME = getattr(config, "LOCAL_SEARXNG_CONTAINER_NAME", "araa-local-searxng")
LOCAL_SEARXNG_HOST = getattr(config, "LOCAL_SEARXNG_HOST", "127.0.0.1")
LOCAL_SEARXNG_PORT = getattr(config, "LOCAL_SEARXNG_PORT", 8081)
LOCAL_SEARXNG_STATE_DIR = getattr(config, "LOCAL_SEARXNG_STATE_DIR", ".searxng_local")
LOCAL_SEARXNG_KEEP_ONLY_ENGINES = getattr(config, "LOCAL_SEARXNG_KEEP_ONLY_ENGINES", ["google", "google images", "qwant", "qwant images", "wikipedia"])
LOCAL_SEARXNG_AUTO_UPDATE = getattr(config, "LOCAL_SEARXNG_AUTO_UPDATE", True)
LOCAL_SEARXNG_AUTO_UPDATE_COOLDOWN_SECONDS = getattr(config, "LOCAL_SEARXNG_AUTO_UPDATE_COOLDOWN_SECONDS", 300)
LOCAL_SEARXNG_STARTUP_TIMEOUT_SECONDS = getattr(config, "LOCAL_SEARXNG_STARTUP_TIMEOUT_SECONDS", 45)


def _run(cmd, capture=False, check=True):
    return subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE if capture else None,
        stderr=subprocess.STDOUT if capture else None,
        check=check,
    )


def _docker(cmd, capture=True, check=False):
    return _run(["docker"] + cmd, capture=capture, check=check)


def _docker_available():
    return shutil.which("docker") is not None


def _parse_int(val, fallback=None):
    try:
        return int(val)
    except Exception:
        return fallback


def _port_is_used(host, port):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(0.35)
            return sock.connect_ex((host, port)) == 0
    except Exception:
        return False


def _preferred_host_port():
    preferred = _parse_int(LOCAL_SEARXNG_PORT, 8081)
    if preferred is None or preferred < 1 or preferred > 65535:
        preferred = 8081

    # Never bind local searxng to the same default app port.
    excluded = {8000, getattr(config, "PORT", 8000)}
    if preferred in excluded:
        preferred = 8081
    return preferred


def _pick_host_port():
    preferred = _preferred_host_port()
    excluded = {8000, getattr(config, "PORT", 8000)}
    if not _port_is_used(LOCAL_SEARXNG_HOST, preferred):
        return preferred

    for port in range(preferred + 1, preferred + 2000):
        if port in excluded:
            continue
        if not _port_is_used(LOCAL_SEARXNG_HOST, port):
            return port

    # Last fallback: ask OS for an ephemeral free port, but still avoid excluded ones.
    while True:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((LOCAL_SEARXNG_HOST, 0))
            free_port = int(s.getsockname()[1])
        if free_port not in excluded:
            return free_port


def _repo_root():
    return Path(__file__).resolve().parent.parent


def _state_dir():
    raw = str(LOCAL_SEARXNG_STATE_DIR).strip()
    if raw == "":
        raw = ".searxng_local"
    base = Path(raw)
    if not base.is_absolute():
        base = _repo_root() / base
    return base


def _normalize_keep_only_engines():
    raw = LOCAL_SEARXNG_KEEP_ONLY_ENGINES
    if isinstance(raw, (list, tuple)):
        engines = [str(engine).strip() for engine in raw if str(engine).strip() != ""]
        return engines or ["google", "google images", "qwant", "qwant images", "wikipedia"]

    if isinstance(raw, str):
        val = raw.strip()
        if val == "":
            return ["google", "google images", "qwant", "qwant images", "wikipedia"]
        try:
            parsed = json.loads(val)
            if isinstance(parsed, list):
                engines = [str(engine).strip() for engine in parsed if str(engine).strip() != ""]
                return engines or ["google", "google images", "qwant", "qwant images", "wikipedia"]
        except Exception:
            pass

        engines = [engine.strip() for engine in val.split(",") if engine.strip() != ""]
        return engines or ["google", "google images", "qwant", "qwant images", "wikipedia"]

    return ["google", "google images", "qwant", "qwant images", "wikipedia"]


def _ensure_secret_key(path):
    if path.exists():
        secret = path.read_text(encoding="utf-8").strip()
        if secret != "":
            return secret

    secret = secrets.token_hex(24)
    path.write_text(secret, encoding="utf-8")
    return secret


def _render_settings(secret_key):
    engines = _normalize_keep_only_engines()
    engine_lines = "\n".join([f"      - {engine}" for engine in engines])
    return (
        "use_default_settings:\n"
        "  engines:\n"
        "    keep_only:\n"
        f"{engine_lines}\n\n"
        "server:\n"
        f"  secret_key: \"{secret_key}\"\n"
        "  limiter: false\n"
        "  public_instance: false\n\n"
        "search:\n"
        "  formats:\n"
        "    - html\n"
        "    - json\n"
    )


def _write_if_changed(path, content):
    old = ""
    if path.exists():
        old = path.read_text(encoding="utf-8")
    if old == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def _acquire_lock(lock_path, timeout_seconds=60):
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            fd = os.open(str(lock_path), os.O_CREAT | os.O_EXCL | os.O_RDWR)
            os.write(fd, str(os.getpid()).encode("utf-8"))
            return fd
        except FileExistsError:
            # Remove stale locks so startup does not get stuck forever.
            try:
                age = time.time() - lock_path.stat().st_mtime
                if age > timeout_seconds + 30:
                    lock_path.unlink(missing_ok=True)
                    continue
            except Exception:
                pass
            time.sleep(0.2)
        except Exception:
            return None
    return None


def _release_lock(fd, lock_path):
    if fd is not None:
        try:
            os.close(fd)
        except Exception:
            pass
    try:
        lock_path.unlink(missing_ok=True)
    except Exception:
        pass


def _inspect_container(name):
    response = _docker(["inspect", name], capture=True, check=False)
    if response.returncode != 0:
        return None
    try:
        payload = json.loads(response.stdout)
        if not payload:
            return None
        return payload[0]
    except Exception:
        return None


def _inspect_image_id(image):
    response = _docker(["image", "inspect", image], capture=True, check=False)
    if response.returncode != 0:
        return None
    try:
        payload = json.loads(response.stdout)
        if not payload:
            return None
        return payload[0].get("Id")
    except Exception:
        return None


def _container_binding(container):
    if container is None:
        return (None, None)
    ports = container.get("NetworkSettings", {}).get("Ports", {})
    binding = ports.get("8080/tcp")
    if not isinstance(binding, list) or len(binding) == 0:
        return (None, None)
    host_ip = binding[0].get("HostIp")
    host_port = _parse_int(binding[0].get("HostPort"), None)
    return (host_ip, host_port)


def _remove_container(name):
    _docker(["rm", "-f", name], capture=True, check=False)


def _start_container(name, image, host_port, config_dir, data_dir):
    cmd = [
        "run",
        "-d",
        "--name",
        name,
        "--restart",
        "unless-stopped",
        "-p",
        f"{LOCAL_SEARXNG_HOST}:{host_port}:8080",
        "-v",
        f"{config_dir}:/etc/searxng",
        "-v",
        f"{data_dir}:/var/cache/searxng",
        image,
    ]
    response = _docker(cmd, capture=True, check=False)
    if response.returncode == 0:
        return True

    stdout = (response.stdout or "").lower()
    if "port is already allocated" in stdout or "already in use" in stdout:
        return False

    print("[local_searxng] ERROR: Failed to create local searxng container.")
    if response.stdout:
        print(response.stdout)
    return None


def _http_ok(url, timeout_s=2.0):
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout_s) as resp:
            return 200 <= resp.status < 500
    except Exception:
        return False


def _wait_ready(base_url):
    deadline = time.time() + float(LOCAL_SEARXNG_STARTUP_TIMEOUT_SECONDS)
    while time.time() < deadline:
        if _http_ok(base_url + "/"):
            return True
        time.sleep(0.5)
    return False


def _should_pull(pull_marker):
    if not LOCAL_SEARXNG_AUTO_UPDATE:
        return False

    if not pull_marker.exists():
        return True

    cooldown = _parse_int(LOCAL_SEARXNG_AUTO_UPDATE_COOLDOWN_SECONDS, 300)
    if cooldown is None or cooldown < 0:
        cooldown = 300

    try:
        age = time.time() - pull_marker.stat().st_mtime
    except Exception:
        return True
    return age >= cooldown


def ensure_local_searxng():
    if not LOCAL_SEARXNG_ENABLED:
        return None

    if not _docker_available():
        print("[local_searxng] WARN: docker is not installed or not available in PATH. Skipping local searxng startup.")
        return None

    try:
        state_dir = _state_dir()
        config_dir = state_dir / "config"
        data_dir = state_dir / "data"
        lock_path = state_dir / "bootstrap.lock"
        pull_marker = state_dir / "last_pull"

        config_dir.mkdir(parents=True, exist_ok=True)
        data_dir.mkdir(parents=True, exist_ok=True)

        lock_fd = _acquire_lock(lock_path, timeout_seconds=90)
        if lock_fd is None:
            print("[local_searxng] WARN: Could not acquire startup lock. Skipping bootstrap for this worker.")
            return None

        try:
            # Keep a stable secret key so container restarts stay predictable.
            secret_path = config_dir / "secret_key"
            settings_path = config_dir / "settings.yml"
            secret = _ensure_secret_key(secret_path)
            settings_changed = _write_if_changed(settings_path, _render_settings(secret))

            if _should_pull(pull_marker):
                pull_result = _docker(["pull", LOCAL_SEARXNG_IMAGE], capture=True, check=False)
                pull_marker.touch()
                if pull_result.returncode != 0:
                    print("[local_searxng] WARN: Could not pull latest searxng image. Continuing with current local image.")
                    if pull_result.stdout:
                        print(pull_result.stdout)

            latest_image_id = _inspect_image_id(LOCAL_SEARXNG_IMAGE)
            container = _inspect_container(LOCAL_SEARXNG_CONTAINER_NAME)
            desired_port = _preferred_host_port()
            running = False
            host_port = desired_port
            needs_recreate = False

            if container is not None:
                running = bool(container.get("State", {}).get("Running", False))
                container_image_id = container.get("Image")
                host_ip, current_port = _container_binding(container)

                if current_port is not None:
                    host_port = current_port

                if latest_image_id and container_image_id and latest_image_id != container_image_id:
                    needs_recreate = True

                if settings_changed:
                    needs_recreate = True

                if host_ip not in ["127.0.0.1", "::1"]:
                    needs_recreate = True

                if current_port in [None, 8000, getattr(config, "PORT", 8000)]:
                    needs_recreate = True

            if needs_recreate and container is not None:
                print("[local_searxng] INFO: Recreating local searxng container.")
                _remove_container(LOCAL_SEARXNG_CONTAINER_NAME)
                container = None
                running = False
                host_port = desired_port

            if container is None:
                create_result = _start_container(
                    LOCAL_SEARXNG_CONTAINER_NAME,
                    LOCAL_SEARXNG_IMAGE,
                    host_port,
                    config_dir,
                    data_dir,
                )

                if create_result is False:
                    host_port = _pick_host_port()
                    create_result = _start_container(
                        LOCAL_SEARXNG_CONTAINER_NAME,
                        LOCAL_SEARXNG_IMAGE,
                        host_port,
                        config_dir,
                        data_dir,
                    )

                if create_result is None or create_result is False:
                    print("[local_searxng] ERROR: Could not start local searxng container.")
                    return None

                running = True

            elif not running:
                start_result = _docker(["start", LOCAL_SEARXNG_CONTAINER_NAME], capture=True, check=False)
                if start_result.returncode != 0:
                    print("[local_searxng] WARN: Existing local searxng container failed to start. Recreating it.")
                    _remove_container(LOCAL_SEARXNG_CONTAINER_NAME)
                    create_result = _start_container(
                        LOCAL_SEARXNG_CONTAINER_NAME,
                        LOCAL_SEARXNG_IMAGE,
                        host_port,
                        config_dir,
                        data_dir,
                    )
                    if create_result is False:
                        host_port = _pick_host_port()
                        create_result = _start_container(
                            LOCAL_SEARXNG_CONTAINER_NAME,
                            LOCAL_SEARXNG_IMAGE,
                            host_port,
                            config_dir,
                            data_dir,
                        )
                    if create_result is None or create_result is False:
                        print("[local_searxng] ERROR: Could not recreate local searxng container.")
                        return None
                running = True

            container = _inspect_container(LOCAL_SEARXNG_CONTAINER_NAME)
            _, mapped_port = _container_binding(container)
            if mapped_port is not None:
                host_port = mapped_port

            base_url = f"http://{LOCAL_SEARXNG_HOST}:{host_port}"
            if not _wait_ready(base_url):
                print("[local_searxng] WARN: Local searxng container started, but readiness check timed out.")
            else:
                print(f"[local_searxng] Ready at {base_url}")

            os.environ["ARAA_LOCAL_SEARXNG_URL"] = base_url
            os.environ["ARAA_LOCAL_SEARXNG_PORT"] = str(host_port)
            return {
                "base_url": base_url,
                "port": host_port,
                "container_name": LOCAL_SEARXNG_CONTAINER_NAME,
                "image": LOCAL_SEARXNG_IMAGE,
            }
        finally:
            _release_lock(lock_fd, lock_path)
    except Exception as e:
        print(f"[local_searxng] WARN: Failed to bootstrap local searxng: {e}")
        return None
