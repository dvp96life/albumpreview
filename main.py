import customtkinter as ctk
import tkinter as tk
import pygame
import sys
import os
from PIL import Image, ImageTk, ImageSequence

# Initialize Mixer
pygame.mixer.init()

class AlbumPreviewApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Album Preview")
        self.window_width = 800  # Increased width for horizontal layout
        self.window_height = 500 # Reduced height
        self.geometry(f"{self.window_width}x{self.window_height}")
        self.is_paused = False
        
        # --- BULLETPROOF EXIT ---
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.bg_x = 0
        self.bg_speed = 2
        self.is_running = True # Track if app is running

        # --- DYNAMIC PATH FINDER ---
        if getattr(sys, 'frozen', False):
            self.base_dir = sys._MEIPASS
        else:
            self.base_dir = os.path.dirname(os.path.abspath(__file__))

        # --- BACKGROUND ---
        try:
            bg_path = os.path.join(self.base_dir, "background.gif")
            if os.path.exists(bg_path):
                self.pil_image = Image.open(bg_path)
                self.frames = []
                for frame in ImageSequence.Iterator(self.pil_image):
                    resized_frame = frame.resize((self.window_width, self.window_height), Image.Resampling.LANCZOS)
                    # Convert to RGBA for transparency support
                    self.frames.append(ImageTk.PhotoImage(resized_frame.convert('RGBA')))
                
                self.frame_index = 0
                self.canvas = ctk.CTkCanvas(self, width=self.window_width, height=self.window_height, highlightthickness=0)
                self.canvas.pack(fill="both", expand=True)
                self.bg_image_id1 = self.canvas.create_image(0, 0, image=self.frames[0], anchor="nw")
                self.bg_image_id2 = self.canvas.create_image(self.window_width, 0, image=self.frames[0], anchor="nw")
                self.animate_bg()
        except Exception as e:
            print(f"BG Error: {e}")

        self.label = ctk.CTkLabel(self, text="Click to play", font=("Arial", 20, "bold"), text_color="white", fg_color="transparent")
        self.label.place(relx=0.5, y=30, anchor="center")

        # --- HORIZONTAL CONTAINER ---
        self.main_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        snippets_folder = os.path.join(self.base_dir, "snippets")
        self.snippets = sorted([f for f in os.listdir(snippets_folder) if f.endswith(".mp3")]) if os.path.exists(snippets_folder) else []
        self.current_song_index = -1

        # --- GRID LAYOUT FOR HORIZONTAL SNIPPETS ---
        for index, song in enumerate(self.snippets):
            btn_img_path = os.path.join(self.base_dir, "button.png")
            try:
                raw_btn = Image.open(btn_img_path)
                # Smaller size for horizontal layout
                song_img = ctk.CTkImage(light_image=raw_btn, dark_image=raw_btn, size=(100, 100))
                
                img_label = ctk.CTkLabel(self.main_frame, image=song_img, text=song, compound="top", text_color="white", font=("Arial", 12))
                # Grid positioning: Row 0, increasing Column
                img_label.grid(row=0, column=index, padx=10, pady=10)
                
                img_label.image = song_img
                img_label.bind("<Button-1>", lambda event, s=song: self.play_specific_song(s))
            except:
                pass

        # --- PLAY/PAUSE BUTTON ---
        self.setup_pause_button()
        self.check_music_end()

    def setup_pause_button(self):
        play_btn_path = os.path.join(self.base_dir, "play_pause_button.png")
        
        try:
            # Load image
            raw_image = Image.open(play_btn_path)
            self.custom_btn_img = ctk.CTkImage(light_image=raw_image, dark_image=raw_image, size=(80, 80))
            
            self.pause_btn = ctk.CTkButton(
                self, 
                text="", 
                image=self.custom_btn_img,
                command=self.toggle_pause,
                fg_color="#2B2B2B", 
                hover_color="#3B3B3B",
                width=80, 
                height=80,
                border_width=0
            )
        except Exception as e:
            print(f"DEBUG: Error: {e}")
            self.pause_btn = ctk.CTkButton(self, text="Pause", command=self.toggle_pause, fg_color="#FF69B4")
            
        self.pause_btn.place(relx=0.5, rely=0.85, anchor="center")

    def on_closing(self):
        """Forces the app to close entirely and stops loops"""
        self.is_running = False 
        pygame.mixer.music.stop()
        pygame.mixer.quit()
        sys.exit() 

    def animate_bg(self):
        if not self.is_running: return 
        self.bg_x -= self.bg_speed
        if self.bg_x <= -self.window_width: self.bg_x = 0
        try:
            self.canvas.coords(self.bg_image_id1, self.bg_x, 0)
            self.canvas.coords(self.bg_image_id2, self.bg_x + self.window_width, 0)
            self.frame_index = (self.frame_index + 1) % len(self.frames)
            self.canvas.itemconfig(self.bg_image_id1, image=self.frames[self.frame_index])
            self.canvas.itemconfig(self.bg_image_id2, image=self.frames[self.frame_index])
            self.after(33, self.animate_bg)
        except:
            pass

    def play_specific_song(self, song_name):
        self.current_song_index = self.snippets.index(song_name)
        self.is_paused = False
        self.play_song()

    def play_song(self):
        if 0 <= self.current_song_index < len(self.snippets):
            song_path = os.path.join(self.base_dir, "snippets", self.snippets[self.current_song_index])
            pygame.mixer.music.load(song_path)
            pygame.mixer.music.play()
            self.label.configure(text=f"Playing: {self.snippets[self.current_song_index]}")

    def toggle_pause(self):
        if pygame.mixer.music.get_busy():
            if not self.is_paused:
                pygame.mixer.music.pause()
                self.is_paused = True
            else:
                pygame.mixer.music.unpause()
                self.is_paused = False

    def check_music_end(self):
        if not self.is_running: return 
        if not pygame.mixer.music.get_busy() and self.current_song_index != -1 and not self.is_paused:
            self.current_song_index += 1
            if self.current_song_index < len(self.snippets): self.play_song()
        self.after(200, self.check_music_end)

if __name__ == "__main__":
    app = AlbumPreviewApp()
    app.mainloop()