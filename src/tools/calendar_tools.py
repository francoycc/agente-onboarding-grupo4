# src/tools/calendar_tools.py
import os
import datetime
from langchain_core.tools import tool
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Función auxiliar para autenticar la API silenciosamente con token.json"""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        raise Exception("Falta token.json. Debes autenticar la app primero.")
    return build('calendar', 'v3', credentials=creds)

@tool
def get_calendar_events(start_time: str, end_time: str) -> str:
    """Obligatorio usar esta herramienta para revisar la disponibilidad del calendario.
    Input start_time y end_time DEBEN estar en formato ISO 8601 (ej. 2026-06-15T09:00:00-03:00)."""
    try:
        service = get_calendar_service()
        
        events_result = service.events().list(
            calendarId='primary', 
            timeMin=start_time,
            timeMax=end_time, 
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return "No hay eventos agendados en ese rango horario. Está totalmente libre."
        
        # Formatear la lista para que el LLM la entienda fácil
        event_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            event_list.append(f"- Evento: {event['summary']} (Desde: {start} Hasta: {end})")
            
        return "Eventos encontrados:\n" + "\n".join(event_list)
        
    except Exception as e:
        return f"Error en la API de Calendar: {str(e)}"

@tool
def insert_calendar_event(title: str, start_time: str, end_time: str, description: str) -> str:
    """Registra el evento en Google Calendar. 
    start_time y end_time en formato ISO 8601 (ej. 2026-06-15T09:00:00-03:00)."""
    try:
        service = get_calendar_service()
        event_body = {
            'summary': title,
            'description': description,
            'start': {'dateTime': start_time},
            'end': {'dateTime': end_time},
        }
        event = service.events().insert(calendarId='primary', body=event_body).execute()
        return f"¡Éxito! Evento '{title}' creado correctamente. Link: {event.get('htmlLink')}"
    except Exception as e:
        return f"Error al crear el evento: {str(e)}"