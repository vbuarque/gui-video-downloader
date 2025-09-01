import customtkinter as ctk
from tkinter import filedialog
import threading
import queue
import sys
import os
from PIL import Image, ImageTk  # NOVO: Importações da biblioteca Pillow

# Importa a nossa classe de backend
from downloader import Downloader

def resource_path(relative_path):
    """ Obtém o caminho absoluto para o recurso, funciona para dev e para PyInstaller """
    try:
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

        # --- Lógica de Backend e Estado ---
        self.download_path = ""
        self.progress_queue = queue.Queue()
        self.downloader = Downloader(progress_hook=self.update_progress)
        
        # NOVO: Variáveis para a animação
        self.spinner_image = None
        self.spinner_label = None
        self.spinner_angle = 0
        self.animation_job = None

        # --- Construir a Interface ---
        self._create_widgets()
        self.check_progress_queue()

    def _create_widgets(self):
        """NOVO: Método para criar e organizar todos os widgets da UI."""
        # --- Frame de Entrada de URL ---
        self.url_frame = ctk.CTkFrame(self)
        self.url_frame.grid(row=0, column=0, padx=20, pady=(20, 10), sticky="ew")
        self.url_frame.grid_columnconfigure(1, weight=1)
        self.url_label = ctk.CTkLabel(self.url_frame, text="Link do Vídeo:")
        self.url_label.grid(row=0, column=0, padx=10, pady=10, sticky="w")
        self.url_entry = ctk.CTkEntry(self.url_frame, placeholder_text="Cole o URL do vídeo aqui")
        self.url_entry.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # --- Frame de Opções e Destino ---
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

        # --- Frame de Download (para o botão e o spinner) ---
        self.download_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.download_frame.grid(row=2, column=0, padx=20, pady=10)
        self.download_button = ctk.CTkButton(self.download_frame, text="Descarregar", command=self.start_download_thread)
        self.download_button.pack(side="left", padx=(0, 10))

        # NOVO: Label para o spinner (inicialmente vazio)
        self.spinner_label = ctk.CTkLabel(self.download_frame, text="")
        self.spinner_label.pack(side="left")

        # --- Barra de Progresso e Status ---
        self.status_frame = ctk.CTkFrame(self)
        self.status_frame.grid(row=3, column=0, padx=20, pady=(10, 20), sticky="nsew")
        self.status_frame.grid_columnconfigure(0, weight=1)
        self.progress_bar = ctk.CTkProgressBar(self.status_frame)
        self.progress_bar.set(0)
        self.progress_bar.grid(row=0, column=0, padx=10, pady=10, sticky="ew")
        self.status_label = ctk.CTkLabel(self.status_frame, text="Aguardando você colocar o URL.", anchor="w")
        self.status_label.grid(row=1, column=0, padx=10, pady=10, sticky="ew")

    # --- NOVO: Métodos para a Animação ---
    def _start_animation(self):
        """Inicia a animação do spinner."""
        try:
            # Carrega a imagem base uma única vez
            if self.spinner_image is None:
                self.spinner_image = Image.open(resource_path("spinner.png")).resize((24, 24), Image.Resampling.LANCZOS)

            # Gira a imagem
            self.spinner_angle = (self.spinner_angle - 15) % 360
            rotated_image = self.spinner_image.rotate(self.spinner_angle)
            self.spinner_photo = ImageTk.PhotoImage(rotated_image)
            self.spinner_label.configure(image=self.spinner_photo)

            # Agenda a próxima frame da animação
            self.animation_job = self.after(50, self._start_animation)
        except FileNotFoundError:
            # Se a imagem não for encontrada, apenas mostra um texto
            self.spinner_label.configure(text="...")
        except Exception as e:
            print(f"Erro na animação: {e}")
            self.spinner_label.configure(text="...")

    def _stop_animation(self):
        """Para a animação do spinner."""
        if self.animation_job:
            self.after_cancel(self.animation_job)
            self.animation_job = None
        self.spinner_label.configure(image=None, text="") # Limpa o spinner

    def _set_ui_state(self, state):
        """MODIFICADO: Ativa ou desativa os controlos da UI."""
        self.download_button.configure(state=state)
        self.url_entry.configure(state=state)
        self.format_menu.configure(state=state)
        self.browse_button.configure(state=state)

    def select_download_path(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.download_path = folder_path
            self.path_display.configure(text=self.download_path)

    def start_download_thread(self):
        url = self.url_entry.get()
        if not url:
            self.status_label.configure(text="Por favor, insira um URL.", text_color="#FF5555") # Vermelho
            return
        if not self.download_path:
            self.status_label.configure(text="Por favor, selecione uma pasta de destino.", text_color="#FF5555") # Vermelho
            return

        self._set_ui_state("disabled") # MODIFICADO: Desativa todos os controlos
        self.status_label.configure(text="Jájá vai começar o download...", text_color="white")
        self.progress_bar.set(0)
        self._start_animation() # NOVO: Inicia a animação

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
                options['postprocessors'] = [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192'}]
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
                self.status_label.configure(text=f"CALMAAA TA BAIXANDO... {percent}%", text_color="white")
            elif message['status'] == 'finished':
                self.progress_bar.set(1)
                self.status_label.configure(text="Download concluído com sucesso!", text_color="#32CD32") # Verde
                self._set_ui_state("normal") # MODIFICADO: Reativa todos os controlos
                self._stop_animation() # NOVO: Para a animação
            elif message['status'] == 'error':
                self.status_label.configure(text=message['message'], text_color="#FF5555") # Vermelho
                self.progress_bar.set(0)
                self._set_ui_state("normal") # MODIFICADO: Reativa todos os controlos
                self._stop_animation() # NOVO: Para a animação
        except queue.Empty:
            pass
        self.after(100, self.check_progress_queue)

if __name__ == "__main__":
    app = App()
    app.mainloop()