# GUI Video Downloader
Uma aplicação de desktop simples para descarregar vídeos e áudio de várias plataformas online.

## Como Usar (Para Utilizadores do Windows)
- Vá para a secção de (https://github.com/vbuarque/gui-video-downloader/releases) no lado direito desta página.
- Faça o download da pasta .zip da versão mais recente (ex: VideoDownloader_v1.0_Windows.zip).
- Descompacte a pasta .zip numa pasta no seu computador.
- Dentro da pasta que foi criada, encontre e execute o ficheiro VideoDownloader.exe.

## Aviso sobre Antivírus (Falso Positivo)
Alguns programas antivírus podem detetar esta aplicação como uma ameaça. Isto é um "falso positivo". O código-fonte está totalmente disponível aqui para ser inspecionado. Se o seu antivírus bloquear o programa, você pode precisar de adicionar uma exceção de segurança para a pasta da aplicação.

## Aviso Legal
Esta ferramenta destina-se a ser utilizada para fins legítimos. O utilizador é o único responsável por garantir que não viola os Termos de Serviço de nenhuma plataforma nem as leis de direitos de autor. Utilize esta ferramenta de forma responsável.

## Para Programadores (Como Executar a partir do Código)
Se você quiser executar ou modificar o código-fonte, siga estes passos:

**Clone o Repositório:**
```
git clone https://github.com/SEU_NOME_DE_USUARIO/SEU_NOME_DE_REPOSITORIO.git
cd SEU_NOME_DE_REPOSITORIO
```

**Instale as Dependências Python:**
```
pip install customtkinter yt-dlp
```

**Descarregue o FFmpeg (Dependência Externa):**

Este projeto requer o FFmpeg para funcionar. Como ficheiros binários grandes não são guardados no repositório, você precisa de o descarregar manualmente.

- Vá para https://ffmpeg.org/download.html e baixe a versão para o seu sistema operativo.
- Crie uma pasta chamada bin na raiz do projeto.
- Extraia os ficheiros ffmpeg.exe e ffprobe.exe para dentro da pasta bin.

Execute a Aplicação:

```
python main.py
```

**Lembre-se de substituir `SEU_NOME_DE_USUARIO/SEU_NOME_DE_REPOSITORIO` nos links!**

**Agora o seu projeto está configurado da forma correta: o código-fonte está limpo no GitHub**
