# Usa imagem base Python
FROM python:3.10-slim

# Cria diretório de trabalho
WORKDIR /app

# Copia arquivos
COPY . .

# Instala dependências
RUN pip install --no-cache-dir -r requirements.txt

# Expõe a porta usada pelo Flask
EXPOSE 8080

# Comando para iniciar o app
CMD ["python", "video_info.py"]