"""
Graceful shutdown handling
"""
import signal
import sys
import logging
import atexit
from typing import List, Callable

logger = logging.getLogger(__name__)


class GracefulShutdown:
    """
    Handle graceful shutdown of the application.

    Features:
    - Register cleanup handlers
    - Handle SIGTERM and SIGINT signals
    - Ensure state is saved before exit
    """

    def __init__(self):
        self.shutdown_handlers: List[Callable] = []
        self.is_shutting_down = False

    def register_handler(self, handler: Callable):
        """
        Register a shutdown handler.

        Args:
            handler: Function to call on shutdown
        """
        self.shutdown_handlers.append(handler)
        logger.debug(f"Registered shutdown handler: {handler.__name__}")

    def shutdown(self, signum=None, frame=None):
        """Execute shutdown sequence"""
        if self.is_shutting_down:
            logger.warning("Shutdown already in progress")
            return

        self.is_shutting_down = True

        if signum:
            signal_name = signal.Signals(signum).name
            logger.info(f"Received signal {signal_name}, initiating graceful shutdown...")
        else:
            logger.info("Initiating graceful shutdown...")

        # Execute shutdown handlers in reverse order (LIFO)
        for handler in reversed(self.shutdown_handlers):
            try:
                logger.info(f"Executing shutdown handler: {handler.__name__}")
                handler()
            except Exception as e:
                logger.error(f"Error in shutdown handler {handler.__name__}: {e}", exc_info=True)

        logger.info("Graceful shutdown completed")

    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        # Handle SIGTERM (docker stop, kubernetes termination)
        signal.signal(signal.SIGTERM, self.shutdown)

        # Handle SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, self.shutdown)

        # Register with atexit as fallback
        atexit.register(lambda: self.shutdown() if not self.is_shutting_down else None)

        logger.info("Signal handlers registered for graceful shutdown")


# Global shutdown manager
shutdown_manager = GracefulShutdown()


# Convenience functions
def register_shutdown_handler(handler: Callable):
    """
    Register a function to be called on shutdown.

    Example:
        @register_shutdown_handler
        def cleanup():
            print("Cleaning up...")
    """
    shutdown_manager.register_handler(handler)
    return handler


def setup_graceful_shutdown(state_manager=None, printify_client=None):
    """
    Setup graceful shutdown handlers for POD Gateway.

    Args:
        state_manager: StateManager instance
        printify_client: PrintifyClient instance
    """
    # Save state on shutdown
    if state_manager:
        @register_shutdown_handler
        def save_state():
            logger.info("Saving state before shutdown...")
            try:
                state_manager.save()
                logger.info("State saved successfully")
            except Exception as e:
                logger.error(f"Failed to save state: {e}", exc_info=True)

    # Close any open connections
    if printify_client:
        @register_shutdown_handler
        def close_connections():
            logger.info("Closing external connections...")
            # Printify client uses requests, no explicit close needed
            # But we can log it
            logger.info("External connections closed")

    # Setup signal handlers
    shutdown_manager.setup_signal_handlers()

    logger.info("Graceful shutdown configured")
