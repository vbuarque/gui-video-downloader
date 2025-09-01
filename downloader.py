import yt_dlp

class Downloader:
    """
    Classe que encapsula a lógica de download usando yt-dlp.
    """
    def __init__(self, progress_hook=None):
        """
        Inicializa o Downloader.
        :param progress_hook: Uma função de callback para receber atualizações de progresso.
        """
        self.progress_hook = progress_hook

    def download_video(self, url, options):
        """
        Descarrega um vídeo com as opções especificadas.
        :param url: O URL do vídeo.
        :param options: Um dicionário de opções para o yt-dlp.
        """
        if self.progress_hook:
            options['progress_hooks'] = [self.progress_hook]
        
        with yt_dlp.YoutubeDL(options) as ydl:
            ydl.download([url])