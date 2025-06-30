import sqlite3

conn = sqlite3.connect("obras.db")
cursor = conn.cursor()

cursor.execute("DROP TABLE IF EXISTS obras")

cursor.execute('''
    CREATE TABLE obras (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario TEXT,
        nombre_obra TEXT UNIQUE,
        ladrillo_1 INTEGER,
        ladrillo_2 INTEGER,
        ladrillo_3 INTEGER,
        ladrillo_4 INTEGER,
        ladrillo_5 INTEGER,
        ladrillo_6 INTEGER,
        cal REAL,
        cemento REAL,
        cemento_alba REAL,
        arena REAL
    )
''')

conn.commit()
conn.close()
print("✅ Tabla 'obras' recreada correctamente con columna 'usuario'")

