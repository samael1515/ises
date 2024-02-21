import sqlite3

# Conectar a la base de datos (si no existe, se creará)
conn = sqlite3.connect('tokens.db')

# Crear un cursor para ejecutar comandos SQL
cursor = conn.cursor()

# Crear la tabla 'tokens' si no existe
cursor.execute('''CREATE TABLE IF NOT EXISTS tokens (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT NOT NULL,
                    token TEXT NOT NULL
                )''')

# Guardar los cambios y cerrar la conexión con la base de datos
conn.commit()
conn.close()

print("Base de datos tokens.db creada exitosamente.")
