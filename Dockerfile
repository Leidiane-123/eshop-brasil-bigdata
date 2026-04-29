# 1. Define a imagem base com Python
FROM python:3.12-slim

# 2. Cria o diretório de trabalho dentro do contêiner
WORKDIR /app

# 3. Copia os ficheiros da sua pasta local para o contêiner
COPY . /app

# 4. Instala as dependências listadas no requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# 5. Expõe a porta 8501 (padrão do Streamlit)
EXPOSE 8501

# 6. Comando para iniciar a aplicação ao subir o contêiner
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]