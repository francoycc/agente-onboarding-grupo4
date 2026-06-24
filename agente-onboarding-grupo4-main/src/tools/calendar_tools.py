# src/tools/calendar_tools.py
import os
import json
import datetime
from langchain_core.tools import tool
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/calendar']

def get_calendar_service():
    """Función auxiliar para autenticar la API silenciosamente con token.json.
    Incluye lógica de refresco automático del token cuando expira."""
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    if not creds:
        raise Exception("Falta token.json. Ejecutá auth.py primero para autenticar la app.")

    # Si el token expiró pero hay refresh_token, renovarlo automáticamente
    if not creds.valid:
        if creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
                # Guardar el token renovado a disco
                with open('token.json', 'w') as f:
                    f.write(creds.to_json())
            except Exception as e:
                raise Exception(f"No se pudo renovar el token de Google. Re-autenticá con auth.py. Error: {e}")
        else:
            raise Exception("Token inválido o expirado. Ejecutá auth.py para re-autenticar.")

    return build('calendar', 'v3', credentials=creds)


@tool
def get_calendar_events(start_time: str, end_time: str) -> str:
    """Obligatorio usar esta herramienta para revisar la disponibilidad del calendario.
    Input start_time y end_time DEBEN estar en formato ISO 8601 (ej. 2026-06-15T09:00:00-03:00).
    También retorna el ID de cada evento, útil para eliminar o modificar luego."""
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

        event_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            event_id = event.get('id', 'sin-id')
            event_list.append(
                f"- ID: {event_id} | Evento: {event['summary']} (Desde: {start} Hasta: {end})"
            )

        return "Eventos encontrados:\n" + "\n".join(event_list)

    except Exception as e:
        return f"Error en la API de Calendar: {str(e)}"


@tool
def insert_calendar_event(title: str, start_time: str, end_time: str, description: str) -> str:
    """Registra el evento en Google Calendar si no hay superposiciones.
    start_time y end_time en formato ISO 8601 (ej. 2026-06-15T09:00:00-03:00)."""
    try:
        service = get_calendar_service()

        # Verificar superposición primero (overlapping)
        events_result = service.events().list(
            calendarId='primary',
            timeMin=start_time,
            timeMax=end_time,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])
        if events:
            conflicts = []
            for event in events:
                start = event['start'].get('dateTime', event['start'].get('date'))
                end = event['end'].get('dateTime', event['end'].get('date'))
                conflicts.append(f"'{event['summary']}' (desde {start} hasta {end})")
            return (
                f"Error: Conflicto de horarios detectado. No se puede agendar '{title}' "
                f"porque se superpone con: {', '.join(conflicts)}. "
                f"Por favor, buscá otro horario libre con find_available_slots."
            )

        event_body = {
            'summary': title,
            'description': description,
            'start': {'dateTime': start_time, 'timeZone': 'America/Argentina/Buenos_Aires'},
            'end': {'dateTime': end_time, 'timeZone': 'America/Argentina/Buenos_Aires'},
        }
        event = service.events().insert(calendarId='primary', body=event_body).execute()
        return f"¡Éxito! Evento '{title}' creado correctamente. Link: {event.get('htmlLink')} | ID: {event.get('id')}"

    except Exception as e:
        return f"Error al crear el evento: {str(e)}"


