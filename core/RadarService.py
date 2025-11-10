import requests
from PyQt5.QtCore import QObject, QTimer, pyqtSignal, QDateTime
from PyQt5.QtGui import QPixmap  # We still need this for the error pixmap

class RadarService(QObject):
    """
    Handles fetching the NWS animated radar loop.
    
    Emits a signal with the raw GIF data (bytes) when successfully fetched.
    """
    
    # --- UPDATED: Signal now emits raw bytes ---
    radar_data_ready = pyqtSignal(bytes)
    
    # We'll send the error pixmap on the error channel
    radar_error = pyqtSignal(QPixmap) 

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.station = self.config['location']['radar_station']
        
        # Load the local error image as a fallback
        try:
            self.error_pixmap = QPixmap("error-image.png")
        except Exception as e:
            print(f"Warning: Could not load 'error-image.png'. {e}")
            self.error_pixmap = QPixmap(400, 300)
            # You might want to create a simple text-based error pixmap here

        self.radar_timer = QTimer(self)
        self.radar_timer.timeout.connect(self.update_radar)
        
        self.long_interval = 600000 # 10 minutes
        self.short_interval = 1000  # 1 second (for initial load)

    def start(self):
        print("RadarService started. Fetching initial image...")
        self.radar_timer.start(self.short_interval)

    def update_radar(self):
        try:
            station = self.config['location']['radar_station']
            current_time_epoch = int(QDateTime.currentSecsSinceEpoch())
            url = f"https://radar.weather.gov/ridge/standard/{station}_loop.gif?t={current_time_epoch}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # --- UPDATED: Emit the raw response.content ---
            self.radar_data_ready.emit(response.content) 

            if self.radar_timer.interval() != self.long_interval:
                print(f"Radar image loaded. Setting interval to {self.long_interval / 60000} minutes.")
                self.radar_timer.setInterval(self.long_interval)

        except requests.exceptions.RequestException as e:
            print(f"Error fetching NWS radar: {e}. Displaying local error-image.png")
            self.radar_error.emit(self.error_pixmap)
            self.radar_timer.setInterval(self.long_interval)
            
        except Exception as e:
            print(f"Error processing NWS radar: {e}. Displaying local error-image.png")
            self.radar_error.emit(self.error_pixmap)
            self.radar_timer.setInterval(self.long_interval)