from src.tools.calendar_tools import get_calendar_service
try:
    get_calendar_service()
    print("¡Login exitoso!")
except Exception as e:
    print("Error:", e)