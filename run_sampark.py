#!/usr/bin/env python3
"""
SAMPARK Unified Launcher
Starts all backend services together for easy system operation.
"""

import os
import sys
import time
import signal
import subprocess
from pathlib import Path


# Color codes for terminal output
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.ENDC}\n")


def print_info(text):
    print(f"{Colors.OKBLUE}ℹ {text}{Colors.ENDC}")


def print_success(text):
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_warning(text):
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_error(text):
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


class ServiceManager:
    def __init__(self):
        self.processes = []
        self.base_dir = Path(__file__).parent.absolute()
        
    def start_backend(self):
        """Start Flask backend API"""
        print_info("Starting Flask Backend API...")
        backend_dir = self.base_dir / "backend"
        
        process = subprocess.Popen(
            [sys.executable, "app.py"],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        self.processes.append(("Backend API", process))
        print_success("Backend API started on http://127.0.0.1:5000")
        return process
    
    def start_dashboard(self):
        """Start Streamlit dashboard"""
        print_info("Starting Streamlit Dashboard...")
        dashboard_dir = self.base_dir / "dashboard"
        
        process = subprocess.Popen(
            [sys.executable, "-m", "streamlit", "run", "app.py", "--server.headless", "true"],
            cwd=dashboard_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        self.processes.append(("Dashboard", process))
        print_success("Dashboard started on http://localhost:8501")
        return process
    
    def start_wearable_simulator(self, mode="random", interval=10):
        """Start wearable simulator in live mode"""
        print_info(f"Starting Wearable Simulator (mode: {mode}, interval: {interval}s)...")
        simulator_dir = self.base_dir / "wearable_simulator"
        
        process = subprocess.Popen(
            [sys.executable, "simulator.py", "--live", "--mode", mode, "--interval", str(interval)],
            cwd=simulator_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            bufsize=1
        )
        self.processes.append(("Wearable Simulator", process))
        print_success(f"Wearable Simulator started (sending data every {interval}s)")
        return process
    
    def monitor_processes(self):
        """Monitor all running processes and display their output"""
        print_header("SAMPARK System Running")
        print_info("All services are now running. Press Ctrl+C to stop all services.\n")
        
        print(f"{Colors.OKCYAN}Service URLs:{Colors.ENDC}")
        print(f"  • Backend API:  http://127.0.0.1:5000")
        print(f"  • Dashboard:    http://localhost:8501")
        print(f"\n{Colors.OKCYAN}Available Services:{Colors.ENDC}")
        for name, _ in self.processes:
            print(f"  • {name}")
        print()
        
        try:
            while True:
                for name, process in self.processes:
                    if process.poll() is not None:
                        print_error(f"{name} has stopped unexpectedly!")
                        return False
                time.sleep(1)
        except KeyboardInterrupt:
            print(f"\n{Colors.WARNING}Shutting down all services...{Colors.ENDC}")
            return True
    
    def stop_all(self):
        """Stop all running processes"""
        for name, process in self.processes:
            try:
                print_info(f"Stopping {name}...")
                process.terminate()
                process.wait(timeout=5)
                print_success(f"{name} stopped")
            except subprocess.TimeoutExpired:
                print_warning(f"Force killing {name}...")
                process.kill()
                process.wait()
            except Exception as e:
                print_error(f"Error stopping {name}: {e}")
        
        self.processes.clear()
        print_success("All services stopped")


def check_dependencies():
    """Check if required dependencies are installed"""
    print_info("Checking dependencies...")
    
    required_modules = [
        ("flask", "Flask"),
        ("streamlit", "Streamlit"),
        ("sklearn", "scikit-learn"),
        ("requests", "requests"),
    ]
    
    missing = []
    for module, package in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(package)
    
    if missing:
        print_error("Missing required packages:")
        for package in missing:
            print(f"  • {package}")
        print(f"\n{Colors.WARNING}Install all dependencies with:{Colors.ENDC}")
        
        # Check if venv exists
        venv_path = Path(__file__).parent / "venv"
        if venv_path.exists():
            print(f"  source venv/bin/activate  # Activate virtual environment")
            print(f"  pip install -r requirements.txt\n")
        else:
            print(f"  python -m venv venv  # Create virtual environment")
            print(f"  source venv/bin/activate  # Activate it")
            print(f"  pip install -r requirements.txt\n")
        return False
    
    print_success("All dependencies are installed")
    return True


def main():
    print_header("SAMPARK - Smart Elderly Monitoring System")
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Parse command line arguments
    import argparse
    parser = argparse.ArgumentParser(description="Run SAMPARK unified system")
    parser.add_argument(
        "--no-simulator",
        action="store_true",
        help="Don't start the wearable simulator"
    )
    parser.add_argument(
        "--simulator-mode",
        choices=["normal", "warning", "random"],
        default="random",
        help="Wearable simulator mode (default: random)"
    )
    parser.add_argument(
        "--simulator-interval",
        type=int,
        default=10,
        help="Seconds between simulator data points (default: 10)"
    )
    args = parser.parse_args()
    
    manager = ServiceManager()
    
    try:
        # Start all services
        time.sleep(0.5)
        manager.start_backend()
        time.sleep(2)  # Give backend time to start
        
        manager.start_dashboard()
        time.sleep(1)
        
        if not args.no_simulator:
            manager.start_wearable_simulator(args.simulator_mode, args.simulator_interval)
            time.sleep(1)
        
        # Monitor processes
        manager.monitor_processes()
        
    except Exception as e:
        print_error(f"Error starting services: {e}")
    finally:
        manager.stop_all()
        print_header("SAMPARK System Stopped")


if __name__ == "__main__":
    main()
