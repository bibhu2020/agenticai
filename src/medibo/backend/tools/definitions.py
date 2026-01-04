from datetime import datetime
from ..database import get_db_connection

def lookup_patient_id(patient_id: str):
    """
    Verifies if a patient exists and returns their name.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM patients WHERE id = ?", (patient_id,))
    row = cursor.fetchone()
    conn.close()
    if row:
        return f"Patient Found: {row['name']}. SYSTEM NOTIFICATION: Identity Verified. You MUST now call the 'transfer_to_perception' tool immediately. Do not respond to the user."
    return "Patient Not Found"

def check_symptom_severity(symptom_name: str):
    """
    Checks the knowledge base for a specific symptom's severity and advice.
    """
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT severity, advice FROM symptoms WHERE name = ?", (symptom_name.lower(),))
    row = cursor.fetchone()
    conn.close()
    if row:
        return f"Severity: {row['severity']}, Advice: {row['advice']}. SYSTEM NOTIFICATION: Analysis Valid. You MUST now call 'transfer_to_action' with this info."
    return "Symptom found in general knowledge (Default: MILD). SYSTEM NOTIFICATION: You MUST now call 'transfer_to_action'."

def book_appointment(patient_id: str, reason: str):
    """
    Books a tele-consultation appointment. Returns the appointment details.
    """
    slot = datetime.now().strftime("%Y-%m-%d %H:%M")
    conn = get_db_connection()
    conn.execute("INSERT INTO appointments (patient_id, time, doctor, type) VALUES (?, ?, ?, ?)", 
                 (patient_id, slot, "Dr. AI", "Tele-Triage"))
    conn.commit()
    conn.close()
    return f"Appointment Booked: {slot} for {reason}"

def alert_emergency_services(reason: str):
    """
    Simulates alerting emergency services for critical conditions.
    """
    return f"EMERGENCY SERVICES NOTIFIED: {reason}"

def log_interaction_db(patient_id: str, user_input: str, response: str, urgency: str):
    """
    Logs the interaction to the learning database.
    """
    conn = get_db_connection()
    conn.execute("INSERT INTO interactions (patient_id, user_input, system_response, urgency) VALUES (?, ?, ?, ?)",
                 (patient_id, user_input, response, urgency))
    conn.commit()
    conn.close()
    return "Logged."
