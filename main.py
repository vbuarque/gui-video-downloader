import customtkinter as ctk
from tkinter import filedialog
import threading
import queue
import sys
import os

# Importa a nossa classe de backend
from downloader import Downloader

def resource_path(relative_path):
    """ Obtém o caminho absoluto para o recurso, funciona para dev e para PyInstaller """
    try:
        # PyInstaller cria uma pasta temp e armazena o caminho em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Video Downloader")
        self.geometry("720x480")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # --- Widgets da UI ---
        self.url_frame = ctk.CTkFrame(self)
        self.url_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.url_frame.grid_columnconfigure(1, weight=1)
        self.url_label = ctk.CTkLabel(self.url_frame, text="Link do Vídeo:")
        self.url_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.url_entry = ctk.CTkEntry(self.url_frame, placeholder_text="Cole o URL do vídeo aqui")
        self.url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=1, column=0, padx=20, pady=10, sticky="ew")
        self.options_frame.grid_columnconfigure(1, weight=1)
        self.format_label = ctk.CTkLabel(self.options_frame, text="Formato:")
        self.format_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.format_menu = ctk.CTkOptionMenu(self.options_frame, values=["MP4 (Vídeo)", "MP3 (Áudio)"])
        self.format_menu.grid(row=0, column=1, padx=10, pady=10, sticky="w")
        self.path_label = ctk.CTkLabel(self.options_frame, text="Guardar em:")
        self.path_label.grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.path_display = ctk.CTkLabel(self.options_frame, text="Nenhuma pasta selecionada", anchor="w")
        self.path_display.grid(row=1, column=1, padx=10, pady=10, sticky="ew")
        self.browse_button = ctk.CTkButton(self.options_frame, text="Procurar...", command=self.select_download_path)
        self.browse_button.grid(row=1, column=2, padx=10, pady=10)

        self.download_button = ctk.CTkButton(self, text="Fazer download :D", command=self.start_download_thread)
        self.download_button.grid(row=2, column=0, padx=20, pady=10)

        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="nsew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        self.progress_bar = ctk.CTkProgressBar(self.status_frame)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.status_label = ctk.CTkLabel(self.status_frame, text="Aguardando você colocar o URL.", anchor="w")
        self.status_label.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

        # --- Lógica de Backend ---
        self.download_path = ""
        self.progress_queue = queue.Queue()
        self.downloader = Downloader(progress_hook=self.update_progress)
        self.check_progress_queue()

    def select_download_path(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.download_path = folder_path
            self.path_display.configure(text=self.download_path)

    def start_download_thread(self):
        url = self.url_entry.get()
        if not url:
            self.status_label.configure(text="Por favor, insira um URL.")
            return
        if not self.download_path:
            self.status_label.configure(text="Por favor, selecione uma pasta de destino.")
            return

        self.download_button.configure(state="disabled")
        self.status_label.configure(text="Jájá vai começar o download...")
        self.progress_bar.set(0)

        download_thread = threading.Thread(target=self.run_download, args=(url,), daemon=True)
        download_thread.start()

    def run_download(self, url):
        try:
            ffmpeg_path = resource_path("bin/ffmpeg.exe")
            options = {
                'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                'ffmpeg_location': ffmpeg_path,
            }
            if self.format_menu.get() == "MP3 (Áudio)":
                options['format'] = 'bestaudio/best'
                options['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            else:
                options['format'] = 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best'
                options['merge_output_format'] = 'mp4'

            self.downloader.download_video(url, options)
        except Exception as e:
            error_message = f"Erro: {str(e)[:100]}"
            self.progress_queue.put({'status': 'error', 'message': error_message})

    def update_progress(self, d):
        status = d.get('status')
        if status == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate')
            if total_bytes and d.get('downloaded_bytes') is not None:
                progress = d['downloaded_bytes'] / total_bytes
                self.progress_queue.put({'status': 'progress', 'value': progress})
        elif status == 'finished':
            self.progress_queue.put({'status': 'finished'})

    def check_progress_queue(self):
        try:
            message = self.progress_queue.get_nowait()
            if message['status'] == 'progress':
                self.progress_bar.set(message['value'])
                percent = int(message['value'] * 100)
                self.status_label.configure(text=f"CALMAAA TA BAIXANDO... {percent}%")
            elif message['status'] == 'finished':
                self.progress_bar.set(1)
                self.status_label.configure(text="Download concluído com sucesso!")
                self.download_button.configure(state="normal")
            elif message['status'] == 'error':
                self.status_label.configure(text=message['message'])
                self.progress_bar.set(0)
                self.download_button.configure(state="normal")
        except queue.Empty:
            pass
        self.after(100, self.check_progress_queue)

if __name__ == "__main__":
    app = App()
    app.mainloop()