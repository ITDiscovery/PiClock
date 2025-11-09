import os
from PyQt5.QtWidgets import (QWidget, QLabel, QVBoxLayout, 
                             QHBoxLayout, QSizePolicy, QStackedWidget)
from PyQt5.QtCore import (Qt, QTimer, QDateTime, pyqtSlot, 
                          QByteArray, QBuffer, QIODevice)
from PyQt5.QtGui import QFont, QPixmap, QMovie

class WeatherWindow(QWidget):
    
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.debug = self.config.get("debug", False)
        
        # ... (Properties are unchanged) ...
        self.current_temp = 0.0
        self.current_desc = "Loading"
        self.current_spoken_forecast = "Weather data is loading."
        
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)
        
        self.screen_stack = QStackedWidget(self)
        self.main_layout.addWidget(self.screen_stack)
        
        # --- QMovie objects ---
        self.radar_movie = QMovie(self)
        self.map_movie = QMovie(self)
        
        # --- UPDATED: Connect frameChanged signals ---
        self.radar_movie.frameChanged.connect(self.on_radar_frame_changed)
        self.map_movie.frameChanged.connect(self.on_map_frame_changed)
        
        # We can remove the error slots, they aren't firing
        # self.radar_movie.error.connect(self.on_radar_movie_error)
        # self.map_movie.error.connect(self.on_map_movie_error)
        
        self.frame_1 = self.create_frame_1()
        self.frame_2 = self.create_frame_2() 
        
        self.screen_stack.addWidget(self.frame_1)
        self.screen_stack.addWidget(self.frame_2) 
        
        self.current_frame_index = 0
        
        self.init_base_ui()
        
        self.clock_timer = QTimer(self)
        self.clock_timer.timeout.connect(self.update_time)
        self.clock_timer.start(1000) 
        self.update_time() 
        
    def init_base_ui(self):
        # ... (This function is unchanged)
        screen_config = self.config['display'].get('screen', {})
        start_x = screen_config.get('start_x', 100)
        start_y = screen_config.get('start_y', 100)
        width = screen_config.get('width', 800)
        height = screen_config.get('height', 480)
        bg_color = self.config['display']['background_color']
        self.setGeometry(start_x, start_y, width, height)
        self.setStyleSheet(f"background-color: {bg_color};")
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.show()

    def create_frame_1(self):
        # ... (Layout setup is unchanged) ...
        frame = QWidget()
        main_layout = QVBoxLayout()
        main_layout.setSpacing(0); main_layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(main_layout)
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(0, 0, 0, 0); top_layout.setSpacing(0)
        left_column_layout = QVBoxLayout()
        left_column_layout.setContentsMargins(5, 5, 5, 5); left_column_layout.setSpacing(0)
        
        # ... (Left column labels are unchanged) ...
        self.temp_label = self.create_label("", 'Arial', 48, QFont.Bold)
        self.desc_label = self.create_label("Loading...", 'Arial', 20)
        self.time_label = self.create_label("", 'Arial', 72, QFont.Bold)
        self.date_label = self.create_label("", 'Arial', 24)
        self.local_temp_label = self.create_label("", 'Arial', 18)
        self.local_humidity_label = self.create_label("", 'Arial', 18)
        left_column_layout.addWidget(self.temp_label)
        left_column_layout.addWidget(self.desc_label)
        left_column_layout.addStretch(1)
        left_column_layout.addWidget(self.local_temp_label)
        left_column_layout.addWidget(self.local_humidity_label)
        left_column_layout.addStretch(1)
        left_column_layout.addWidget(self.time_label)
        left_column_layout.addWidget(self.date_label)

        # --- Radar Label ---
        self.radar_label = QLabel()
        self.radar_label.setAlignment(Qt.AlignCenter)
        # --- UPDATED: Removed setScaledContents ---
        # self.radar_label.setScaledContents(True) 
        self.radar_label.setMovie(self.radar_movie) 
        
        top_layout.addLayout(left_column_layout, 1) 
        top_layout.addWidget(self.radar_label, 2)    
        
        # ... (News label is unchanged) ...
        self.news_label = QLabel("Loading news...")
        self.news_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        self.news_label.setFont(QFont('Arial', 18))
        font_color = self.config['display']['font_color']
        self.news_label.setStyleSheet(f"color: {font_color}; padding-left: 10px;")
        self.news_label.setFixedHeight(40) 
        self.news_label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Fixed)
        main_layout.addLayout(top_layout, 1)
        main_layout.addWidget(self.news_label, 0)
        return frame
        
    def create_frame_2(self):
        frame = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(layout)
        
        self.map_label = QLabel("Loading National Map...")
        self.map_label.setAlignment(Qt.AlignCenter)
        # --- UPDATED: Removed setScaledContents ---
        # self.map_label.setScaledContents(True)
        self.map_label.setMovie(self.map_movie) 
        
        layout.addWidget(self.map_label)
        
        return frame

    def create_label(self, text, font_family, font_size, 
                     font_weight=QFont.Normal, alignment=Qt.AlignCenter):
        # ... (This function is unchanged)
        label = QLabel(text)
        label.setAlignment(alignment)
        label.setFont(QFont(font_family, font_size, font_weight))
        label.setStyleSheet(f"color: {self.config['display']['font_color']};")
        return label

    def update_time(self):
        # ... (This function is unchanged)
        current_time = QDateTime.currentDateTime()
        time_text = current_time.toString(" h:mm AP")
        date_text = current_time.toString("dddd, MMM d")
        self.time_label.setText(time_text)
        self.date_label.setText(date_text)

    # --- (All on_weather, on_news, on_bme slots are unchanged) ---
    @pyqtSlot(dict)
    def on_weather_ready(self, data):
        self.current_temp = data.get('temperature', 0)
        self.current_desc = data.get('description', 'Error')
        self.current_spoken_forecast = data.get('spoken_forecast', 'No forecast available.')
        self.temp_label.setText(f"{self.current_temp:.0f}°")
        self.desc_label.setText(self.current_desc)
    @pyqtSlot(str)
    def on_weather_error(self, error_msg):
        self.temp_label.setText("Err")
        self.desc_label.setText("API Error")
    @pyqtSlot(str)
    def on_news_updated(self, ticker_string):
        self.news_label.setText(ticker_string)
    @pyqtSlot(dict)
    def on_bme_data(self, data):
        units = self.config['display']['units']
        if units == 'imperial':
            temp_f = (data.get('temperature_c', 0) * 9/5) + 32
            self.local_temp_label.setText(f"Local: {temp_f:.1f}°F")
        else:
            self.local_temp_label.setText(f"Local: {data.get('temperature_c', 0):.1f}°C")
        self.local_humidity_label.setText(f"Humidity: {data.get('humidity', 0):.1f}%")

    # --- (on_radar_ready and on_map_ready are unchanged) ---
    @pyqtSlot(str)
    def on_radar_ready(self, file_path):
        """Slot for the local radar (Frame 1)"""
        print(f"on_radar_ready: Loading from file: {file_path}")
        self.radar_movie.stop()
        self.radar_movie.setFileName(file_path)
        self.radar_movie.start()
        self.radar_label.setPixmap(QPixmap()) 
    @pyqtSlot(str)
    def on_map_ready(self, file_path):
        """Slot for the national map (Frame 2)"""
        print(f"on_map_ready: Loading from file: {file_path}")
        self.map_movie.stop()
        self.map_movie.setFileName(file_path)
        self.map_movie.start()
        self.map_label.setPixmap(QPixmap()) 

    # --- (on_radar_error and on_map_error are unchanged) ---
    @pyqtSlot(QPixmap)
    def on_radar_error(self, error_pixmap):
        self.radar_movie.stop()
        self.radar_label.setMovie(None)
        scaled_pixmap = error_pixmap.scaled(self.radar_label.size(), 
                                            Qt.KeepAspectRatio, 
                                            Qt.SmoothTransformation)
        self.radar_label.setPixmap(scaled_pixmap)
    @pyqtSlot(QPixmap)
    def on_map_error(self, error_pixmap):
        self.map_movie.stop()
        self.map_label.setMovie(None)
        scaled_pixmap = error_pixmap.scaled(self.map_label.size(), 
                                            Qt.KeepAspectRatio, 
                                            Qt.SmoothTransformation)
        self.map_label.setPixmap(scaled_pixmap)

    # --- (on_button_pressed is unchanged) ---
    @pyqtSlot(str)
    def on_button_pressed(self, action):
        if action == "next_frame":
            self.current_frame_index += 1
            if self.current_frame_index >= self.screen_stack.count():
                self.current_frame_index = 0
            self.screen_stack.setCurrentIndex(self.current_frame_index)
            print(f"Switching to frame {self.current_frame_index}")
            
    # --- NEW: Slots to manually scale the movie frames ---
    @pyqtSlot()
    def on_radar_frame_changed(self):
        """Manually scale and set the current frame"""
        pixmap = self.radar_movie.currentPixmap()
        scaled_pixmap = pixmap.scaled(self.radar_label.size(), 
                                      Qt.KeepAspectRatio, 
                                      Qt.SmoothTransformation)
        self.radar_label.setPixmap(scaled_pixmap)

    @pyqtSlot()
    def on_map_frame_changed(self):
        """Manually scale and set the current frame"""
        pixmap = self.map_movie.currentPixmap()
        scaled_pixmap = pixmap.scaled(self.map_label.size(), 
                                      Qt.KeepAspectRatio, 
                                      Qt.SmoothTransformation)
        self.map_label.setPixmap(scaled_pixmap)