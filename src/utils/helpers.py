"""
Helper utilities for the RCP Database Editor, including logging setup.
"""
import logging
import os
from typing import Any, Type, Dict

LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
LOG_FILE = os.path.join(LOG_DIR, 'rcp_db_editor.log')

os.makedirs(LOG_DIR, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

def get_logger(name: str) -> logging.Logger:
    """Get a configured logger by name."""
    return logging.getLogger(name)

# --- Utility Functions ---
def format_data(data: Any) -> str:
    """Format data as a stripped string."""
    return str(data).strip()

def validate_input(input_value: Any, expected_type: Type[Any]) -> None:
    """Validate that input_value is of expected_type, raise ValueError if not."""
    if not isinstance(input_value, expected_type):
        raise ValueError(f"Expected input of type {expected_type}, got {type(input_value)}")

def log_message(message: str) -> None:
    """Log a message to the console and log file."""
    logger = get_logger("RCP_DBEditor")
    logger.info(message)
    print(message)

def convert_to_dict(obj: Any) -> Dict[str, Any]:
    """Convert an object's __dict__ to a dictionary, excluding private attributes."""
    return {k: v for k, v in vars(obj).items() if not k.startswith('_')}

def refresh_app(main_window):
    """Centralized refresh for the main application window."""
    if hasattr(main_window, 'current_collection') and hasattr(main_window, 'on_collection_selected'):
        current = getattr(main_window, 'current_collection', None)
        if current:
            main_window.on_collection_selected(current)