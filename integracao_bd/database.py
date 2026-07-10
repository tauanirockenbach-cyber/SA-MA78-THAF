# Módulo de infraestrutura: Conexão com o Banco de Dados
# Instalar no terminal: pip install mysql-connector-python python-dotenv

import os
import mysql.connector
from dotenv import load_dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

def conectar():
    conexao = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        port=int(os.getenv("DB_PORT")),
        database=os.getenv("DB_NAME")
    )
    return conexao

# --- BLOCO DE TESTE ---
if __name__ == "__main__":
    try:
        print("Tentando conectar ao banco de dados...")
        conexao = conectar()
        
        if conexao.is_connected():
            print("Conexão realizada com sucesso!")
            conexao.close()  # Fecha a conexão após o teste
            print("Conexão fechada com segurança.")
            
    except Exception as erro:
        print(f"Erro ao conectar: {erro}")
