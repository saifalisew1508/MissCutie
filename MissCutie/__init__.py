"""
MissCutie – Bot initialisation.
Builds the PTB Application and exposes it for modules to use.
"""

import logging

from telegram.ext import Application

from MissCutie import config
from MissCutie.database import init_db

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    level=logging.INFO,
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# ── Initialise database ───────────────────────────────────────────────────────
init_db()

# ── Build the PTB Application ─────────────────────────────────────────────────
application: Application = (
    Application.builder()
    .token(config.TOKEN)
    .concurrent_updates(True)
    .build()
)

bot = application.bot
dispatcher = application 
