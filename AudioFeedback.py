import tkinter as tk
from tkinter import filedialog, messagebox
import numpy as np
import sounddevice as sd
import os
import threading
 
 
class AudioFeedbackApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Audio Feedback")
        self.root.geometry("500x400")
        self.root.configure(bg="#1e1e1e")
        self.is_playing = False
 
        self.label = tk.Label(root, text="Audio", font=("Courier", 20, "bold"), fg="#00ff00", bg="#1e1e1e")
        self.label.pack(pady=20)
 
        self.info_text = tk.Label(root, text="Select any file (EXE, DLL, JPG, etc.) to hear its data. may be shitty",
                                  fg="white", bg="#1e1e1e", font=("Arial", 10))
        self.info_text.pack(pady=5)
 
        self.file_size_var = tk.StringVar(value="")
        self.file_size_label = tk.Label(root, textvariable=self.file_size_var, fg="#888", bg="#1e1e1e", font=("Arial", 9))
        self.file_size_label.pack()
 
        rate_frame = tk.Frame(root, bg="#1e1e1e")
        rate_frame.pack(pady=10)
 
        tk.Label(rate_frame, text="Sample Rate:", fg="white", bg="#1e1e1e", font=("Arial", 10)).pack(side="left", padx=5)
 
        self.rate_var = tk.IntVar(value=44100)
        self.rate_slider = tk.Scale(rate_frame, from_=8000, to=96000, orient="horizontal",
                                    variable=self.rate_var, bg="#1e1e1e", fg="white",
                                    highlightbackground="#1e1e1e", troughcolor="#333",
                                    activebackground="#00ff00", length=220)
        self.rate_slider.pack(side="left")
 
        self.rate_display = tk.Label(rate_frame, textvariable=self.rate_var, fg="#00ff00", bg="#1e1e1e", font=("Courier", 10))
        self.rate_display.pack(side="left", padx=5)
 
        btn_frame = tk.Frame(root, bg="#1e1e1e")
        btn_frame.pack(pady=15)
 
        self.btn_browse = tk.Button(btn_frame, text="Files (:", command=self.browse_everything,
                                    bg="#333", fg="white", font=("Arial", 12, "bold"), width=15)
        self.btn_browse.pack(side="left", padx=10)
 
        self.btn_stop = tk.Button(btn_frame, text="Stop", command=self.stop_playback,
                                  bg="#550000", fg="white", font=("Arial", 12, "bold"), width=10,
                                  state="disabled")
        self.btn_stop.pack(side="left", padx=10)
 
        self.status_var = tk.StringVar(value="Status: Ready")
        self.status_label = tk.Label(root, textvariable=self.status_var, fg="#aaa", bg="#1e1e1e")
        self.status_label.pack(side="bottom", pady=10)
 
    def stop_playback(self):
        sd.stop()
        self.is_playing = False
        self.status_var.set("Stopped")
        self.btn_stop.config(state="disabled")
        self.btn_browse.config(state="normal")
 
    def play_data_as_audio(self, filepath):
        try:
            self.is_playing = True
            self.btn_stop.config(state="normal")
            self.btn_browse.config(state="disabled")
            self.status_var.set(f"Reading: {os.path.basename(filepath)}...")
 
            with open(filepath, 'rb') as f:
                raw_bytes = f.read()
 
            if not raw_bytes:
                self.status_var.set("File is empty ):")
                self.btn_stop.config(state="disabled")
                self.btn_browse.config(state="normal")
                return
 
            audio_array = np.frombuffer(raw_bytes, dtype=np.int8)
            audio_data = audio_array.astype(np.float32)
 
            max_val = np.max(np.abs(audio_data))
            if max_val > 0:
                audio_data = audio_data / max_val * 0.8
 
            self.status_var.set(f"Playing: {os.path.basename(filepath)}")
 
            sd.play(audio_data, samplerate=self.rate_var.get())
            sd.wait()
 
            if self.is_playing:
                self.status_var.set("Playback Finished")
 
        except Exception as e:
            messagebox.showerror("Error", f"Could not play file: {e}")
            self.status_var.set("Error |:")
        finally:
            self.is_playing = False
            self.btn_stop.config(state="disabled")
            self.btn_browse.config(state="normal")
 
    def browse_everything(self):
        file_path = filedialog.askopenfilename(
            initialdir="/",
            title="SELECT ANY FILE",
            filetypes=[("All Files", "*.*")]
        )
 
        if file_path:
            size_bytes = os.path.getsize(file_path)
            if size_bytes < 1024:
                size_str = f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                size_str = f"{size_bytes / 1024:.1f} KB"
            else:
                size_str = f"{size_bytes / (1024 * 1024):.2f} MB"
 
            self.file_size_var.set(f"File size: {size_str}")
            threading.Thread(target=self.play_data_as_audio, args=(file_path,), daemon=True).start()
 
 
if __name__ == "__main__":
    root = tk.Tk()
    app = AudioFeedbackApp(root)
    root.mainloop()