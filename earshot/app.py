"""Earshot - Menu bar transcription app for macOS."""

import os
import threading
import time
from datetime import datetime
from pathlib import Path

# Hide Python from Dock (must be before rumps import)
try:
    from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
    NSApplication.sharedApplication().setActivationPolicy_(NSApplicationActivationPolicyAccessory)
except ImportError:
    pass

import rumps

from .audio_capture import AudioCapture
from .config import load_settings, save_settings, get_output_dir
from .diarization import diarize_transcript, is_ollama_available
from .file_processor import prepare_audio, get_output_base_name, is_supported_file
from .output_writer import write_all_formats
from .transcriber import Transcriber

# Audio level visualization characters
AUDIO_LEVELS = ["▁", "▂", "▃", "▄", "▅", "▆", "▇", "█"]


class EarshotApp(rumps.App):
    """Menu bar application for Earshot transcription."""
    
    def __init__(self):
        super().__init__("Earshot", icon=None, quit_button=None)
        
        self.settings = load_settings()
        self.transcriber = None
        self.audio_capture = None
        self.is_recording = False
        self.recording_start_time = None
        self.level_monitor_thread = None
        self.stop_monitor = False
        
        # Build menu
        self.menu = [
            rumps.MenuItem("Start Live Transcription", callback=self.toggle_recording),
            rumps.MenuItem("Transcribe File...", callback=self.transcribe_file),
            None,  # Separator
            rumps.MenuItem("Open Output Folder", callback=self.open_output_folder),
            self._build_settings_menu(),
            None,  # Separator
            rumps.MenuItem("Quit", callback=self.quit_app),
        ]
        
        # Set initial icon
        self._update_icon(recording=False)
    
    def _build_settings_menu(self) -> rumps.MenuItem:
        """Build the Settings submenu."""
        settings_menu = rumps.MenuItem("Settings")
        
        # Model size submenu
        model_menu = rumps.MenuItem("Model Size")
        for model in ["tiny", "base", "small", "medium", "large-v3"]:
            item = rumps.MenuItem(model, callback=self.set_model)
            if model == self.settings["model_size"]:
                item.state = 1
            model_menu.add(item)
        settings_menu.add(model_menu)
        
        # Audio device submenu (populated dynamically)
        device_menu = rumps.MenuItem("Audio Input")
        device_menu.add(rumps.MenuItem("Refresh Devices", callback=self.refresh_devices))
        device_menu.add(None)  # Separator
        self._populate_device_menu(device_menu)
        settings_menu.add(device_menu)
        
        return settings_menu
    
    def _populate_device_menu(self, device_menu: rumps.MenuItem) -> None:
        """Populate audio device menu with available devices."""
        try:
            capture = AudioCapture()
            devices = capture.list_devices()
            
            for device in devices:
                item = rumps.MenuItem(device["name"], callback=self.set_device)
                if device["name"] == self.settings["audio_device"]:
                    item.state = 1
                device_menu.add(item)
        except Exception:
            device_menu.add(rumps.MenuItem("(No devices found)"))
    
    def _update_icon(self, recording: bool, level: int = 0) -> None:
        """Update menu bar icon based on recording state and audio level."""
        if recording:
            # Show audio level visualization
            if level > 0 and level <= len(AUDIO_LEVELS):
                self.title = f"🔴 {AUDIO_LEVELS[level - 1]}"
            else:
                self.title = "🔴"
        else:
            self.title = "🎙️"
    
    def _start_level_monitor(self) -> None:
        """Start the audio level monitor thread."""
        self.stop_monitor = False
        self.level_monitor_thread = threading.Thread(target=self._level_monitor_loop)
        self.level_monitor_thread.daemon = True
        self.level_monitor_thread.start()
    
    def _stop_level_monitor(self) -> None:
        """Stop the audio level monitor thread."""
        self.stop_monitor = True
        if self.level_monitor_thread:
            self.level_monitor_thread.join(timeout=1.0)
            self.level_monitor_thread = None
    
    def _level_monitor_loop(self) -> None:
        """Monitor audio levels and update the menu bar icon."""
        while not self.stop_monitor and self.is_recording:
            if self.audio_capture:
                level = self.audio_capture.get_current_level()
                # Map 0-1 to 1-8 for visualization
                level_index = min(int(level * 8) + 1, 8) if level > 0.01 else 0
                self._update_icon(recording=True, level=level_index)
            time.sleep(0.15)  # Update ~7 times per second
    
    def _update_recording_menu(self) -> None:
        """Update menu item text based on recording state."""
        if self.is_recording:
            self.menu["Start Live Transcription"].title = "⏹ Stop Recording"
        else:
            self.menu["Start Live Transcription"].title = "Start Live Transcription"
    
    def _get_transcriber(self) -> Transcriber:
        """Get or create transcriber instance."""
        if self.transcriber is None or self.transcriber.model_size != self.settings["model_size"]:
            self.transcriber = Transcriber(model_size=self.settings["model_size"])
        return self.transcriber
    
    @rumps.clicked("Start Live Transcription")
    def toggle_recording(self, sender: rumps.MenuItem) -> None:
        """Toggle live recording on/off."""
        if self.is_recording:
            self._stop_recording()
        else:
            self._start_recording()
    
    def _start_recording(self) -> None:
        """Start live audio capture."""
        self.audio_capture = AudioCapture(
            device_name=self.settings["audio_device"],
            chunk_duration=self.settings["chunk_duration"],
            silence_timeout=self.settings["silence_timeout"],
            on_silence_timeout=self._on_silence_timeout,
        )
        
        if not self.audio_capture.start():
            rumps.notification(
                title="Earshot",
                subtitle="Recording Failed",
                message=f"Could not find audio device: {self.settings['audio_device']}",
            )
            return
        
        self.is_recording = True
        self.recording_start_time = datetime.now()
        self._update_icon(recording=True)
        self._update_recording_menu()
        self._start_level_monitor()
        
        rumps.notification(
            title="Earshot",
            subtitle="Recording Started",
            message="Capturing audio. Click menu to stop.",
        )
    
    def _stop_recording(self) -> None:
        """Stop recording and transcribe."""
        if not self.is_recording or not self.audio_capture:
            return
        
        self._stop_level_monitor()
        self.is_recording = False
        self._update_icon(recording=False)
        self._update_recording_menu()
        
        chunks = self.audio_capture.stop()
        
        if not chunks:
            rumps.notification(
                title="Earshot",
                subtitle="No Audio",
                message="No audio was captured.",
            )
            self.audio_capture.cleanup()
            return
        
        rumps.notification(
            title="Earshot",
            subtitle="Processing...",
            message=f"Transcribing {len(chunks)} audio segments.",
        )
        
        # Transcribe in background thread
        thread = threading.Thread(target=self._transcribe_recording, args=(chunks,))
        thread.daemon = True
        thread.start()
    
    def _transcribe_recording(self, chunks: list[Path]) -> None:
        """Transcribe recorded chunks (runs in background thread)."""
        try:
            transcriber = self._get_transcriber()
            
            if len(chunks) == 1:
                transcript = transcriber.transcribe(chunks[0])
            else:
                transcript = transcriber.transcribe_chunks(chunks)
            
            # Attempt speaker diarization with Ollama
            if is_ollama_available():
                rumps.notification(
                    title="Earshot",
                    subtitle="Identifying speakers...",
                    message="Using Ollama for speaker diarization",
                )
                transcript = diarize_transcript(transcript)
            
            # Generate output filename
            timestamp = self.recording_start_time.strftime("%Y-%m-%d_%H-%M-%S")
            base_name = f"meeting_{timestamp}"
            
            output_dir = get_output_dir()
            files = write_all_formats(
                transcript,
                output_dir,
                base_name,
                formats=self.settings["output_formats"],
            )
            
            rumps.notification(
                title="Earshot",
                subtitle="Transcription Complete",
                message=f"Saved to {output_dir}",
            )
        
        except Exception as e:
            rumps.notification(
                title="Earshot",
                subtitle="Transcription Failed",
                message=str(e)[:100],
            )
        
        finally:
            if self.audio_capture:
                self.audio_capture.cleanup()
    
    def _on_silence_timeout(self) -> None:
        """Called when silence timeout is reached."""
        rumps.notification(
            title="Earshot",
            subtitle="Auto-stopping",
            message="No audio detected for 60 seconds.",
        )
        # Schedule stop on main thread
        self._stop_recording()
    
    @rumps.clicked("Transcribe File...")
    def transcribe_file(self, sender: rumps.MenuItem) -> None:
        """Open file picker and transcribe selected file."""
        # Use osascript for native file picker
        script = '''
        tell application "System Events"
            activate
            set theFile to choose file with prompt "Select audio or video file" of type {"public.audio", "public.movie"}
            return POSIX path of theFile
        end tell
        '''
        
        try:
            import subprocess
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
            )
            
            if result.returncode != 0:
                return  # User cancelled
            
            file_path = Path(result.stdout.strip())
            
            if not file_path.exists():
                return
            
            rumps.notification(
                title="Earshot",
                subtitle="Processing...",
                message=f"Transcribing {file_path.name}",
            )
            
            # Transcribe in background
            thread = threading.Thread(target=self._transcribe_file, args=(file_path,))
            thread.daemon = True
            thread.start()
        
        except Exception as e:
            rumps.notification(
                title="Earshot",
                subtitle="Error",
                message=str(e)[:100],
            )
    
    def _transcribe_file(self, file_path: Path) -> None:
        """Transcribe a file (runs in background thread)."""
        temp_audio = None
        
        try:
            audio_path, is_temp = prepare_audio(file_path)
            if is_temp:
                temp_audio = audio_path
            
            transcriber = self._get_transcriber()
            transcript = transcriber.transcribe(audio_path)
            
            # Save to same directory as input file
            output_dir = file_path.parent
            base_name = get_output_base_name(file_path)
            
            files = write_all_formats(
                transcript,
                output_dir,
                base_name,
                formats=self.settings["output_formats"],
            )
            
            rumps.notification(
                title="Earshot",
                subtitle="Transcription Complete",
                message=f"Saved {len(files)} files to {output_dir}",
            )
        
        except Exception as e:
            rumps.notification(
                title="Earshot",
                subtitle="Transcription Failed",
                message=str(e)[:100],
            )
        
        finally:
            if temp_audio and temp_audio.exists():
                os.remove(temp_audio)
    
    @rumps.clicked("Open Output Folder")
    def open_output_folder(self, sender: rumps.MenuItem) -> None:
        """Open the output folder in Finder."""
        output_dir = get_output_dir()
        os.system(f'open "{output_dir}"')
    
    def set_model(self, sender: rumps.MenuItem) -> None:
        """Set the transcription model size."""
        # Update checkmarks
        for item in sender.parent.values():
            if isinstance(item, rumps.MenuItem):
                item.state = 0
        sender.state = 1
        
        self.settings["model_size"] = sender.title
        save_settings(self.settings)
        
        # Reset transcriber to load new model on next use
        self.transcriber = None
        
        rumps.notification(
            title="Earshot",
            subtitle="Model Changed",
            message=f"Will use {sender.title} model for next transcription.",
        )
    
    def set_device(self, sender: rumps.MenuItem) -> None:
        """Set the audio input device."""
        # Update checkmarks
        for item in sender.parent.values():
            if isinstance(item, rumps.MenuItem) and item.title != "Refresh Devices":
                item.state = 0
        sender.state = 1
        
        self.settings["audio_device"] = sender.title
        save_settings(self.settings)
    
    def refresh_devices(self, sender: rumps.MenuItem) -> None:
        """Refresh the list of audio devices."""
        device_menu = sender.parent
        
        # Remove existing device items (keep Refresh and separator)
        items_to_remove = []
        for key, item in device_menu.items():
            if isinstance(item, rumps.MenuItem) and key not in ["Refresh Devices", None]:
                items_to_remove.append(key)
        
        for key in items_to_remove:
            del device_menu[key]
        
        self._populate_device_menu(device_menu)
    
    def quit_app(self, sender: rumps.MenuItem) -> None:
        """Quit the application."""
        if self.is_recording:
            self._stop_recording()
        rumps.quit_application()


def main():
    """Run the Earshot app."""
    app = EarshotApp()
    app.run()


if __name__ == "__main__":
    main()
