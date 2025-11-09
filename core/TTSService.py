import subprocess
from PyQt5.QtCore import QObject, pyqtSlot

class TTSService(QObject):
    """
    Manages text-to-speech (TTS) synthesis using the 'espeak' utility.
    
    This version pipes 'espeak' to 'aplay' and uses a configurable
    'espeak_voice' from the config file.
    """
    
    def __init__(self, config, parent=None):
        super().__init__(parent)
        self.config = config
        self.debug = self.config.get('debug', False)
        
        # --- Read audio settings from config ---
        audio_config = self.config.get('audio', {})
        self.aplay_device = audio_config.get('aplay_device', 'default')
        volume_percent = audio_config.get('audio_volume_percent', 90)
        self.espeak_volume = str(int(volume_percent * 2)) # Convert 90% -> 180
        
        # --- NEW: Read the voice name ---
        # Defaults to 'en' (standard English) if not specified
        self.espeak_voice = audio_config.get('espeak_voice', 'en')
        
        self.tts_process = None
        
        print(f"TTSService: Initialized to use aplay device: '{self.aplay_device}'")
        print(f"TTSService: espeak volume set to: '{self.espeak_volume}'")
        print(f"TTSService: espeak voice set to: '{self.espeak_voice}'") # New log

    @pyqtSlot(str)
    def speak(self, text_to_speak):
        """
        Public slot to read the given text aloud using espeak.
        It will stop any previously speaking process to prevent overlap.
        """
        
        if "loading" in text_to_speak.lower():
            print("TTSService: Ignoring 'loading' message. Waiting for data.")
            return

        if self.tts_process:
            try:
                self.tts_process.terminate()
                self.tts_process.wait(timeout=0.5)
            except Exception:
                pass 
            self.tts_process = None

        if self.debug:
            print(f"TTSService: Speaking text: '{text_to_speak}'")

        try:
            # --- UPDATED: Added the -v (voice) flag ---
            espeak_cmd = [
                "/usr/bin/espeak-ng",
                "-a", self.espeak_volume,
                "-s", "150",
                "-v", self.espeak_voice, # <-- The new flag
                text_to_speak,
                "--stdout"
            ]
            
            aplay_cmd = ["/usr/bin/aplay"]
            if self.aplay_device != "default":
                aplay_cmd.extend(["-D", self.aplay_device])

            # 3. Start the espeak process and pipe its stdout
            espeak_process = subprocess.Popen(espeak_cmd, stdout=subprocess.PIPE)
            
            # 4. Start aplay, using espeak's stdout as its stdin
            self.tts_process = subprocess.Popen(aplay_cmd, 
                                                stdin=espeak_process.stdout)
            
            espeak_process.stdout.close() 
            
        except FileNotFoundError as e:
            print(f"TTSService: ERROR - Command not found. {e}")
            print("Please ensure 'espeak' and 'aplay' are at /usr/bin/")
        except Exception as e:
            print(f"TTSService: Error starting espeak/aplay pipe: {e}")
            self.tts_process = None

    @pyqtSlot()
    def cleanup(self):
        """
        Ensures the espeak process is killed when the application quits.
        """
        if self.tts_process:
            print("TTSService: Cleanup - Killing active process.")
            self.tts_process.kill()
            self.tts_process = None