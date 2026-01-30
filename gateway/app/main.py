"""
POD Gateway - Entry Point

Human-in-the-loop approval system for POD designs.
Run with: python -m app.main
"""
import logging

from app import create_app

logger = logging.getLogger(__name__)


def main():
    """Run the POD Gateway application"""
    app = create_app()

    # Get config for startup info
    config = app.config
    generation_service = config.get("generation_service")
    publishing_service = config.get("publishing_service")

    # Print startup banner
    print("=" * 60)
    print("POD GATEWAY v2.0.0")
    print("=" * 60)
    print(f"Image Directory:  {config['IMAGE_DIR']}")
    print(f"State File:       {config['STATE_FILE']}")
    print(f"Generation:       {generation_service.backend_name if generation_service else 'disabled'}")
    print(f"Publishing:       {'Printify' if publishing_service and publishing_service.is_available else 'disabled'}")
    print(f"Server:           {config['HOST']}:{config['PORT']}")
    print("=" * 60)

    logger.info("Starting POD Gateway...")

    app.run(
        host=config["HOST"],
        port=config["PORT"],
        debug=config["DEBUG"]
    )


if __name__ == "__main__":
    main()
