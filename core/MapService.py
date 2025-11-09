import requests
from PyQt5.QtCore import QObject, QTimer, pyqtSignal, QDateTime
from PyQt5.QtGui import QPixmap

class MapService(QObject):
    """
    Fetches an animated map, saves it to a temp file,
    and emits the file path.
    """
    
    # --- UPDATED: New signal emits a string (file path) ---
    map_file_ready = pyqtSignal(str)
    map_error = pyqtSignal(QPixmap)

    def __init__(self, config, temp_file_name, parent=None):
        super().__init__(parent)
        self.config = config
        self.map_url = self.config.get('url', None)
        self.refresh_ms = self.config.get('refresh_ms', 900000)
        
        # --- NEW: Path to save the temp file ---
        self.temp_file = temp_file_name

        try:
            self.error_pixmap = QPixmap("error_image.png")
        except Exception as e:
            self.error_pixmap = QPixmap(400, 300)
            print(f"Warning: Could not load 'error_image.png'. {e}")

        self.map_timer = QTimer(self)
        self.map_timer.timeout.connect(self.update_map)

    def start(self):
        if not self.map_url:
            print(f"MapService: No 'url' in config. Service not started.")
            return
            
        print(f"MapService started for {self.map_url}. Refreshing every {self.refresh_ms / 60000} min.")
        self.update_map()
        self.map_timer.start(self.refresh_ms)

    def update_map(self):
        """
        Fetches the map image from the URL and saves it to a file.
        """
        try:
            current_time_epoch = int(QDateTime.currentSecsSinceEpoch())
            url = f"{self.map_url}?t={current_time_epoch}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status() 
            
            content_type = response.headers.get('Content-Type', '')
            if 'image/gif' not in content_type:
                raise Exception(f"Received non-GIF content-type: {content_type}")
            
            # --- NEW: Save the file ---
            with open(self.temp_file, 'wb') as f:
                f.write(response.content)
            
            # --- UPDATED: Emit the file path ---
            self.map_file_ready.emit(self.temp_file) 

        except Exception as e:
            print(f"Error fetching/processing map ({self.map_url}): {e}.")
            self.map_error.emit(self.error_pixmap)