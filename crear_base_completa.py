import sqlite3

# Crear la base de datos
conn = sqlite3.connect("obras.db")
cursor = conn.cursor()

# Crear tabla de usuarios
cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE,
        username TEXT,
        password TEXT
    )
''')

# Crear tabla de obras con la columna 'usuario'
cursor.execute('''
    CREATE TABLE IF NOT EXISTS obras (
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

print("✅ Base de datos creada correctamente con tablas 'usuarios' y 'obras'")
