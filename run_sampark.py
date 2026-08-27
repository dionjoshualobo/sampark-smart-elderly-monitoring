#!/usr/bin/env python3
"""
SAMPARK Unified Launcher
Starts the whole system with one command:

    python run_sampark.py

This starts:
  1. Flask backend API        -> http://127.0.0.1:5000
  2. Care Dashboard           -> http://127.0.0.1:5000/dashboard
  3. Watch Simulator page     -> http://127.0.0.1:5000/watch
  4. Phone Voice page         -> http://127.0.0.1:5000/phone
  5. Background watch data feed (unless --no-watch)

Press Ctrl+C to stop everything.
"""

import argparse
import os
import socket
import subprocess
import sys
import threading
import time
import urllib.request
import webbrowser
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

REQUIRED_MODULES = [
    ("flask", "Flask"),
    ("flask_cors", "flask-cors"),
    ("sklearn", "scikit-learn"),
    ("requests", "requests"),
]


def log(message):
    print(f"[sampark] {message}", flush=True)


def check_dependencies():
    missing = []
    for module_name, package_name in REQUIRED_MODULES:
        try:
            __import__(module_name)
        except ImportError:
            missing.append(package_name)
    return missing


def install_dependencies(packages):
    log(f"Installing missing packages: {', '.join(packages)}")
    try:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", *packages],
            cwd=BASE_DIR,
        )
    except subprocess.CalledProcessError:
        log("Automatic install failed. Install manually with:")
        log(f"    pip install -r {BASE_DIR / 'requirements.txt'}")
        sys.exit(1)


def port_is_open(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(1)
        return sock.connect_ex((host, port)) == 0


def wait_for_backend(url, timeout_seconds=30):
    deadline = time.time() + timeout_seconds
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(url, timeout=2) as response:
                if response.status == 200:
                    return True
        except Exception:
            time.sleep(0.5)
    return False


def open_browser_when_ready(url):
    if wait_for_backend(url):
        webbrowser.open(url)
        log(f"Dashboard opened in your browser: {url}")
    else:
        log("Backend did not become ready in time; open the URL manually.")


def start_watch_feed(mode, interval):
    """Run the wearable simulator inside this process as a daemon thread."""
    simulator_dir = BASE_DIR / "wearable_simulator"
    if str(simulator_dir) not in sys.path:
        sys.path.insert(0, str(simulator_dir))

    import simulator as watch_simulator

    def feed_loop():
        wait_for_backend(os.environ["SAMPARK_BACKEND_URL"], timeout_seconds=60)
        watch_state = watch_simulator.WatchState()
        log(f"Watch feed running (mode={mode}, every {interval}s)")
        while True:
            steps = watch_state.next_steps(mode)
            data = watch_simulator.get_watch_data(mode, steps)
            try:
                record = watch_simulator.send_watch_data(data)
                watch_simulator.print_result(record)
            except Exception as error:
                print(f"[watch] Could not send reading: {error}", flush=True)
            time.sleep(interval)

    thread = threading.Thread(target=feed_loop, daemon=True)
    thread.start()


def start_streamlit_dashboard(port):
    dashboard_dir = BASE_DIR / "dashboard"
    try:
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "streamlit",
                "run",
                "app.py",
                "--server.headless",
                "true",
                "--server.port",
                "8501",
            ],
            cwd=dashboard_dir,
        )
        log("Streamlit dashboard starting on http://localhost:8501")
        return process
    except Exception as error:
        log(f"Could not start Streamlit ({error}). Install extras: pip install -r requirements-full.txt")
        return None


def reset_database():
    db_path = BASE_DIR / "backend" / "sampark.db"
    if db_path.exists():
        db_path.unlink()
        log(f"Cleared database: {db_path}")
    else:
        log("Database already empty")


def parse_args():
    parser = argparse.ArgumentParser(description="Run the complete SAMPARK system with one command.")
    parser.add_argument("--no-watch", action="store_true", help="Do not start the background wearable data feed")
    parser.add_argument("--mode", choices=["normal", "warning", "random"], default="random",
                        help="Background watch feed data mode (default: random)")
    parser.add_argument("--interval", type=int, default=10, help="Seconds between background watch readings (default: 10)")
    parser.add_argument("--port", type=int, default=5000, help="Backend port (default: 5000)")
    parser.add_argument("--no-browser", action="store_true", help="Do not auto-open the dashboard in a browser")
    parser.add_argument("--streamlit", action="store_true", help="Also start the optional Streamlit dashboard")
    parser.add_argument("--reset-db", action="store_true", help="Delete all saved records and alerts before starting")
    return parser.parse_args()


def main():
    args = parse_args()

    print()
    print("=" * 62)
    print("SAMPARK - Smart Elderly Monitoring System".center(62))
    print("=" * 62)
    print()

    missing = check_dependencies()
    if missing:
        install_dependencies(missing)

    if args.reset_db:
        reset_database()

    host = "127.0.0.1"
    if port_is_open(host, args.port):
        log(f"Port {args.port} is already in use (is SAMPARK already running?)")
        log(f"Try: http://{host}:{args.port}/dashboard  or stop the other program first.")
        sys.exit(1)

    # Make sure every part of the app talks to the same backend URL
    os.environ["SAMPARK_BACKEND_URL"] = f"http://{host}:{args.port}"

    if not args.no_watch:
        start_watch_feed(args.mode, max(args.interval, 3))

    streamlit_process = None
    if args.streamlit:
        streamlit_process = start_streamlit_dashboard(args.port)

    if not args.no_browser:
        threading.Thread(
            target=open_browser_when_ready,
            args=(f"http://{host}:{args.port}/dashboard",),
            daemon=True,
        ).start()

    sys.path.insert(0, str(BASE_DIR / "backend"))
    from app import app  # noqa: E402

    print()
    log(f"Backend API      : http://{host}:{args.port}")
    log(f"Care Dashboard   : http://{host}:{args.port}/dashboard")
    log(f"Watch Simulator  : http://{host}:{args.port}/watch")
    log(f"Phone Voice      : http://{host}:{args.port}/phone")
    log("Press Ctrl+C to stop everything.")
    print()

    try:
        app.run(host="0.0.0.0", port=args.port, debug=False, use_reloader=False)
    except KeyboardInterrupt:
        pass
    finally:
        if streamlit_process:
            streamlit_process.terminate()
        print()
        log("SAMPARK stopped. Goodbye!")


if __name__ == "__main__":
    main()
