import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Mismo alcance que definiste en calendar_tools.py
SCOPES = ['https://www.googleapis.com/auth/calendar']

def main():
    creds = None
    # Si ya existe un token, intentamos cargarlo
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # Si no hay credenciales válidas, iniciamos el flujo
    if not creds or not creds.valid:
        print("Iniciando flujo de autenticación...")
        # Asegurate de tener 'credentials.json' en la misma carpeta
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        
        # Guardar las credenciales para la próxima vez
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
        print("¡Token generado exitosamente en 'token.json'!")
    else:
        print("Ya tienes credenciales válidas.")

if __name__ == '__main__':
    main()