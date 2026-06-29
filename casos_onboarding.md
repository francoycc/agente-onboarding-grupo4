Suite de Casos de Prueba (QA) — Mentor de Onboarding Corporativo

Tecnología & Innovación S.A. | Versión del Manual: 3.1 (Junio 2026)
Proyecto de Cátedra — Grupo 4 · UTN Santa Fe

Este documento define la suite de pruebas de aceptación para validar el comportamiento semántico (RAG sobre ChromaDB) y dinámico (Google Calendar API) del agente autónomo.

Matriz de Cobertura de Pruebas

ID

Sección del Manual

Entrada de Prueba (User Input)

Comportamiento Esperado (RAG + Tools)

Respuesta Esperada

P-01

Sección 1: Cultura

"¿Cuál es la misión y visión de la empresa?"

Llama a query_company_knowledge con "misión y visión de la empresa".

Debe recitar textualmente la misión (soluciones de impacto con bienestar) y visión (Latinoamérica para 2030).

P-02

Sección 5: Beneficios

"¿Qué beneficios de cobertura médica me ofrece la empresa?"

Llama a query_company_knowledge con "beneficios cobertura médica".

Debe especificar la bonificación de OSDE 410 (70% empleado, 50% grupo familiar).

P-03

Sección 5: Capacitación

"Quiero comprarme un curso de Java de USD 150, ¿la empresa me lo cubre? ¿Cómo hago?"

Llama a query_company_knowledge con "presupuesto capacitación". Aplica inferencia lógica ($150 \le 500$).

Debe confirmar el presupuesto anual de USD 500 e indicar explícitamente que el gasto de USD 150 está completamente cubierto.

P-04

Sección 6: Conducta

"Estuve recibiendo tratos de acoso y discriminación por Slack por un compañero, ¿cómo se maneja la empresa?"

Llama a query_company_knowledge con "política anti-discriminación y anti-acoso". (Bypass de alineación activo).

Debe empatizar formalmente, advertir tolerancia cero, indicar que conlleva la desvinculación inmediata y dirigir al canal anónimo en "Ética y Conducta".

P-05

Sección 8: Procesos

"¿Cómo es el proceso de revisión de código para staging?"

Llama a query_company_knowledge con "proceso de code review y pull request".

Debe listar los requisitos: crear PR, requerir 2 aprobaciones (senior + Tech Lead) y un coverage de tests mínimo del 80% en SonarQube.

P-06

Sección 8: Despliegue

"¿Puedo hacer un despliegue de mi base de datos a producción un viernes a las 17:30 hs?"

Llama a query_company_knowledge con "días y horarios de despliegue en producción". El guardrail de código intercepta.

Debe denegar rotundamente el despliegue citando que solo se permiten los martes y jueves de 10:00 a 16:00 hs según la Sección 8 del manual.

P-07

Sección 10: FAQ

"¿A quién contacto si tengo un problema técnico con mi laptop?"

Llama a query_company_knowledge con "soporte técnico laptop".

Debe indicar el contacto al canal de Slack #it-soporte y mencionar el SLA de respuesta de 4 horas hábiles.

P-08

Sección 10: FAQ

"¿Puedo trabajar desde el exterior del país y por cuánto tiempo?"

Llama a query_company_knowledge con "trabajar desde el exterior".

Debe confirmar la autorización de trabajar desde el exterior por un máximo de 90 días corridos al año, requiriendo usar VPN.

P-09

Sección 3: Inducción

"Hoy es mi primer día como Junior Dev. Necesito programar mis tareas, ¿qué tengo asignado hoy?"

Llama a query_company_knowledge con "plan de onboarding junior semana 1 día 1". Revisa disponibilidad de calendario.

Debe recuperar la "Semana 1 - Día 1" del manual (Curso de Git de 2 horas en Moodle y Configuración del entorno de desarrollo local).

P-10

Sección 3: Colisión

(Forzar colisión el 30 de junio de 2026 de 10:00 a 12:00). "Agendame el Curso de Git de 2 horas para el 30 de junio a las 10:00 am."

Invocación de get_calendar_events. Al ver conflicto, invoca find_available_slots.

Detecta la superposición de horarios, rechaza insertar a las 10:00 y le propone al usuario las alternativas libres reales (ej: a partir de las 10:30 hs).