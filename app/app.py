import streamlit as st
import pandas as pd
# import database  # Descomente isso quando for integrar com seu arquivo database.py

# ==========================================
# 1. CONFIGURAÇÃO DA PÁGINA E CORES (AZUL)
# ==========================================
st.set_page_config(page_title="Sistema Industrial", page_icon="⚙️", layout="wide")

# CSS customizado para forçar os vários tons de azul
st.markdown("""
    <style>
    /* Fundo da tela - Azul bem claro (AliceBlue) */
    .stApp { background-color: #F0F8FF; }
    
    /* Textos e Títulos - Azul Marinho */
    h1, h2, h3, p, label { color: #003366 !important; }
    
    /* Botões - Azul Padrão */
    .stButton>button {
        background-color: #005A9C; 
        color: white; 
        border: none;
        border-radius: 8px;
        width: 100%;
    }
    /* Botões quando o mouse passa por cima - Azul Escuro */
    .stButton>button:hover { background-color: #003366; color: white; }
    
    /* Sidebar (Menu Lateral) - Azul Metálico */
    [data-testid="stSidebar"] { background-color: #B0C4DE; }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# 2. VARIÁVEIS DE SESSÃO (Para manter o Login)
# ==========================================
if 'logado' not in st.session_state:
    st.session_state['logado'] = False
if 'usuario' not in st.session_state:
    st.session_state['usuario'] = ""
if 'perfil' not in st.session_state:
    st.session_state['perfil'] = ""

# ==========================================
# 3. TELA DE LOGIN
# ==========================================
def tela_login():
    st.title("Acesso ao Sistema 🔒")
    
    # Criando colunas para centralizar o login
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.subheader("Faça seu login")
        user = st.text_input("Usuário:")
        senha = st.text_input("Senha:", type="password")
        
        if st.button("Entrar"):
            # Lógica simples de verificação (No mundo real, isso vem do Banco de Dados)
            if user == "admin" and senha == "123":
                st.session_state['logado'] = True
                st.session_state['usuario'] = user
                st.session_state['perfil'] = "Administrador"
                st.rerun() # Recarrega a página
                
            elif user == "operador" and senha == "123":
                st.session_state['logado'] = True
                st.session_state['usuario'] = user
                st.session_state['perfil'] = "Operador"
                st.rerun()
                
            else:
                st.error("Usuário ou senha incorretos! Tente novamente.")

# ==========================================
# 4. TELAS DE CADA PERFIL
# ==========================================
def tela_administrador():
    st.title("Painel de Administração 🛠️")
    st.write("Bem-vindo, Chefe! Aqui você tem acesso total para modificar o banco.")
    
    st.subheader("Cadastrar Nova Máquina")
    with st.form("form_nova_maquina"):
        tag = st.text_input("Tag da Máquina")
        modelo = st.selectbox("Selecione o Modelo", ["Torno", "Fresa", "Compressor"])
        serie = st.text_input("Número de Série")
        
        submit = st.form_submit_button("Salvar no Banco de Dados")
        if submit:
            # Aqui você chamaria a função do seu arquivo database.py:
            # database.inserir_maquina(tag, modelo, serie)
            st.success(f"Máquina {tag} inserida com sucesso no banco!")
            
    st.subheader("Visão Geral do Banco (Edição Habilitada)")
    # Simulando dados puxados do MySQL
    dados_mock = pd.DataFrame({
        "Tag": ["MAQ-01", "MAQ-02"],
        "Modelo": ["Torno", "Fresa"],
        "Status": ["Operando", "Parado"]
    })
    # O st.data_editor permite alterar o dado direto na tabela!
    dados_editados = st.data_editor(dados_mock, num_rows="dynamic")
    
    if st.button("Salvar Alterações da Tabela"):
        # Aqui você faria um loop no 'dados_editados' disparando os UPDATEs pro banco
        st.info("Alterações sincronizadas com o MySQL!")

def tela_operador():
    st.title("Painel de Operação 🏭")
    st.write("Bem-vindo, Operador! Seu acesso permite consultar os dados e reportar manutenções.")
    
    st.subheader("Máquinas na Fábrica")
    # Simulando dados puxados do MySQL (somente leitura)
    dados_mock = pd.DataFrame({
        "Tag": ["MAQ-01", "MAQ-02"],
        "Status": ["Operando", "Parado"],
        "Localização": ["Setor A", "Setor B"]
    })
    st.dataframe(dados_mock)

# ==========================================
# 5. GERENCIADOR DE ROTAS (Navegação)
# ==========================================
if not st.session_state['logado']:
    tela_login()
else:
    # Cria um menu lateral amigável para quem está logado
    with st.sidebar:
        st.header(f"Olá, {st.session_state['usuario'].capitalize()}!")
        st.write(f"**Perfil:** {st.session_state['perfil']}")
        st.divider()
        if st.button("Sair (Logout)"):
            st.session_state['logado'] = False
            st.session_state['usuario'] = ""
            st.session_state['perfil'] = ""
            st.rerun()

    # Redireciona para a tela certa com base no perfil
    if st.session_state['perfil'] == "Administrador":
        tela_administrador()
    elif st.session_state['perfil'] == "Operador":
        tela_operador()