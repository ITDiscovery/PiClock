import time
from PyQt5.QtCore import QObject, QTimer, pyqtSignal

# --- Hardware Library Imports ---
# We use try...except blocks so the app doesn't crash
# if we run it on a non-Raspberry Pi machine for testing.

HW_ENABLED = False
try:
    import RPi.GPIO as GPIO
    import smbus2
    import bme280
    HW_ENABLED = True
    print("HardwareService: RPi.GPIO, smbus2, and bme280 loaded successfully.")
except ImportError:
    print("HardwareService: WARNING - Hardware libraries not found.")
    print("HardwareService: Running in 'simulation' mode (no hardware I/O).")
except RuntimeError:
    print("HardwareService: ERROR - Failed to import RPi.GPIO.")
    print("HardwareService: This likely means the script isn't run as root")
    print("HardwareService: or is not on a Raspberry Pi. Disabling hardware.")


# --- BME280 WIRING DOCUMENTATION ---
#
# The BME280 sensor typically connects via I2C.
#
# Raspberry Pi Pin -> BME280 Pin
# -------------------------------
# Pin 1 (3.3V) ----> VIN (or VCC)
# Pin 3 (GPIO 2) --> SDA (Serial Data)
# Pin 5 (GPIO 3) --> SCL (Serial Clock)
# Pin 9 (GND) -----> GND
#
# (Using BCM numbering, SDA is GPIO 2 and SCL is GPIO 3)
# -------------------------------

class HardwareService(QObject):
    """
    Manages all hardware I/O: GPIO buttons and the BME280 sensor.
    """
    
    # --- Signals ---
    # Emits a dict with temp, humidity, and pressure
    bme_data_ready = pyqtSignal(dict) 
    
    # Emits the *action* (e.g., "next_frame") when a button is pressed
    button_pressed = pyqtSignal(str) 
    
    # Emits an error message
    hardware_error = pyqtSignal(str)

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config.get('hardware', {})
        self.hw_enabled = HW_ENABLED and self.config.get('enable', False)
        
        self.button_pins = {}
        self.last_press_time = 0
        self.debounce_time = 0.3 # 300ms debounce
        
        if self.hw_enabled:
            try:
                # --- 1. Setup BME280 ---
                self.i2c_address = int(self.config.get('bme280_i2c_address', '0x76'), 16)
                self.smbus = smbus2.SMBus(1) # Port 1
                self.calibration_params = bme280.load_calibration_params(
                    self.smbus, self.i2c_address
                )
                print(f"HardwareService: BME280 initialized at {hex(self.i2c_address)}")
                
                # --- 2. Setup GPIO Buttons ---
                
                # Use BCM numbering
                GPIO.setmode(GPIO.BCM) 
                
                self.button_pins = self.config.get('buttons', {})
                if not self.button_pins:
                    self.hardware_error.emit("No button pins defined in config.")
                
                for action, pin in self.button_pins.items():
                    print(f"HardwareService: Setting up button '{action}' on pin {pin}")
                    
                    # --- UPDATED: Re-enable internal pull-up resistor ---
                    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
                
            except Exception as e:
                print(f"HardwareService: ERROR during hardware setup: {e}")
                self.hardware_error.emit(f"Hardware Init Failed: {e}")
                self.hw_enabled = False

        # --- 3. Setup Poll Timer ---
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.poll_hardware)
        self.poll_interval = self.config.get('poll_interval_ms', 2000)

    def start(self):
        """Starts the hardware polling timer."""
        if self.hw_enabled:
            print(f"HardwareService started. Polling every {self.poll_interval}ms.")
            self.poll_hardware() # Poll immediately on start
            self.poll_timer.start(self.poll_interval)
        else:
            print("HardwareService is disabled (libraries not found or config 'enable' is false).")

    def poll_hardware(self):
        """
        Called by the QTimer to read sensor data and check for button presses.
        """
        if not self.hw_enabled:
            return

        # --- 1. Poll BME280 Sensor ---
        try:
            # read_compensated_data returns a BME280Data object
            data = bme280.sample(self.smbus, self.i2c_address, self.calibration_params)
            
            # Convert pressure from hPa (millibars) to inHg
            pressure_inhg = data.pressure * 0.02953
            
            bme_packet = {
                'temperature_c': data.temperature,
                'humidity': data.humidity,
                'pressure_hpa': data.pressure,
                'pressure_inhg': pressure_inhg
            }
            self.bme_data_ready.emit(bme_packet)
            
        except Exception as e:
            print(f"HardwareService: Error reading BME280: {e}")
            self.hardware_error.emit(f"BME280 Read Error: {e}")

        # --- 2. Check Buttons (with Debounce) ---
        current_time = time.time()
        if (current_time - self.last_press_time) < self.debounce_time:
            return # In debounce period, ignore all presses
            
        for action, pin in self.button_pins.items():
            # This logic is correct for an internal pull-up
            # Pin is HIGH (True) when idle, LOW (False) when pressed
            if GPIO.input(pin) == False:
                print(f"HardwareService: Button '{action}' (Pin {pin}) pressed.")
                self.last_press_time = current_time
                self.button_pressed.emit(action)
                
                # We only process one button press per poll cycle
                break 

    def cleanup(self):
        """Cleans up GPIO pins."""
        if self.hw_enabled:
            print("HardwareService: Cleaning up GPIO pins.")
            GPIO.cleanup()