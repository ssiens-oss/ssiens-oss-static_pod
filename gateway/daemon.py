#!/usr/bin/env python3
"""
POD Gateway Daemon
Runs the Flask application as a background daemon process
"""
import os
import sys
import signal
import time
import logging
from pathlib import Path
import subprocess
import atexit

# Add app directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

PIDFILE = '/tmp/pod-gateway.pid'
LOGFILE = '/var/log/pod-gateway.log'


class Daemon:
    """Daemon base class"""

    def __init__(self, pidfile):
        self.pidfile = pidfile
        self.setup_logging()

    def setup_logging(self):
        """Setup logging to file"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(LOGFILE),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger('PODGatewayDaemon')

    def daemonize(self):
        """Daemonize the process using double-fork technique"""
        try:
            # First fork
            pid = os.fork()
            if pid > 0:
                # Exit parent
                sys.exit(0)
        except OSError as e:
            self.logger.error(f"First fork failed: {e}")
            sys.exit(1)

        # Decouple from parent environment
        os.chdir('/')
        os.setsid()
        os.umask(0)

        try:
            # Second fork
            pid = os.fork()
            if pid > 0:
                # Exit second parent
                sys.exit(0)
        except OSError as e:
            self.logger.error(f"Second fork failed: {e}")
            sys.exit(1)

        # Redirect standard file descriptors
        sys.stdout.flush()
        sys.stderr.flush()

        # Write pidfile
        atexit.register(self.delpid)
        pid = str(os.getpid())
        with open(self.pidfile, 'w+') as f:
            f.write(f"{pid}\n")

    def delpid(self):
        """Delete PID file"""
        if os.path.exists(self.pidfile):
            os.remove(self.pidfile)

    def start(self):
        """Start the daemon"""
        self.logger.info("Starting POD Gateway daemon...")

        # Check if already running
        if os.path.exists(self.pidfile):
            with open(self.pidfile, 'r') as f:
                pid = int(f.read().strip())

            try:
                os.kill(pid, 0)
                self.logger.error(f"Daemon already running with PID {pid}")
                sys.exit(1)
            except OSError:
                # Process doesn't exist, remove stale pidfile
                os.remove(self.pidfile)

        # Daemonize
        self.daemonize()

        # Run the application
        self.run()

    def stop(self):
        """Stop the daemon"""
        self.logger.info("Stopping POD Gateway daemon...")

        if not os.path.exists(self.pidfile):
            self.logger.error("Daemon not running (no pidfile)")
            return

        with open(self.pidfile, 'r') as f:
            pid = int(f.read().strip())

        try:
            # Send SIGTERM
            os.kill(pid, signal.SIGTERM)
            time.sleep(1)

            # Check if still running
            try:
                os.kill(pid, 0)
                # Still running, send SIGKILL
                self.logger.warning("Process didn't stop, sending SIGKILL")
                os.kill(pid, signal.SIGKILL)
            except OSError:
                pass

            # Remove pidfile
            if os.path.exists(self.pidfile):
                os.remove(self.pidfile)

            self.logger.info("Daemon stopped")
        except OSError as e:
            self.logger.error(f"Failed to stop daemon: {e}")
            sys.exit(1)

    def restart(self):
        """Restart the daemon"""
        self.stop()
        time.sleep(2)
        self.start()

    def status(self):
        """Check daemon status"""
        if not os.path.exists(self.pidfile):
            self.logger.info("Daemon is not running")
            return False

        with open(self.pidfile, 'r') as f:
            pid = int(f.read().strip())

        try:
            os.kill(pid, 0)
            self.logger.info(f"Daemon is running (PID: {pid})")
            return True
        except OSError:
            self.logger.info("Daemon is not running (stale pidfile)")
            os.remove(self.pidfile)
            return False

    def run(self):
        """Override this method to run your application"""
        raise NotImplementedError


class PODGatewayDaemon(Daemon):
    """POD Gateway specific daemon"""

    def run(self):
        """Run the Flask application"""
        self.logger.info("Starting Flask application...")

        # Setup signal handlers
        signal.signal(signal.SIGTERM, self.handle_signal)
        signal.signal(signal.SIGINT, self.handle_signal)

        # Import and run Flask app
        try:
            from app.main import app
            from app import config

            # Log startup
            self.logger.info(f"POD Gateway listening on {config.FLASK_HOST}:{config.FLASK_PORT}")

            # Run Flask
            app.run(
                host=config.FLASK_HOST,
                port=config.FLASK_PORT,
                debug=config.FLASK_DEBUG,
                use_reloader=False  # Important: disable reloader in daemon mode
            )
        except Exception as e:
            self.logger.error(f"Failed to start Flask application: {e}", exc_info=True)
            sys.exit(1)

    def handle_signal(self, signum, frame):
        """Handle shutdown signals"""
        self.logger.info(f"Received signal {signum}, shutting down...")
        self.delpid()
        sys.exit(0)


def main():
    """Main entry point"""
    daemon = PODGatewayDaemon(PIDFILE)

    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} {{start|stop|restart|status}}")
        sys.exit(1)

    command = sys.argv[1]

    if command == 'start':
        daemon.start()
    elif command == 'stop':
        daemon.stop()
    elif command == 'restart':
        daemon.restart()
    elif command == 'status':
        daemon.status()
    else:
        print(f"Unknown command: {command}")
        print(f"Usage: {sys.argv[0]} {{start|stop|restart|status}}")
        sys.exit(1)


if __name__ == '__main__':
    main()