@tool
def delete_calendar_event(event_title: str, date: str) -> str:
    """Elimina un evento del calendario buscándolo por nombre y fecha.
    - event_title: Nombre (o parte del nombre) del evento a eliminar.
    - date: Fecha del evento en formato AAAA-MM-DD.
    Si hay múltiples coincidencias, lista los eventos encontrados y pide confirmación."""
    try:
        service = get_calendar_service()

        # Buscar en todo el día indicado
        if 'T' in date:
            date = date.split('T')[0]

        tz_suffix = "-03:00"
        day_start = f"{date}T00:00:00{tz_suffix}"
        day_end = f"{date}T23:59:59{tz_suffix}"

        events_result = service.events().list(
            calendarId='primary',
            timeMin=day_start,
            timeMax=day_end,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            return f"No se encontraron eventos para el {date}. No hay nada que eliminar."

        # Filtrar por título (búsqueda parcial, case-insensitive)
        matches = [
            e for e in events
            if event_title.lower() in e.get('summary', '').lower()
        ]

        if not matches:
            available = [e.get('summary', 'Sin título') for e in events]
            return (
                f"No se encontró ningún evento con el nombre '{event_title}' el {date}. "
                f"Los eventos existentes ese día son: {', '.join(available)}."
            )

        if len(matches) > 1:
            options = []
            for e in matches:
                start = e['start'].get('dateTime', e['start'].get('date'))
                options.append(f"- ID: {e['id']} | '{e['summary']}' a las {start}")
            return (
                f"Se encontraron {len(matches)} eventos con ese nombre el {date}. "
                f"Por favor especificá cuál eliminar:\n" + "\n".join(options)
            )

        # Exactamente 1 coincidencia — eliminar
        event_to_delete = matches[0]
        event_id = event_to_delete['id']
        event_name = event_to_delete.get('summary', 'Sin título')
        event_start = event_to_delete['start'].get('dateTime', event_to_delete['start'].get('date'))

        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return f"✓ Evento '{event_name}' (programado para {event_start}) eliminado exitosamente del calendario."

    except Exception as e:
        return f"Error al eliminar el evento: {str(e)}"


@tool
def update_calendar_event(
    event_title: str,
    date: str,
    new_title: str = "",
    new_start_time: str = "",
    new_end_time: str = "",
    new_description: str = ""
) -> str:
    """Modifica un evento existente en el calendario. Buscá el evento por nombre y fecha,
    luego actualizá solo los campos que el usuario quiere cambiar.
    - event_title: Nombre actual del evento a modificar.
    - date: Fecha actual del evento (AAAA-MM-DD).
    - new_title: Nuevo nombre (dejar vacío para no cambiar).
    - new_start_time: Nueva hora de inicio en ISO 8601 (dejar vacío para no cambiar).
    - new_end_time: Nueva hora de fin en ISO 8601 (dejar vacío para no cambiar).
    - new_description: Nueva descripción (dejar vacío para no cambiar)."""
    try:
        service = get_calendar_service()

        if 'T' in date:
            date = date.split('T')[0]

        tz_suffix = "-03:00"
        day_start = f"{date}T00:00:00{tz_suffix}"
        day_end = f"{date}T23:59:59{tz_suffix}"

        events_result = service.events().list(
            calendarId='primary',
            timeMin=day_start,
            timeMax=day_end,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        if not events:
            return f"No se encontraron eventos para el {date}."

        # Filtrar por título
        matches = [
            e for e in events
            if event_title.lower() in e.get('summary', '').lower()
        ]

        if not matches:
            available = [e.get('summary', 'Sin título') for e in events]
            return (
                f"No se encontró ningún evento con el nombre '{event_title}' el {date}. "
                f"Los eventos existentes ese día son: {', '.join(available)}."
            )

        if len(matches) > 1:
            options = []
            for e in matches:
                start = e['start'].get('dateTime', e['start'].get('date'))
                options.append(f"- '{e['summary']}' a las {start}")
            return (
                f"Se encontraron {len(matches)} eventos con ese nombre. "
                f"Por favor especificá mejor cuál modificar:\n" + "\n".join(options)
            )

        # Exactamente 1 coincidencia — modificar
        event = matches[0]
        event_id = event['id']

        # Aplicar cambios solo a los campos no vacíos
        if new_title:
            event['summary'] = new_title
        if new_description:
            event['description'] = new_description
        if new_start_time:
            event['start'] = {
                'dateTime': new_start_time,
                'timeZone': 'America/Argentina/Buenos_Aires'
            }
        if new_end_time:
            event['end'] = {
                'dateTime': new_end_time,
                'timeZone': 'America/Argentina/Buenos_Aires'
            }

        updated = service.events().update(
            calendarId='primary', eventId=event_id, body=event
        ).execute()

        return (
            f"✓ Evento actualizado correctamente. "
            f"Nuevo título: '{updated.get('summary')}' | "
            f"Link: {updated.get('htmlLink')}"
        )

    except Exception as e:
        return f"Error al modificar el evento: {str(e)}"


@tool
def find_available_slots(date: str, duration_minutes: int) -> str:
    """Analiza la agenda para una fecha determinada (formato AAAA-MM-DD) y devuelve las franjas horarias libres
    dentro del horario laboral (09:00 a 18:00, GTM-3) con la duración mínima especificada (en minutos)."""
    try:
        # Extraer solo la fecha AAAA-MM-DD
        if 'T' in date:
            date = date.split('T')[0]

        service = get_calendar_service()

        tz_suffix = "-03:00"
        work_start_str = f"{date}T09:00:00{tz_suffix}"
        work_end_str = f"{date}T18:00:00{tz_suffix}"

        work_start = datetime.datetime.fromisoformat(work_start_str)
        work_end = datetime.datetime.fromisoformat(work_end_str)

        events_result = service.events().list(
            calendarId='primary',
            timeMin=work_start_str,
            timeMax=work_end_str,
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        events = events_result.get('items', [])

        occupied_slots = []
        for event in events:
            start_raw = event['start'].get('dateTime', event['start'].get('date'))
            end_raw = event['end'].get('dateTime', event['end'].get('date'))

            if len(start_raw) == 10:
                start_dt = datetime.datetime.fromisoformat(f"{start_raw}T00:00:00{tz_suffix}")
                end_dt = datetime.datetime.fromisoformat(f"{end_raw}T23:59:59{tz_suffix}")
            else:
                start_dt = datetime.datetime.fromisoformat(start_raw)
                end_dt = datetime.datetime.fromisoformat(end_raw)

            start_dt = max(start_dt, work_start)
            end_dt = min(end_dt, work_end)

            if start_dt < end_dt:
                occupied_slots.append((start_dt, end_dt))

        occupied_slots.sort(key=lambda x: x[0])
        merged_slots = []
        for slot in occupied_slots:
            if not merged_slots:
                merged_slots.append(slot)
            else:
                prev_start, prev_end = merged_slots[-1]
                curr_start, curr_end = slot
                if curr_start <= prev_end:
                    merged_slots[-1] = (prev_start, max(prev_end, curr_end))
                else:
                    merged_slots.append(slot)

        free_slots = []
        current_time = work_start
        min_delta = datetime.timedelta(minutes=duration_minutes)

        for start_occ, end_occ in merged_slots:
            if start_occ - current_time >= min_delta:
                free_slots.append((current_time, start_occ))
            current_time = max(current_time, end_occ)

        if work_end - current_time >= min_delta:
            free_slots.append((current_time, work_end))

        if not free_slots:
            return f"No hay franjas libres de {duration_minutes} minutos en el horario laboral (09:00 a 18:00) para el día {date}."

        result = [f"- De {slot[0].strftime('%H:%M')} a {slot[1].strftime('%H:%M')}" for slot in free_slots]
        return f"Franjas horarias libres para el {date} (09:00-18:00):\n" + "\n".join(result)

    except Exception as e:
        return f"Error al calcular franjas horarias libres: {str(e)}"