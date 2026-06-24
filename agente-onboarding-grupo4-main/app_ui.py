import streamlit as st
import os
import json
import logging
import uuid
from datetime import datetime
from dotenv import load_dotenv
from src.core.agent import app
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

# Configurar variables de entorno y Logger
load_dotenv()
logging.basicConfig(level=logging.INFO)

# ──────────────────────────────────────────────
# CONFIGURACIÓN DE PÁGINA
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Onboarding AI · Grupo 4",
    page_icon="✦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ──────────────────────────────────────────────
# CSS PREMIUM – NIVEL COMERCIAL / SaaS
# ──────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ── Ocultar solo elementos innecesarios ── */
    #MainMenu {display:none !important;}
    footer {display:none !important;}
    .stDeployButton {display:none !important;}

    /* ── Avatares del chat ── */
    [data-testid="stChatMessage"] [data-testid*="chatAvatarIcon"] {
        display: none !important;
    }
    .chat-avatar {
        width: 32px; height: 32px;
        border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.75rem; font-weight: 700;
        flex-shrink: 0;
        letter-spacing: 0.02em;
    }
    .chat-avatar.user-av {
        background: linear-gradient(135deg, #6366f1, #8b5cf6);
        color: #fff;
    }
    .chat-avatar.bot-av {
        background: linear-gradient(135deg, #0ea5e9, #06b6d4);
        color: #fff;
    }

    /* ── Tipografía ── */
    html, body, [class*="css"], .stMarkdown, .stTextInput>div>div>input,
    .stSelectbox>div>div, p, li, td, th, label {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    /* Botones y spans: aplicar Inter solo donde NO sea un ícono Material */
    button:not([kind="icon"]), span:not([data-testid*="Icon"]):not(.material-symbols-rounded) {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    /* Preservar íconos Material de Streamlit */
    [data-testid="stSidebarCollapseButton"] span,
    [data-testid="baseButton-headerNoPadding"] span,
    .material-symbols-rounded {
        font-family: 'Material Symbols Rounded' !important;
    }

    /* ── Fondo principal ── */
    .stApp {
        background:
            radial-gradient(ellipse at 20% 50%, rgba(99,102,241,0.12) 0%, transparent 50%),
            radial-gradient(ellipse at 80% 20%, rgba(139,92,246,0.08) 0%, transparent 50%),
            radial-gradient(ellipse at 50% 80%, rgba(14,165,233,0.06) 0%, transparent 50%),
            #0a0e1a;
        color: #e2e8f0;
    }

    /* ── Scrollbar ── */
    ::-webkit-scrollbar {width:6px; height:6px;}
    ::-webkit-scrollbar-track {background:transparent;}
    ::-webkit-scrollbar-thumb {background:#334155; border-radius:3px;}
    ::-webkit-scrollbar-thumb:hover {background:#475569;}

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f1629 0%, #111827 100%) !important;
        border-right: 1px solid rgba(99,102,241,0.15) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown li,
    section[data-testid="stSidebar"] .stMarkdown span {color:#cbd5e1 !important;}

    /* ── Botones sidebar ── */
    section[data-testid="stSidebar"] .stButton > button {
        background: rgba(99,102,241,0.1) !important;
        color: #c7d2fe !important;
        border: 1px solid rgba(99,102,241,0.25) !important;
        border-radius: 10px !important;
        font-weight: 500 !important;
        font-size: 0.82rem !important;
        padding: 0.45rem 0.8rem !important;
        transition: all 0.25s ease !important;
    }
    section[data-testid="stSidebar"] .stButton > button:hover {
        background: rgba(99,102,241,0.25) !important;
        border-color: #818cf8 !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(99,102,241,0.2) !important;
    }

    /* ── Header hero ── */
    .hero-title {
        font-size: 2.6rem;
        font-weight: 900;
        letter-spacing: -0.04em;
        line-height: 1.1;
        background: linear-gradient(135deg, #818cf8 0%, #c084fc 40%, #f472b6 70%, #fb923c 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-size: 200% auto;
        animation: shimmer 6s ease infinite;
        margin-bottom: 4px;
    }
    @keyframes shimmer {
        0%   {background-position: 0% 50%;}
        50%  {background-position: 100% 50%;}
        100% {background-position: 0% 50%;}
    }
    .hero-sub {
        color: #64748b;
        font-size: 0.95rem;
        font-weight: 400;
        margin-bottom: 28px;
        letter-spacing: 0.01em;
    }

    /* ── Burbujas de chat ── */
    [data-testid="stChatMessage"] {
        background: rgba(15,23,42,0.4) !important;
        border-radius: 16px !important;
        padding: 1.2rem 1.4rem !important;
        margin-bottom: 0.75rem !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        animation: msgIn 0.35s cubic-bezier(0.16,1,0.3,1) forwards;
        opacity: 0;
    }
    @keyframes msgIn {
        from {opacity:0; transform:translateY(12px) scale(0.98);}
        to   {opacity:1; transform:translateY(0) scale(1);}
    }

    /* ── Input del chat ── */
    [data-testid="stChatInput"] {
        background: rgba(15,23,42,0.6) !important;
        border: 1px solid rgba(99,102,241,0.2) !important;
        border-radius: 16px !important;
        padding: 4px !important;
        transition: all 0.3s ease !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #818cf8 !important;
        box-shadow: 0 0 0 3px rgba(129,140,248,0.15), 0 8px 25px rgba(0,0,0,0.4) !important;
    }
    [data-testid="stChatInput"] textarea {
        color: #e2e8f0 !important;
        caret-color: #818cf8 !important;
    }

    /* ── Badges de fase ── */
    .phase-pill {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 6px 14px;
        border-radius: 100px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
    }
    .phase-1 {
        background: rgba(251,191,36,0.12);
        color: #fde68a;
        border: 1px solid rgba(251,191,36,0.3);
    }
    .phase-2 {
        background: rgba(52,211,153,0.12);
        color: #6ee7b7;
        border: 1px solid rgba(52,211,153,0.3);
    }

    /* ── Tarjetas de perfil ── */
    .profile-card {
        background: linear-gradient(135deg, rgba(30,41,59,0.6), rgba(15,23,42,0.4));
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 18px;
        margin-top: 8px;
    }
    .profile-card .field-label {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #64748b;
        font-weight: 600;
        margin-bottom: 2px;
    }
    .profile-card .field-value {
        font-size: 0.88rem;
        color: #e2e8f0;
        margin-bottom: 12px;
        font-weight: 500;
    }

    /* ── Trazas / Logs ── */
    .trace-item {
        background: rgba(15,23,42,0.5);
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 8px;
        border-left: 3px solid #818cf8;
        font-size: 0.8rem;
        transition: transform 0.2s ease, background 0.2s ease;
    }
    .trace-item:hover {
        transform: translateX(3px);
        background: rgba(30,41,59,0.5);
    }
    .trace-item.tool-call  {border-left-color: #fbbf24;}
    .trace-item.tool-resp  {border-left-color: #34d399;}
    .trace-item .trace-title {
        font-weight: 600;
        color: #f1f5f9;
        font-size: 0.82rem;
    }
    .trace-item .trace-body {
        color: #94a3b8;
        font-size: 0.78rem;
        margin-top: 4px;
        word-break: break-word;
    }

    /* ── Separadores sutiles ── */
    hr {border-color: rgba(255,255,255,0.06) !important;}

    /* ── Chat session items ── */
    .chat-session-item {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 10px 12px;
        border-radius: 10px;
        cursor: pointer;
        transition: all 0.2s ease;
        margin-bottom: 4px;
        border: 1px solid transparent;
    }
    .chat-session-item:hover {
        background: rgba(99,102,241,0.08);
        border-color: rgba(99,102,241,0.15);
    }
    .chat-session-item.active {
        background: rgba(99,102,241,0.15);
        border-color: rgba(99,102,241,0.3);
    }
    .chat-session-item .session-icon {
        width: 32px; height: 32px;
        border-radius: 8px;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.85rem;
        background: rgba(99,102,241,0.15);
        flex-shrink: 0;
    }
    .chat-session-item .session-info {
        overflow: hidden;
    }
    .chat-session-item .session-name {
        font-size: 0.82rem;
        font-weight: 600;
        color: #e2e8f0;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .chat-session-item .session-date {
        font-size: 0.68rem;
        color: #64748b;
    }

    /* ── Sección sidebar títulos ── */
    .sidebar-section-title {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #475569;
        font-weight: 700;
        padding: 16px 0 8px 0;
        border-top: 1px solid rgba(255,255,255,0.05);
        margin-top: 8px;
    }

    /* ── Empty state ── */
    .empty-state {
        text-align: center;
        padding: 80px 20px;
    }
    .empty-state .empty-icon {
        font-size: 4rem;
        margin-bottom: 16px;
        opacity: 0.6;
    }
    .empty-state .empty-title {
        font-size: 1.4rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 8px;
    }
    .empty-state .empty-desc {
        font-size: 0.9rem;
        color: #64748b;
        max-width: 400px;
        margin: 0 auto;
        line-height: 1.5;
    }

    /* ── Expander styling ── */
    .streamlit-expanderHeader {
        background: transparent !important;
        color: #cbd5e1 !important;
        font-weight: 600 !important;
        font-size: 0.85rem !important;
    }
</style>
""", unsafe_allow_html=True)


# ──────────────────────────────────────────────
# GESTIÓN DE SESIONES DE CHAT (MULTI-CHAT)
# ──────────────────────────────────────────────
SESSIONS_DIR = "data/sessions"
os.makedirs(SESSIONS_DIR, exist_ok=True)

def _session_path(session_id: str) -> str:
    return os.path.join(SESSIONS_DIR, f"{session_id}.json")

def load_sessions_index() -> list[dict]:
    """Carga la lista de sesiones guardadas, ordenadas por última actividad."""
    sessions = []
    if os.path.isdir(SESSIONS_DIR):
        for fname in os.listdir(SESSIONS_DIR):
            if fname.endswith(".json"):
                fpath = os.path.join(SESSIONS_DIR, fname)
                try:
                    with open(fpath, "r", encoding="utf-8") as f:
                        meta = json.load(f)
                    sessions.append(meta)
                except Exception:
                    pass
    sessions.sort(key=lambda s: s.get("updated_at", ""), reverse=True)
    return sessions

def save_session(session_id: str, name: str, chat_history_serialized: list, log_history: list, profile: dict | None):
    """Persiste la sesión actual a disco."""
    data = {
        "id": session_id,
        "name": name,
        "created_at": st.session_state.get("session_created_at", datetime.now().isoformat()),
        "updated_at": datetime.now().isoformat(),
        "chat_history": chat_history_serialized,
        "log_history": log_history,
        "profile": profile,
    }
    with open(_session_path(session_id), "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def delete_session(session_id: str):
    path = _session_path(session_id)
    if os.path.exists(path):
        os.remove(path)

def serialize_messages(messages: list) -> list:
    """Convierte los objetos de LangChain a dicts serializables."""
    out = []
    for m in messages:
        if isinstance(m, HumanMessage):
            out.append({"type": "human", "content": m.content})
        elif isinstance(m, AIMessage):
            tc = []
            if m.tool_calls:
                for t in m.tool_calls:
                    tc.append({"name": t["name"], "args": t["args"], "id": t.get("id", "")})
            out.append({"type": "ai", "content": m.content, "tool_calls": tc})
        elif isinstance(m, ToolMessage):
            out.append({"type": "tool", "content": m.content, "name": getattr(m, "name", ""), "tool_call_id": getattr(m, "tool_call_id", "")})
    return out

def deserialize_messages(data: list) -> list:
    """Reconstruye objetos LangChain desde dicts."""
    out = []
    for d in data:
        if d["type"] == "human":
            out.append(HumanMessage(content=d["content"]))
        elif d["type"] == "ai":
            msg = AIMessage(content=d["content"])
            if d.get("tool_calls"):
                msg.tool_calls = d["tool_calls"]
            out.append(msg)
        elif d["type"] == "tool":
            out.append(ToolMessage(content=d["content"], name=d.get("name", ""), tool_call_id=d.get("tool_call_id", "")))
    return out


# ──────────────────────────────────────────────
# INICIALIZACIÓN DEL SESSION STATE
# ──────────────────────────────────────────────
if "current_session_id" not in st.session_state:
    st.session_state.current_session_id = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "log_history" not in st.session_state:
    st.session_state.log_history = []
if "session_name" not in st.session_state:
    st.session_state.session_name = ""
if "session_created_at" not in st.session_state:
    st.session_state.session_created_at = datetime.now().isoformat()


def start_new_session():
    sid = uuid.uuid4().hex[:10]
    st.session_state.current_session_id = sid
    st.session_state.chat_history = []
    st.session_state.log_history = []
    st.session_state.session_name = f"Chat {datetime.now().strftime('%d/%m %H:%M')}"
    st.session_state.session_created_at = datetime.now().isoformat()
    # Reset the LangGraph thread so the agent starts fresh
    st.session_state.thread_id = sid


def _on_new_chat_click():
    """Callback for the 'Nuevo Chat' button — saves current session, then starts fresh."""
    # Save current session if it has messages
    if st.session_state.get("current_session_id") and st.session_state.get("chat_history"):
        save_session(
            st.session_state.current_session_id,
            st.session_state.session_name,
            serialize_messages(st.session_state.chat_history),
            st.session_state.log_history,
            get_user_profile()
        )
    start_new_session()
    # Flag to show toast after rerun
    st.session_state._show_new_chat_toast = True

def switch_session(session_data: dict):
    st.session_state.current_session_id = session_data["id"]
    st.session_state.chat_history = deserialize_messages(session_data.get("chat_history", []))
    st.session_state.log_history = session_data.get("log_history", [])
    st.session_state.session_name = session_data.get("name", "Sin nombre")
    st.session_state.session_created_at = session_data.get("created_at", datetime.now().isoformat())
    # Restaurar perfil si la sesión lo tenía
    profile = session_data.get("profile")
    if profile:
        os.makedirs("data", exist_ok=True)
        with open("data/user_profile.json", "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)


# Función auxiliar para comprobar perfil
def get_user_profile():
    file_path = "data/user_profile.json"
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


# ──────────────────────────────────────────────
# SIDEBAR
# ──────────────────────────────────────────────
with st.sidebar:
    # Logo / Branding
    st.markdown("""
    <div style="display:flex; align-items:center; gap:10px; padding:4px 0 20px 0;">
        <div style="width:36px;height:36px;border-radius:10px;
            background:linear-gradient(135deg,#818cf8,#c084fc);
            display:flex;align-items:center;justify-content:center;font-size:1.1rem;font-weight:800;color:#fff;">✦</div>
        <div>
            <div style="font-size:1rem;font-weight:800;color:#f1f5f9;letter-spacing:-0.02em;">Onboarding AI</div>
            <div style="font-size:0.65rem;color:#64748b;font-weight:500;">Grupo 4 · UTN Santa Fe</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Botón Nuevo Chat (usa callback para rerun confiable)
    st.button("＋  Nuevo Chat", use_container_width=True, key="btn_new_chat", on_click=_on_new_chat_click)

    # Toast de confirmación al crear nuevo chat
    if st.session_state.pop("_show_new_chat_toast", False):
        st.toast("Nuevo chat creado", icon="✨")

    # Lista de sesiones
    sessions = load_sessions_index()
    if sessions:
        st.markdown('<div class="sidebar-section-title">Conversaciones</div>', unsafe_allow_html=True)

        def _on_switch_session(sess_data):
            """Callback to switch to a different session."""
            if st.session_state.get("current_session_id") and st.session_state.get("chat_history"):
                save_session(
                    st.session_state.current_session_id,
                    st.session_state.session_name,
                    serialize_messages(st.session_state.chat_history),
                    st.session_state.log_history,
                    get_user_profile()
                )
            switch_session(sess_data)

        def _on_delete_session(sess_id):
            """Callback to delete a session."""
            delete_session(sess_id)
            if sess_id == st.session_state.current_session_id:
                start_new_session()

        for sess in sessions:
            is_active = (sess["id"] == st.session_state.current_session_id)
            label = f"{'● ' if is_active else ''}{sess['name']}"
            col_a, col_b = st.columns([5, 1])
            with col_a:
                st.button(label, key=f"sess_{sess['id']}", use_container_width=True,
                          on_click=_on_switch_session, args=(sess,))
            with col_b:
                st.button("✕", key=f"del_{sess['id']}",
                          on_click=_on_delete_session, args=(sess["id"],))

    # ── Separador y Fase ──
    st.markdown('<div class="sidebar-section-title">Estado del Agente</div>', unsafe_allow_html=True)

    profile = get_user_profile()
    profile_exists = profile is not None

    if not profile_exists:
        st.markdown('<span class="phase-pill phase-1"><span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:#fbbf24;margin-right:4px;"></span> Fase 1 · Perfilado</span>', unsafe_allow_html=True)
        st.caption("El agente está recopilando información del nuevo empleado.")
    else:
        st.markdown('<span class="phase-pill phase-2"><span style="display:inline-block;width:7px;height:7px;border-radius:50%;background:#34d399;margin-right:4px;"></span> Fase 2 · Operativo</span>', unsafe_allow_html=True)
        st.caption("Perfil completo. RAG y Google Calendar habilitados.")

    # Perfil del empleado
    if profile_exists:
        st.markdown('<div class="sidebar-section-title">Perfil del Empleado</div>', unsafe_allow_html=True)
        fields = [
            ("Nombre", profile.get("nombre", "—")),
            ("Rol", profile.get("rol", "—")),
            ("Seniority", profile.get("seniority", "—")),
            ("Horario", profile.get("horario_laboral", "—")),
            ("Preferencias", profile.get("preferencias", "—")),
        ]
        card_html = '<div class="profile-card">'
        for label, value in fields:
            card_html += f'<div class="field-label">{label}</div><div class="field-value">{value}</div>'
        card_html += '</div>'
        st.markdown(card_html, unsafe_allow_html=True)

    # Trazas de observabilidad
    st.markdown('<div class="sidebar-section-title">Trazas ReAct</div>', unsafe_allow_html=True)
    if not st.session_state.log_history:
        st.caption("Sin actividad aún en este turno.")
    else:
        for log in st.session_state.log_history:
            if log["type"] == "thought":
                icon, css_class = "▸", ""
            elif log["type"] == "tool_call":
                icon, css_class = "⚡", "tool-call"
            else:
                icon, css_class = "↩", "tool-resp"
            st.markdown(f"""
            <div class="trace-item {css_class}">
                <div class="trace-title">{icon} {log['title']}</div>
                <div class="trace-body">{log['content']}</div>
            </div>
            """, unsafe_allow_html=True)

    # ── Estadísticas de la sesión ──
    st.markdown('<div class="sidebar-section-title">Estadísticas</div>', unsafe_allow_html=True)
    human_msgs = [m for m in st.session_state.chat_history if isinstance(m, HumanMessage)]
    tools_used = [log["title"].replace("Acción: ", "") for log in st.session_state.log_history if log["type"] == "tool_call"]
    tools_unique = list(dict.fromkeys(tools_used))  # unique preservando orden
    session_start = st.session_state.get("session_created_at", datetime.now().isoformat())
    try:
        delta = datetime.now() - datetime.fromisoformat(session_start)
        mins = int(delta.total_seconds() // 60)
        duration_str = f"{mins} min" if mins > 0 else "<1 min"
    except Exception:
        duration_str = "—"

    stats_html = f"""
    <div class="profile-card" style="margin-top:4px;">
        <div class="field-label">Mensajes enviados</div>
        <div class="field-value">{len(human_msgs)}</div>
        <div class="field-label">Herramientas usadas</div>
        <div class="field-value">{', '.join(tools_unique) if tools_unique else '—'}</div>
        <div class="field-label">Duración sesión</div>
        <div class="field-value">{duration_str}</div>
    </div>
    """
    st.markdown(stats_html, unsafe_allow_html=True)

    # Acciones de sesión
    st.markdown('<div class="sidebar-section-title">Acciones</div>', unsafe_allow_html=True)

    def _on_clear_chat():
        st.session_state.chat_history = []
        st.session_state.log_history = []

    def _on_reset_profile():
        if os.path.exists("data/user_profile.json"):
            os.remove("data/user_profile.json")
        st.session_state.chat_history = []
        st.session_state.log_history = []

    col1, col2 = st.columns(2)
    with col1:
        st.button("Limpiar Chat", use_container_width=True, key="btn_clear", on_click=_on_clear_chat)
    with col2:
        st.button("Reiniciar Perfil", use_container_width=True, key="btn_reset", on_click=_on_reset_profile)


# ──────────────────────────────────────────────
# PANEL PRINCIPAL – CHAT
# ──────────────────────────────────────────────

# Si no hay sesión activa, crear una
if st.session_state.current_session_id is None:
    start_new_session()

# Header
st.markdown('<div class="hero-title">Mentor de Onboarding</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Asistente autónomo con razonamiento multi-paso · LangGraph · RAG · Google Calendar</div>', unsafe_allow_html=True)

# Renderizar historial de chat
chat_container = st.container()
with chat_container:
    has_messages = False
    for msg in st.session_state.chat_history:
        if isinstance(msg, HumanMessage):
            has_messages = True
            with st.chat_message("user"):
                st.markdown(msg.content)
        elif isinstance(msg, AIMessage):
            if msg.content and not msg.tool_calls:
                has_messages = True
                with st.chat_message("assistant"):
                    st.markdown(msg.content)

    # Empty state cuando no hay mensajes
    if not has_messages:
        st.markdown("""
        <div class="empty-state">
            <div class="empty-icon">✦</div>
            <div class="empty-title">¡Hola! Soy tu Mentor de Onboarding</div>
            <div class="empty-desc">
                Estoy aquí para guiarte en tu proceso de inducción corporativa.
                Pregúntame sobre políticas de la empresa, cursos, o pedime que organice tu agenda.
            </div>
        </div>
        """, unsafe_allow_html=True)

# Entrada de mensaje
if user_query := st.chat_input("Escribí tu consulta de onboarding acá..."):
    with st.chat_message("user"):
        st.markdown(user_query)

    st.session_state.chat_history.append(HumanMessage(content=user_query))

    # Auto-nombrar la sesión con el primer mensaje
    if st.session_state.session_name.startswith("Chat ") and len([m for m in st.session_state.chat_history if isinstance(m, HumanMessage)]) == 1:
        st.session_state.session_name = user_query[:40] + ("..." if len(user_query) > 40 else "")

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        st.session_state.log_history = []

        # ── Labels amigables para el indicador de progreso ──
        TOOL_LABELS = {
            "query_company_knowledge": "Consultando manuales de la empresa...",
            "query_user_profile":      "Leyendo tu perfil...",
            "save_user_profile":       "Guardando tu perfil...",
            "get_calendar_events":     "Revisando tu calendario...",
            "insert_calendar_event":   "Agendando el evento...",
            "delete_calendar_event":   "Eliminando el evento...",
            "update_calendar_event":   "Modificando el evento...",
            "find_available_slots":    "Buscando horarios libres...",
        }

        def _is_rate_limit(err: Exception) -> bool:
            s = str(err).lower()
            return "429" in s or "rate_limit" in s or "rate limit" in s

        def _is_tool_fail(err: Exception) -> bool:
            s = str(err).lower()
            return "400" in s or "tool_use_failed" in s

        try:
            inputs = {"messages": st.session_state.chat_history}
            final_response = ""

            with st.status("Pensando...", expanded=False) as status:
                for event in app.stream(inputs):
                    for node_name, value in event.items():
                        if "messages" not in value:
                            continue
                        for m in value["messages"]:
                            st.session_state.chat_history.append(m)

                            if isinstance(m, AIMessage):
                                if m.tool_calls:
                                    for tc in m.tool_calls:
                                        label = TOOL_LABELS.get(tc['name'], f"Ejecutando {tc['name']}...")
                                        status.update(label=label)
                                        st.session_state.log_history.append({
                                            "type": "tool_call",
                                            "title": f"Acción: {tc['name']}",
                                            "content": f"<code>{json.dumps(tc['args'], ensure_ascii=False)}</code>"
                                        })
                                else:
                                    final_response = m.content
                                    status.update(label="Redactando respuesta...", state="running")
                                    st.session_state.log_history.append({
                                        "type": "thought",
                                        "title": "Respuesta del Agente",
                                        "content": m.content[:200] + "..." if len(m.content) > 200 else m.content
                                    })

                            elif isinstance(m, ToolMessage):
                                status.update(label="Procesando resultado...")
                                content_preview = m.content[:300] + "..." if len(m.content) > 300 else m.content
                                st.session_state.log_history.append({
                                    "type": "tool_response",
                                    "title": f"Resultado: {m.name}",
                                    "content": content_preview
                                })

                status.update(label="Respuesta lista", state="complete", expanded=False)

            # Mostrar la respuesta final
            if final_response:
                response_placeholder.markdown(final_response)

            # Guardar sesión
            save_session(
                st.session_state.current_session_id,
                st.session_state.session_name,
                serialize_messages(st.session_state.chat_history),
                st.session_state.log_history,
                get_user_profile()
            )

            st.rerun()

        except Exception as e:
            err_str = str(e)
            if "429" in err_str or "rate_limit" in err_str.lower():
                st.warning(
                    "⏳ **Límite de tokens alcanzado.** El servicio de IA está temporalmente saturado. "
                    "Esperá 1-2 minutos e intentá de nuevo.",
                    icon="⚠️"
                )
                logging.warning(f"Groq rate limit: {err_str}")
            elif "400" in err_str or "tool_use_failed" in err_str.lower():
                st.warning(
                    "⚡ **Error en la ejecución de una herramienta.** Reformulá tu pregunta con más detalle "
                    "e intentá de nuevo.",
                    icon="⚠️"
                )
                logging.warning(f"Groq tool_use_failed: {err_str}")
            elif "token.json" in err_str or "autenticar" in err_str.lower():
                st.error(
                    "🔐 **Problema de autenticación con Google Calendar.** "
                    "El token expiró. Contactá al administrador para re-autenticar."
                )
            else:
                st.error(f"❌ Error inesperado: {err_str}")
                logging.error(f"Agent error: {err_str}")
