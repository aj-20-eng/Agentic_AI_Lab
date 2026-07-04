import logging
import os

from config.settings import LOG_FOLDER

os.makedirs(LOG_FOLDER, exist_ok=True)

logging.basicConfig(
    filename=os.path.join(LOG_FOLDER, "guardian.log"),
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)

logger = logging.getLogger("SystemGuardian")