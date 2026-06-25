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
    [data-testid="stExpander"] {
        background: rgba(15,23,42,0.5) !important;
        border: 1px solid rgba(255,255,255,0.07) !important;
        border-radius: 12px !important;
        margin-bottom: 6px !important;
    }

    /* ── Panel Observabilidad ── */
    .obs-panel {
        background: linear-gradient(135deg, rgba(15,23,42,0.97), rgba(10,14,26,0.99));
        border: 1px solid rgba(129,140,248,0.2);
        border-radius: 20px;
        padding: 28px 32px;
        margin-bottom: 14px;
        animation: panelIn 0.4s cubic-bezier(0.16,1,0.3,1) forwards;
        backdrop-filter: blur(20px);
    }
    @keyframes panelIn {
        from {opacity:0; transform:translateY(-12px);}
        to   {opacity:1; transform:translateY(0);}
    }
    .obs-panel-header {
        display: flex;
        align-items: center;
        gap: 16px;
        margin-bottom: 22px;
        padding-bottom: 18px;
        border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .obs-panel-icon {
        font-size: 1.6rem;
        width: 50px; height: 50px;
        background: rgba(129,140,248,0.1);
        border: 1px solid rgba(129,140,248,0.2);
        border-radius: 14px;
        display: flex; align-items: center; justify-content: center;
        flex-shrink: 0;
    }
    .obs-panel-title {
        font-size: 1.05rem;
        font-weight: 800;
        color: #f1f5f9;
        letter-spacing: -0.02em;
    }
    .obs-panel-sub {
        font-size: 0.78rem;
        color: #64748b;
        margin-top: 3px;
    }
    /* Diagrama arquitectura */
    .obs-arch-flow {
        display: flex;
        align-items: stretch;
        justify-content: center;
        gap: 0;
        margin-bottom: 20px;
        flex-wrap: wrap;
        gap: 8px;
    }
    .obs-arch-node {
        text-align: center;
        padding: 16px 22px;
        border-radius: 16px;
        border: 1px solid;
        min-width: 115px;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        flex: 1;
        max-width: 160px;
    }
    .obs-arch-node:hover { transform: translateY(-4px); box-shadow: 0 8px 24px rgba(0,0,0,0.35); }
    .obs-arch-icon { font-size: 1.6rem; margin-bottom: 6px; }
    .obs-arch-name { font-size: 0.85rem; font-weight: 700; color: #f1f5f9; margin-bottom: 2px; }
    .obs-arch-tech { font-size: 0.66rem; color: #64748b; font-weight: 500; }
    .obs-arch-desc { font-size: 0.68rem; color: #475569; margin-top: 5px; line-height: 1.4; }
    .obs-ui     { background: rgba(99,102,241,0.12); border-color: rgba(99,102,241,0.3); }
    .obs-agent  { background: rgba(192,132,252,0.12); border-color: rgba(192,132,252,0.3); }
    .obs-llm    { background: rgba(245,158,11,0.12); border-color: rgba(245,158,11,0.3); }
    .obs-rag    { background: rgba(16,185,129,0.12); border-color: rgba(16,185,129,0.3); }
    .obs-cal    { background: rgba(251,113,133,0.12); border-color: rgba(251,113,133,0.3); }
    .obs-profile{ background: rgba(14,165,233,0.12); border-color: rgba(14,165,233,0.3); }
    .obs-arch-conn {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 3px;
        padding: 0 6px;
        flex-shrink: 0;
    }
    .obs-arch-line {
        width: 32px; height: 2px;
        background: linear-gradient(90deg, rgba(129,140,248,0.3), rgba(129,140,248,0.8));
        border-radius: 2px;
    }
    .obs-arch-arrowhead {
        font-size: 0.75rem;
        color: rgba(129,140,248,0.7);
        margin-top: -3px;
    }
    .obs-arch-conn-label {
        font-size: 0.58rem;
        color: #475569;
        font-weight: 600;
        letter-spacing: 0.05em;
        white-space: nowrap;
    }
    .obs-tools-separator {
        text-align: center;
        font-size: 0.68rem;
        color: #475569;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
        margin: 16px 0 12px 0;
        display: flex;
        align-items: center;
        gap: 12px;
    }
    .obs-tools-separator::before, .obs-tools-separator::after {
        content: '';
        flex: 1;
        height: 1px;
        background: rgba(255,255,255,0.06);
    }
    .obs-arch-tools-row {
        display: flex;
        gap: 10px;
        justify-content: center;
        flex-wrap: wrap;
    }
    .obs-arch-tool {
        text-align: center;
        padding: 14px 16px;
        border-radius: 14px;
        border: 1px solid;
        min-width: 140px;
        flex: 1;
        max-width: 200px;
        transition: transform 0.2s ease;
    }
    .obs-arch-tool:hover { transform: translateY(-3px); }
    /* Traza timeline */
    .obs-step {
        display: flex;
        gap: 14px;
        align-items: flex-start;
    }
    .obs-step-left {
        display: flex;
        flex-direction: column;
        align-items: center;
        flex-shrink: 0;
        width: 32px;
    }
    .obs-step-num {
        width: 32px; height: 32px;
        border-radius: 50%;
        display: flex; align-items: center; justify-content: center;
        font-size: 0.78rem;
        font-weight: 800;
        color: #fff;
        flex-shrink: 0;
        position: relative;
        z-index: 1;
    }
    .obs-step-vline {
        width: 2px;
        flex: 1;
        min-height: 24px;
        margin: 4px 0;
        border-radius: 2px;
    }
    .obs-step-right {
        padding-bottom: 18px;
        flex: 1;
        min-width: 0;
    }
    .obs-step-badge {
        display: inline-block;
        font-size: 0.6rem;
        font-weight: 800;
        letter-spacing: 0.07em;
        text-transform: uppercase;
        padding: 2px 9px;
        border-radius: 20px;
        margin-bottom: 5px;
    }
    .obs-step-title {
        font-size: 0.9rem;
        font-weight: 700;
        color: #e2e8f0;
        margin-bottom: 3px;
    }
    .obs-step-desc {
        font-size: 0.81rem;
        color: #94a3b8;
        line-height: 1.5;
    }
    /* Tech tags */
    .obs-tech-row {
        display: flex;
        flex-wrap: wrap;
        gap: 6px;
        margin-top: 18px;
        padding-top: 16px;
        border-top: 1px solid rgba(255,255,255,0.05);
    }
    .obs-tech-tag {
        font-size: 0.67rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        color: #64748b;
    }
    /* Backward compat: keep old wf-* classes as stubs so nothing breaks */
    .workflow-panel {
        background: linear-gradient(135deg, rgba(15,23,42,0.95), rgba(10,14,26,0.98));
        border: 1px solid rgba(129,140,248,0.25);
        border-radius: 20px;
        padding: 28px 32px;
        margin-bottom: 28px;
        animation: panelIn 0.4s cubic-bezier(0.16,1,0.3,1) forwards;
        backdrop-filter: blur(20px);
    }
    @keyframes panelIn {
        from {opacity:0; transform:translateY(-16px);}
        to   {opacity:1; transform:translateY(0);}
    }
    .wf-title {
        font-size: 1.1rem;
        font-weight: 800;
        color: #f1f5f9;
        letter-spacing: -0.02em;
        margin-bottom: 4px;
    }
    .wf-subtitle {
        font-size: 0.8rem;
        color: #64748b;
        margin-bottom: 24px;
    }
    /* Nodos del diagrama */
    .wf-diagram {
        display: flex;
        align-items: center;
        gap: 0;
        overflow-x: auto;
        padding: 8px 0 16px 0;
        flex-wrap: nowrap;
    }
    .wf-node {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 8px;
        min-width: 100px;
        flex-shrink: 0;
    }
    .wf-node-box {
        width: 88px;
        height: 72px;
        border-radius: 14px;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        gap: 4px;
        font-size: 0.68rem;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
        border: 1px solid;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .wf-node-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    }
    .wf-node-icon { font-size: 1.4rem; }
    .wf-node-label { font-size: 0.85rem; color: #94a3b8; font-weight: 500; text-transform: none; letter-spacing: 0; }
    /* Colores por nodo */
    .wf-ui    { background: rgba(99,102,241,0.15); border-color: rgba(99,102,241,0.4); color: #a5b4fc; }
    .wf-agent { background: rgba(192,132,252,0.15); border-color: rgba(192,132,252,0.4); color: #d8b4fe; }
    .wf-llm   { background: rgba(251,191,36,0.12);  border-color: rgba(251,191,36,0.35); color: #fde68a; }
    .wf-rag   { background: rgba(52,211,153,0.12);  border-color: rgba(52,211,153,0.35); color: #6ee7b7; }
    .wf-cal   { background: rgba(251,113,133,0.12); border-color: rgba(251,113,133,0.35); color: #fda4af; }
    /* Flechas */
    .wf-arrow {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 2px;
        padding: 0 4px;
        flex-shrink: 0;
    }
    .wf-arrow-line {
        width: 36px;
        height: 2px;
        background: linear-gradient(90deg, rgba(129,140,248,0.4), rgba(129,140,248,0.8));
        border-radius: 2px;
        position: relative;
    }
    .wf-arrow-label {
        font-size: 0.6rem;
        color: #475569;
        font-weight: 600;
        letter-spacing: 0.05em;
        white-space: nowrap;
    }
    /* Sección de traza viva */
    .wf-trace-section {
        margin-top: 24px;
        border-top: 1px solid rgba(255,255,255,0.06);
        padding-top: 20px;
    }
    .wf-trace-title {
        font-size: 0.75rem;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        color: #475569;
        font-weight: 700;
        margin-bottom: 12px;
    }
    .wf-step {
        display: flex;
        gap: 12px;
        margin-bottom: 10px;
        align-items: flex-start;
    }
    .wf-step-badge {
        font-size: 0.65rem;
        font-weight: 700;
        padding: 3px 8px;
        border-radius: 6px;
        white-space: nowrap;
        flex-shrink: 0;
        margin-top: 2px;
    }
    .wf-badge-user   { background: rgba(99,102,241,0.2);  color: #a5b4fc; border: 1px solid rgba(99,102,241,0.3); }
    .wf-badge-agent  { background: rgba(192,132,252,0.2); color: #d8b4fe; border: 1px solid rgba(192,132,252,0.3); }
    .wf-badge-tool   { background: rgba(251,191,36,0.15);  color: #fde68a; border: 1px solid rgba(251,191,36,0.3); }
    .wf-badge-rag    { background: rgba(52,211,153,0.15);  color: #6ee7b7; border: 1px solid rgba(52,211,153,0.3); }
    .wf-badge-result { background: rgba(251,113,133,0.15); color: #fda4af; border: 1px solid rgba(251,113,133,0.3); }
    .wf-badge-resp   { background: rgba(129,140,248,0.2);  color: #c7d2fe; border: 1px solid rgba(129,140,248,0.3); }
    .wf-step-content {
        font-size: 0.82rem;
        color: #94a3b8;
        line-height: 1.5;
        flex: 1;
    }
    .wf-step-content code {
        background: rgba(255,255,255,0.06);
        padding: 1px 5px;
        border-radius: 4px;
        font-size: 0.78rem;
        color: #cbd5e1;
    }
    /* Leyenda tecnologías */
    .wf-tech-row {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        margin-top: 20px;
        border-top: 1px solid rgba(255,255,255,0.05);
        padding-top: 16px;
    }
    .wf-tech-badge {
        font-size: 0.68rem;
        font-weight: 600;
        padding: 4px 10px;
        border-radius: 20px;
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.1);
        color: #64748b;
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
        "traces": st.session_state.get("traces", []),
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
if "traces" not in st.session_state:
    st.session_state.traces = []  # lista de trazas, una por respuesta del agente
if "session_name" not in st.session_state:
    st.session_state.session_name = ""
if "session_created_at" not in st.session_state:
    st.session_state.session_created_at = datetime.now().isoformat()


def start_new_session():
    sid = uuid.uuid4().hex[:10]
    st.session_state.current_session_id = sid
    st.session_state.chat_history = []
    st.session_state.log_history = []
    st.session_state.traces = []
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
    st.session_state.traces = session_data.get("traces", [])
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
            ltype = log.get("type", "")
            if ltype == "user_input":
                icon, css_class = "▸", ""
            elif ltype in ("llm_decision", "llm_response", "thought"):
                icon, css_class = "🧠", ""
            elif ltype == "tool_call":
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

# ── (El panel lateral de flujo fue eliminado para centrarse en la traza por mensaje) ──

# ── BLOQUE ANTERIOR (eliminado) —— inicio marcador ficticio ──
if False:  # dead code — se mantiene para no romper nada
    _diagram_html_old = """
    <div class="workflow-panel">
        <div class="wf-title">Flujo de Trabajo — Arquitectura del Sistema</div>
        <div class="wf-subtitle">Cómo interactúan los componentes para responder cada mensaje</div>

        <div class="wf-diagram">
            <div class="wf-node">
                <div class="wf-node-box wf-ui">
                    <span class="wf-node-icon">💬</span>
                    <span>UI</span>
                </div>
                <span class="wf-node-label">Streamlit</span>
            </div>
            <div class="wf-arrow">
                <div class="wf-arrow-line"></div>
                <span class="wf-arrow-label">mensaje</span>
            </div>
            <div class="wf-node">
                <div class="wf-node-box wf-agent">
                    <span class="wf-node-icon">🔁</span>
                    <span>Agente</span>
                </div>
                <span class="wf-node-label">LangGraph</span>
            </div>
            <div class="wf-arrow">
                <div class="wf-arrow-line"></div>
                <span class="wf-arrow-label">prompt</span>
            </div>
            <div class="wf-node">
                <div class="wf-node-box wf-llm">
                    <span class="wf-node-icon">🧠</span>
                    <span>LLM</span>
                </div>
                <span class="wf-node-label">Groq / Llama</span>
            </div>
            <div class="wf-arrow">
                <div class="wf-arrow-line"></div>
                <span class="wf-arrow-label">tool call</span>
            </div>
            <div class="wf-node">
                <div class="wf-node-box wf-rag">
                    <span class="wf-node-icon">📚</span>
                    <span>RAG</span>
                </div>
                <span class="wf-node-label">ChromaDB</span>
            </div>
            <div class="wf-arrow">
                <div class="wf-arrow-line"></div>
                <span class="wf-arrow-label">resultado</span>
            </div>
            <div class="wf-node">
                <div class="wf-node-box wf-cal">
                    <span class="wf-node-icon">📅</span>
                    <span>Calendar</span>
                </div>
                <span class="wf-node-label">Google API</span>
            </div>
        </div>

        <div class="wf-tech-row">
            <span class="wf-tech-badge">Python 3.11</span>
            <span class="wf-tech-badge">Streamlit</span>
            <span class="wf-tech-badge">LangGraph</span>
            <span class="wf-tech-badge">LangChain</span>
            <span class="wf-tech-badge">Groq API</span>
            <span class="wf-tech-badge">meta-llama/llama-4-scout-17b-16e-instruct</span>
            <span class="wf-tech-badge">ChromaDB</span>
            <span class="wf-tech-badge">HuggingFace Embeddings</span>
            <span class="wf-tech-badge">Google Calendar API</span>
            <span class="wf-tech-badge">OAuth 2.0</span>
            <span class="wf-tech-badge">ReAct Pattern</span>
        </div>
    </div>
    """
    st.markdown(diagram_html, unsafe_allow_html=True)

    # ── Traza viva de la última interacción ──
    if st.session_state.log_history:
        steps_html = ""
        # Reconstruir flujo desde log_history
        for log in st.session_state.log_history:
            if log["type"] == "thought":
                badge = '<span class="wf-step-badge wf-badge-resp">RESPUESTA LLM</span>'
            elif log["type"] == "tool_call":
                tool_name = log["title"].replace("Acción: ", "")
                if "rag" in tool_name or "knowledge" in tool_name or "profile" in tool_name:
                    badge = f'<span class="wf-step-badge wf-badge-rag">RAG / PERFIL</span>'
                elif "calendar" in tool_name or "event" in tool_name or "slots" in tool_name:
                    badge = f'<span class="wf-step-badge wf-badge-tool">CALENDAR</span>'
                else:
                    badge = f'<span class="wf-step-badge wf-badge-agent">AGENTE</span>'
            else:
                badge = '<span class="wf-step-badge wf-badge-result">RESULTADO</span>'

            steps_html += f"""
            <div class="wf-step">
                {badge}
                <div class="wf-step-content">
                    <strong style="color:#e2e8f0;">{log['title']}</strong><br>
                    {log['content']}
                </div>
            </div>
            """

        trace_html = f"""
        <div class="workflow-panel" style="animation-delay:0.1s;">
            <div class="wf-title">Traza de la Última Interacción</div>
            <div class="wf-subtitle">Pasos ejecutados por el agente para responder tu último mensaje</div>
            <div class="wf-trace-section">
                <div class="wf-trace-title">Secuencia de ejecución — {len(st.session_state.log_history)} pasos</div>
                {steps_html}
            </div>
        </div>
        """
        st.markdown(trace_html, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="workflow-panel" style="text-align:center; padding: 24px 32px;">
            <div style="font-size:2rem; margin-bottom:8px;">⬡</div>
            <div style="color:#64748b; font-size:0.88rem;">Todavía no hay interacciones en esta sesión.<br>Enviá un mensaje al agente para ver la traza en tiempo real.</div>
        </div>
        """, unsafe_allow_html=True)

# Renderizar historial de chat
# ──────────────────────────────────────────────────────────────────
# FUNCIÓN: Renderizar traza de ejecución inline (por mensaje)
# ──────────────────────────────────────────────────────────────────
def render_trace_inline(trace_steps: list):
    """Muestra la traza completa de un mensaje en texto legible (logs de LLM y Tools)."""
    st.markdown("---")
    st.markdown("**Flujo de Ejecución (Observabilidad Técnica):**")
    
    for i, step in enumerate(trace_steps):
        ltype = step.get("type", "")
        title = step.get("title", "")
        content = step.get("content", "")
        details = step.get("details", "")

        import re
        content_plain = re.sub(r"<[^>]+>", "", content)

        if ltype == "user_input":
            st.markdown(f"**Paso {i+1}: Entrada del Usuario**")
            st.code(details or content_plain, language="text")

        elif ltype == "llm_decision":
            st.markdown(f"**Paso {i+1}: LLM - Razonamiento y Llamada a Herramientas**")
            st.markdown("*El LLM decidió utilizar las siguientes herramientas:*")
            if details:
                st.code(details, language="json")

        elif ltype == "tool_call":
            st.markdown(f"**Paso {i+1}: Herramienta - Invocación (Entrada)**")
            st.markdown(f"Función Invocada: `{title}`")
            if details:
                st.markdown("*Argumentos (Input):*")
                st.code(details, language="json")

        elif ltype == "tool_response":
            st.markdown(f"**Paso {i+1}: Herramienta - Resultado (Salida)**")
            if details:
                st.markdown("*Respuesta de la Herramienta (Output):*")
                display = details if len(details) <= 2000 else details[:2000] + "\n\n... [Contenido truncado a 2000 caracteres]"
                st.code(display, language="text")

        elif ltype in ("llm_response", "thought"):
            st.markdown(f"**Paso {i+1}: LLM - Generación de Respuesta Final**")
            st.markdown("*Respuesta pura generada por el LLM:*")
            if details:
                st.code(details, language="markdown")

        if i < len(trace_steps) - 1:
            st.markdown("---")


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
    ai_response_idx = 0  # índice para mapear AI responses con sus trazas
    
    total_ai_msgs = sum(1 for msg in st.session_state.chat_history if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls)
    traces_len = len(st.session_state.traces)
    offset = total_ai_msgs - traces_len

    def _toggle_trace_view(key: str):
        st.session_state[key] = not st.session_state.get(key, False)

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
                    # Botón de traza por mensaje
                    trace_idx = ai_response_idx - offset
                    has_trace = 0 <= trace_idx < traces_len
                    if has_trace:
                        trace_key = f"trace_visible_{trace_idx}"
                        is_open = st.session_state.get(trace_key, False)
                        btn_label = "Ocultar flujo de trabajo" if is_open else "Ver flujo de trabajo"
                        st.button(
                            btn_label,
                            key=f"trace_btn_{trace_idx}",
                            on_click=_toggle_trace_view,
                            args=(trace_key,)
                        )
                        if is_open:
                            with st.container():
                                render_trace_inline(st.session_state.traces[trace_idx])
                ai_response_idx += 1

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

        # ── Logging: captura mensaje del usuario como primer paso ──
        st.session_state.log_history.append({
            "type": "user_input",
            "title": "Consulta del Usuario",
            "content": "Mensaje recibido y enviado al agente.",
            "details": user_query
        })

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
        TOOL_DESCRIPTIONS = {
            "query_company_knowledge": "Búsqueda semántica sobre la base vectorial ChromaDB usando embeddings HuggingFace (all-MiniLM-L6-v2). Recupera los fragmentos del manual más relevantes para la consulta.",
            "query_user_profile":      "Lee el perfil del empleado guardado localmente en data/user_profile.json.",
            "save_user_profile":       "Persiste el perfil del empleado (nombre, rol, seniority, horario, preferencias) en data/user_profile.json.",
            "get_calendar_events":     "Obtiene los eventos de Google Calendar del usuario en un rango de fechas vía API REST.",
            "insert_calendar_event":   "Crea un nuevo evento en Google Calendar con título, descripción, hora de inicio y fin.",
            "delete_calendar_event":   "Busca y elimina un evento en Google Calendar por nombre y fecha.",
            "update_calendar_event":   "Modifica campos específicos de un evento existente en Google Calendar.",
            "find_available_slots":    "Analiza el calendario del usuario y encuentra horarios disponibles en un día dado.",
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
            llm_round = 0

            with st.status("Pensando...", expanded=False) as status:
                for event in app.stream(inputs):
                    for node_name, value in event.items():
                        if "messages" not in value:
                            continue
                        for m in value["messages"]:
                            st.session_state.chat_history.append(m)

                            if isinstance(m, AIMessage):
                                if m.tool_calls:
                                    llm_round += 1
                                    tool_names = [tc['name'] for tc in m.tool_calls]
                                    # Log: LLM decidió invocar herramientas
                                    st.session_state.log_history.append({
                                        "type": "llm_decision",
                                        "title": f"LLM — Razonamiento (turno {llm_round})",
                                        "content": f"El modelo analizó el contexto y decidió invocar: <strong>{', '.join(tool_names)}</strong>",
                                        "details": json.dumps({
                                            "modelo": "meta-llama/llama-4-scout-17b-16e-instruct",
                                            "proveedor": "Groq",
                                            "patron": "ReAct (Reasoning + Acting)",
                                            "turno_de_razonamiento": llm_round,
                                            "herramientas_elegidas": tool_names
                                        }, indent=2, ensure_ascii=False)
                                    })
                                    for tc in m.tool_calls:
                                        label = TOOL_LABELS.get(tc['name'], f"Ejecutando {tc['name']}...")
                                        status.update(label=label)
                                        st.session_state.log_history.append({
                                            "type": "tool_call",
                                            "title": f"Tool invocada: {tc['name']}",
                                            "content": TOOL_DESCRIPTIONS.get(tc['name'], tc['name']),
                                            "details": json.dumps(tc['args'], indent=2, ensure_ascii=False)
                                        })
                                else:
                                    final_response = m.content
                                    status.update(label="Redactando respuesta...", state="running")
                                    st.session_state.log_history.append({
                                        "type": "llm_response",
                                        "title": "LLM — Respuesta Final",
                                        "content": "El modelo sintetizó toda la información recopilada y generó la respuesta al usuario.",
                                        "details": m.content
                                    })

                            elif isinstance(m, ToolMessage):
                                status.update(label="Procesando resultado...")
                                char_count = len(m.content)
                                st.session_state.log_history.append({
                                    "type": "tool_response",
                                    "title": f"Resultado de: {m.name}",
                                    "content": f"La herramienta retornó <strong>{char_count} caracteres</strong> de datos al agente.",
                                    "details": m.content[:4000]
                                })

                status.update(label="Respuesta lista", state="complete", expanded=False)

            # Guardar traza de esta interacción
            st.session_state.traces.append(list(st.session_state.log_history))

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
