
import sqlite3
import os

DB_PATH = "medibo.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    c = conn.cursor()
    
    # Patients Table
    c.execute('''CREATE TABLE IF NOT EXISTS patients
                 (id TEXT PRIMARY KEY, name TEXT, age INTEGER, history TEXT)''')
    
    # Appointments Table
    c.execute('''CREATE TABLE IF NOT EXISTS appointments
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id TEXT, time TEXT, doctor TEXT, type TEXT)''')
    
    # Interactions Table (Learning Module)
    c.execute('''CREATE TABLE IF NOT EXISTS interactions
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, patient_id TEXT, user_input TEXT, system_response TEXT, urgency TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')

    # Knowledge Graph (Simplified as Symptoms Table)
    c.execute('''CREATE TABLE IF NOT EXISTS symptoms
                 (name TEXT PRIMARY KEY, severity TEXT, advice TEXT)''')

    # Seed Data
    # Patients
    c.execute("INSERT OR IGNORE INTO patients (id, name, age, history) VALUES ('P001', 'John Doe', 45, 'Hypertension')")
    c.execute("INSERT OR IGNORE INTO patients (id, name, age, history) VALUES ('P002', 'Jane Smith', 30, 'Asthma')")
    
    # Symptoms
    symptoms = [
        ('chest pain', 'CRITICAL', 'Call 911 immediately. Possible cardiac event.'),
        ('shortness of breath', 'CRITICAL', 'Seek emergency care immediately.'),
        ('tightness in chest', 'CRITICAL', 'Possible heart attack. Call emergency services.'),
        ('fever', 'MODERATE', 'Monitor temperature. If above 39C, consult doctor.'),
        ('headache', 'MILD', 'Rest and hydration. Take OTC painkiller if needed.'),
        ('cough', 'MILD', 'Warm fluids and rest.')
    ]
    for sym, sev, adv in symptoms:
        c.execute("INSERT OR IGNORE INTO symptoms (name, severity, advice) VALUES (?, ?, ?)", (sym, sev, adv))

    conn.commit()
    conn.close()
    print("Database initialized and populated.")

if __name__ == "__main__":
    init_db()
