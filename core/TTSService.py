import subprocess
from PyQt5.QtCore import QObject, pyqtSlot, QTimer, pyqtSignal

class TTSService(QObject):
    """
    Manages text-to-speech (TTS) synthesis using the 'espeak-ng' utility.
    Emits a signal when audio state changes (playing/stopped).
    """
    
    # --- NEW: Signal to notify the UI ---
    audio_state_changed = pyqtSignal(bool) # True = playing, False = stopped

    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.debug = self.config.get('debug', False)
        
        audio_config = self.config.get('audio', {})
        self.aplay_device = audio_config.get('aplay_device', 'default')
        volume_percent = audio_config.get('audio_volume_percent', 90)
        self.espeak_volume = str(int(volume_percent * 2)) 
        self.espeak_voice = audio_config.get('espeak_voice', 'en')
        
        self.tts_process = None
        
        # --- NEW: Timer to check if speech has finished ---
        self.poll_timer = QTimer(self)
        self.poll_timer.timeout.connect(self.check_process_status)
        
        print(f"TTSService: Initialized to use aplay device: '{self.aplay_device}'")
        print(f"TTSService: espeak volume set to: '{self.espeak_volume}'")
        print(f"TTSService: espeak voice set to: '{self.espeak_voice}'")

    @pyqtSlot()
    def check_process_status(self):
        """Called by the poll_timer to see if the audio process has finished."""
        if not self.tts_process:
            self.poll_timer.stop()
            return
            
        # .poll() returns None if running, or the exit code if finished
        if self.tts_process.poll() is not None:
            if self.debug:
                print("TTSService: Process finished naturally.")
            self.tts_process = None
            self.poll_timer.stop()
            self.audio_state_changed.emit(False) # Tell UI to turn off icon

    @pyqtSlot(str)
    def speak(self, text_to_speak):
        """
        Public slot to read the given text aloud using espeak-ng.
        - If not playing: starts the speech.
        - If already playing: stops the speech.
        """
        
        if self.tts_process:
            if self.debug:
                print("TTSService: Audio is already playing. Stopping.")
            try:
                self.tts_process.terminate()
                self.tts_process.wait(timeout=0.5)
            except Exception:
                pass 
            self.tts_process = None
            self.poll_timer.stop()
            self.audio_state_changed.emit(False) # Tell UI to turn off icon
            return 

        if "loading" in text_to_speak.lower():
            print("TTSService: Ignoring 'loading' message. Waiting for data.")
            return

        if self.debug:
            print(f"TTSService: Speaking text: '{text_to_speak}'")

        try:
            espeak_cmd = [
                "/usr/bin/espeak-ng",
                "-a", self.espeak_volume,
                "-s", "150",
                "-v", self.espeak_voice,
                text_to_speak,
                "--stdout"
            ]
            
            aplay_cmd = ["/usr/bin/aplay"]
            if self.aplay_device != "default":
                aplay_cmd.extend(["-D", self.aplay_device])

            espeak_process = subprocess.Popen(espeak_cmd, stdout=subprocess.PIPE)
            
            self.tts_process = subprocess.Popen(aplay_cmd, 
                                                stdin=espeak_process.stdout)
            
            espeak_process.stdout.close() 
            
            # --- NEW: Start polling and tell UI to turn on icon ---
            self.poll_timer.start(200) # Check 5 times/sec
            self.audio_state_changed.emit(True)
            
        except FileNotFoundError as e:
            print(f"TTSService: ERROR - Command not found. {e}")
            print("Please ensure 'espeak-ng' is at /usr/bin/")
        except Exception as e:
            print(f"TTSService: Error starting espeak-ng/aplay pipe: {e}")
            self.tts_process = None

    @pyqtSlot()
    def cleanup(self):
        """
        Ensures the espeak process is killed when the application quits.
        """
        self.poll_timer.stop()
        if self.tts_process:
            print("TTSService: Cleanup - Killing active process.")
            self.tts_process.kill()
            self.tts_process = None