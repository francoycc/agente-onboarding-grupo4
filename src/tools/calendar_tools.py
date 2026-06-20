from langchain_core.tools import tool

@tool
def get_calendar_events(start_time: str, end_time: str) -> list:
    """Revisa la disponibilidad en el calendario en formato ISO 8601."""
    # Lógica de Google API
    return [{"event": "Reunión", "time": "10:00-11:00"}]

@tool
def insert_calendar_event(title: str, start_time: str, end_time: str, description: str) -> str:
    """Registra el evento en Google Calendar."""
    # Lógica de Google API
    return f"Evento '{title}' creado con éxito."