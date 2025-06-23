from PyQt6.QtWidgets import QApplication
from widgets.application import ApplicationWindow
from env import MONGO_URI, MONGO_DB_NAME
from db.mongo_handler import MongoDBHandler
import sys

def main() -> None:
    app = QApplication(sys.argv)
    
    # Initialize MongoDB handler
    db_handler = MongoDBHandler(MONGO_URI, MONGO_DB_NAME)
    if not db_handler.connect():
        sys.exit("Failed to connect to the database.")
    
    # Create the main application window
    main_window = ApplicationWindow(db_handler)
    main_window.show()
    
    # Set up the application exit behavior
    app.aboutToQuit.connect(db_handler.close) # type: ignore
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()