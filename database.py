import sqlite3
import csv
import os

def crear_base_datos():
    conn = sqlite3.connect('inventario3d.db')
    cursor = conn.cursor()
    cursor.execute("DROP TABLE IF EXISTS inventario")
    # 1. Crear la tabla con la estructura final de 8 columnas
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS inventario (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            producto_base TEXT NOT NULL,
            tipo TEXT NOT NULL,
            marca TEXT NOT NULL,
            material TEXT NOT NULL,
            color TEXT NOT NULL,
            stock INTEGER NOT NULL,
            precio REAL NOT NULL,
            url_imagen TEXT
        )
    ''')
    
    archivo_csv = 'inventario.csv'
    
    if os.path.exists(archivo_csv):
        # Limpiamos para evitar duplicados al recargar el CSV
        cursor.execute("DELETE FROM inventario")
        
        with open(archivo_csv, mode='r', encoding='utf-8') as f:
            lector = csv.DictReader(f)
            
            productos_inicio = []
            for fila in lector:
                productos_inicio.append((
                    fila['producto_base'],
                    fila['tipo'],
                    fila['marca'],
                    fila['material'],
                    fila['color'],
                    int(fila['stock']),
                    float(fila['precio']),
                    fila['url_imagen']
                ))
            
            # Insertar las 8 columnas mapeadas
            cursor.executemany(
                """INSERT INTO inventario 
                (producto_base, tipo, marca, material, color, stock, precio, url_imagen) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)""", 
                productos_inicio
            )
            conn.commit()
            print(f"¡Base de datos armada con éxito desde '{archivo_csv}'!")
    else:
        print(f"⚠️ Archivo '{archivo_csv}' no encontrado en la carpeta.")
        
    conn.close()

if __name__ == "__main__":
    crear_base_datos()