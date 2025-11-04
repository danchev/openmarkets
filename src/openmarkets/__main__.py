# Application entry point (starts the server)

import logging
import sys

from openmarkets.core.server import main

logging.basicConfig(
    level=logging.INFO, stream=sys.stdout, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

if __name__ == "__main__":
    main()
