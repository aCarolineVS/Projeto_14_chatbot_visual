import os

import streamlit as st
from dotenv import load_dotenv
from groq import Groq

# Carrega as variáveis do arquivo .env
load_dotenv()

# ---------------------------------------------------------------------------
# Configuração da página
# ---------------------------------------------------------------------------
st.set_page_config(page_title="Chatbot Groq", page_icon="💙", layout="centered")

MODELO_PADRAO = "openai/gpt-oss-120b"

SUGESTOES = [
    "👋 Olá! O que você sabe fazer?",
    "💡 Me dê ideias criativas para um projeto",
    "📚 Explique um assunto de forma simples",
    "✍️ Me ajude a escrever um texto",
]

# ---------------------------------------------------------------------------
# Estilo (tons de azul)
# ---------------------------------------------------------------------------
CSS = """
<style>
/* ---------- Paleta ----------
   Azul marinho  #0b2a5b   Azul royal   #0b4cb3   Azul vivo   #1e6fe0
   Azul céu      #3b8cf0   Azul claro   #9ec8ff   Azul gelo   #e8f3ff
------------------------------ */

/* Fundo geral */
.stApp {
    background: linear-gradient(180deg, #e8f3ff 0%, #cfe5ff 45%, #a9cffb 100%);
    background-attachment: fixed;
}
header[data-testid="stHeader"] { background: transparent; }
[data-testid="stBottom"] > div { background: transparent; }
.block-container { padding-top: 2rem; max-width: 820px; }

/* Cabeçalho */
.hero {
    background: linear-gradient(135deg, #0b2a5b 0%, #0b4cb3 55%, #3b8cf0 100%);
    border-radius: 24px;
    padding: 28px 30px;
    margin-bottom: 22px;
    box-shadow: 0 10px 30px rgba(11, 76, 179, 0.35);
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: "";
    position: absolute;
    right: -40px; top: -40px;
    width: 180px; height: 180px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(158,200,255,0.55), rgba(158,200,255,0));
}
.hero h1 {
    color: #ffffff !important;
    margin: 0;
    font-size: 2.1rem;
    font-weight: 800;
    letter-spacing: -0.5px;
    padding: 0;
}
.hero p {
    color: #cfe5ff !important;
    margin: 6px 0 0 0;
    font-size: 1.02rem;
}
.hero .status {
    display: inline-block;
    margin-top: 14px;
    padding: 4px 12px;
    border-radius: 999px;
    background: rgba(255,255,255,0.16);
    color: #e8f3ff;
    font-size: 0.8rem;
}
.hero .status::before {
    content: "●";
    color: #7dd3ff;
    margin-right: 6px;
}

/* Balões de mensagem */
[data-testid="stChatMessage"] {
    border-radius: 20px;
    padding: 14px 18px;
    margin-bottom: 12px;
    box-shadow: 0 4px 14px rgba(11, 42, 91, 0.12);
    border: 1px solid rgba(59, 140, 240, 0.25);
}

/* Mensagens da IA */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) {
    background: #ffffff;
    border-left: 6px solid #3b8cf0;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarAssistant"]) * {
    color: #0b2a5b;
}

/* Mensagens do usuário */
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) {
    background: linear-gradient(135deg, #1e6fe0 0%, #0b4cb3 100%);
    border-right: 6px solid #9ec8ff;
}
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) * {
    color: #ffffff;
}

/* Avatares */
[data-testid="stChatMessageAvatarAssistant"] {
    background: linear-gradient(135deg, #3b8cf0, #0b4cb3) !important;
}
[data-testid="stChatMessageAvatarUser"] {
    background: linear-gradient(135deg, #0b2a5b, #1e6fe0) !important;
}
[data-testid="stChatMessageAvatarAssistant"] *,
[data-testid="stChatMessageAvatarUser"] * { color: #ffffff !important; }

/* Campo de digitação */
[data-testid="stChatInput"] {
    border-radius: 26px;
    border: 2px solid #3b8cf0;
    background: #ffffff;
    box-shadow: 0 6px 20px rgba(30, 111, 224, 0.25);
}
[data-testid="stChatInput"],
[data-testid="stChatInput"] div,
[data-testid="stChatInput"] [data-baseweb],
[data-testid="stChatInput"] textarea {
    background: #ffffff !important;
    background-color: #ffffff !important;
    color: #0b2a5b !important;                       /* cor da letra que você digita */
    -webkit-text-fill-color: #0b2a5b !important;     /* garante a cor no Chrome/Edge */
    caret-color: #1e6fe0 !important;                 /* cor do cursor piscando */
}
[data-testid="stChatInput"] {
    border-color: #3b8cf0 !important;
}
[data-testid="stChatInput"] button,
[data-testid="stChatInput"] button div {
    background: linear-gradient(135deg, #1e6fe0, #0b4cb3) !important;
}
[data-testid="stChatInput"] textarea::placeholder {
    color: #5f86b8 !important;            /* cor do texto "Digite sua mensagem..." */
    opacity: 1 !important;
}
[data-testid="stChatInput"] button {
    background: linear-gradient(135deg, #1e6fe0, #0b4cb3) !important;
    border-radius: 50% !important;
}
[data-testid="stChatInput"] button svg { fill: #ffffff !important; color: #ffffff !important; }

/* Botões de sugestão e botões gerais */
.stButton > button {
    border-radius: 16px;
    border: 1.5px solid #3b8cf0;
    background: #ffffff;
    color: #0b4cb3;
    font-weight: 600;
    padding: 0.7rem 0.9rem;
    transition: all 0.18s ease;
}
.stButton > button:hover {
    background: linear-gradient(135deg, #1e6fe0, #0b4cb3);
    color: #ffffff;
    border-color: #0b4cb3;
    transform: translateY(-2px);
    box-shadow: 0 6px 16px rgba(11, 76, 179, 0.3);
}

/* Barra lateral */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0b2a5b 0%, #0b4cb3 100%);
}
[data-testid="stSidebar"] *,
[data-testid="stSidebar"] label p { color: #e8f3ff; }
[data-testid="stSidebar"] input {
    background: #e8f3ff !important;
    color: #0b2a5b !important;
    border-radius: 10px;
}
[data-testid="stSidebar"] hr { border-color: rgba(158, 200, 255, 0.35); }
[data-testid="stSidebar"] .stButton > button {
    background: rgba(255, 255, 255, 0.12);
    color: #ffffff;
    border: 1.5px solid #9ec8ff;
}
[data-testid="stSidebar"] .stButton > button:hover {
    background: #9ec8ff;
    color: #0b2a5b;
}

/* Mensagem de boas-vindas */
.boas-vindas {
    background: rgba(255, 255, 255, 0.75);
    border: 1px dashed #3b8cf0;
    border-radius: 18px;
    padding: 16px 20px;
    color: #0b2a5b;
    margin-bottom: 14px;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def obter_api_key() -> str | None:
    """Busca a chave em: .env / variável de ambiente > st.secrets."""
    chave = os.getenv("GROQ_API_KEY")
    if chave:
        return chave
    try:
        return st.secrets.get("GROQ_API_KEY")
    except Exception:
        return None


@st.cache_resource
def criar_client(api_key: str) -> Groq:
    return Groq(api_key=api_key)


def gerar_resposta(client: Groq, modelo: str, historico: list[dict], temperatura: float):
    """Gera a resposta em streaming, pedaço por pedaço."""
    stream = client.chat.completions.create(
        model=modelo,
        messages=historico,
        temperature=temperatura,
        stream=True,
    )
    for chunk in stream:
        if not chunk.choices:
            continue
        pedaco = chunk.choices[0].delta.content
        if pedaco:
            yield pedaco


# ---------------------------------------------------------------------------
# Estado da sessão
# ---------------------------------------------------------------------------
if "historico" not in st.session_state:
    st.session_state.historico = []
if "pendente" not in st.session_state:
    st.session_state.pendente = None


# ---------------------------------------------------------------------------
# Barra lateral
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("## 💙 Configurações")
    modelo = st.text_input("Modelo", value=MODELO_PADRAO)
    temperatura = st.slider("Criatividade", 0.0, 2.0, 1.0, 0.1)

    st.divider()
    if st.button("🗑️ Nova conversa", use_container_width=True):
        st.session_state.historico = []
        st.session_state.pendente = None
        st.rerun()

    st.caption(f"💬 Mensagens na conversa: {len(st.session_state.historico)}")


# ---------------------------------------------------------------------------
# Cabeçalho
# ---------------------------------------------------------------------------
st.markdown(
    """
    <div class="hero">
        <h1>💙 Chatbot Groq</h1>
        <p>Pergunte qualquer coisa. Estou aqui para ajudar!</p>
        <span class="status">Online e pronto para conversar</span>
    </div>
    """,
    unsafe_allow_html=True,
)

api_key = obter_api_key()
if not api_key:
    st.error(
        "Chave da API não encontrada. Crie um arquivo `.env` na mesma pasta do app "
        "com a linha `GROQ_API_KEY=sua_chave` e reinicie."
    )
    st.stop()

client = criar_client(api_key)

# ---------------------------------------------------------------------------
# Boas-vindas e sugestões (só quando a conversa está vazia)
# ---------------------------------------------------------------------------
if not st.session_state.historico:
    st.markdown(
        '<div class="boas-vindas">✨ <b>Bem-vindo!</b> Digite uma mensagem abaixo '
        "ou escolha uma das sugestões para começar.</div>",
        unsafe_allow_html=True,
    )
    colunas = st.columns(2)
    for i, sugestao in enumerate(SUGESTOES):
        if colunas[i % 2].button(sugestao, key=f"sug_{i}", use_container_width=True):
            st.session_state.pendente = sugestao
            st.rerun()

# ---------------------------------------------------------------------------
# Histórico
# ---------------------------------------------------------------------------
for msg in st.session_state.historico:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------------------------------------------------------------------
# Entrada do usuário
# ---------------------------------------------------------------------------
pergunta = st.chat_input("Digite sua mensagem...")
if st.session_state.pendente:
    pergunta = st.session_state.pendente
    st.session_state.pendente = None

if pergunta:
    st.session_state.historico.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        try:
            texto = st.write_stream(
                gerar_resposta(client, modelo, st.session_state.historico, temperatura)
            )
            st.session_state.historico.append({"role": "assistant", "content": texto})
        except Exception as e:
            # Remove a pergunta sem resposta para não quebrar o histórico
            st.session_state.historico.pop()
            st.error(f"Ocorreu um erro ao falar com a Groq: {e}")
