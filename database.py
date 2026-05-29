import sqlite3

def crear_base_datos():
    # Conexión al archivo local de la BD
    conn = sqlite3.connect('inventario3d.db')
    cursor = conn.cursor()
    
    # Crear tabla de inventario
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto TEXT NOT NULL,
            tipo TEXT NOT NULL, -- Filamento, Plancha, Boquilla, etc.
            stock INTEGER NOT NULL,
            precio REAL NOT NULL
        )
    ''')
    
    # Insertar datos de prueba si la tabla está vacía
    cursor.execute("SELECT COUNT(*) FROM inventario")
    if cursor.fetchone()[0] == 0:
        productos_inicio = [
            ('Filamento PLA+ Negro 1kg', 'Filamento', 5, 450.00),
            ('Filamento PETG Gris 1kg', 'Filamento', 2, 480.00),
            ('Plancha de PEI Texturizado', 'Plancha', 3, 600.00),
            ('Boquilla de Latón 0.4mm', 'Refacción', 15, 50.00),
            ('Filamento High-Speed Blanco 1kg', 'Filamento', 0, 550.00) # Sin stock para probar regla
        ]
        cursor.executemany("INSERT INTO inventario (producto, tipo, stock, precio) VALUES (?, ?, ?, ?)", productos_inicio)
        conn.commit()
        print("¡Base de datos inicializada con productos de impresión 3D!")
    
    conn.close()

if __name__ == "__main__":
    crear_base_datos()