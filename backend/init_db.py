import sqlite3
import csv

def inicializar_base_de_datos():
    conexion = sqlite3.connect("inventario3d.db")
    cursor = conexion.cursor()

    # 1. Crear Tabla Impresoras
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS impresoras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modelo TEXT NOT NULL,
            marca TEXT NOT NULL,
            volumen_impresion TEXT,
            precio REAL,
            stock INTEGER
        )
    ''')

    # 2. Crear Tabla Filamentos (¡Actualizada a tu nuevo CSV!)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS filamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT NOT NULL,
            material TEXT NOT NULL,
            color TEXT NOT NULL,
            stock INTEGER,
            precio REAL,
            url_imagen TEXT
        )
    ''')

    # 3. Crear Tabla Accesorios
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accesorios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            compatibilidad TEXT,
            precio REAL,
            stock INTEGER
        )
    ''')

    # Limpiamos datos viejos
    cursor.execute("DELETE FROM impresoras")
    cursor.execute("DELETE FROM filamentos")
    cursor.execute("DELETE FROM accesorios")

    # --- INYECTAR DATOS MANUALES ---
    cursor.execute('''
        INSERT INTO impresoras (modelo, marca, volumen_impresion, precio, stock) 
        VALUES ('U1', 'Snapmaker', '400x400x400 mm', 1599.00, 2)
    ''')

    cursor.execute('''
        INSERT INTO accesorios (nombre, compatibilidad, precio, stock) 
        VALUES ('Hotend Dual', 'Snapmaker U1', 120.00, 4)
    ''')

    # --- LECTURA DE TU NUEVO CSV ---
    try:
        with open('filamentos.csv', mode='r', encoding='utf-8') as archivo_csv:
            lector = csv.DictReader(archivo_csv)
            contador = 0
            
            for fila in lector:
                # Inyectamos los datos exactamente con los nombres de tus 6 columnas
                cursor.execute('''
                    INSERT INTO filamentos (marca, material, color, stock, precio, url_imagen)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    fila['marca'],
                    fila['material'],
                    fila['color'],
                    fila['stock'],
                    fila['precio'],
                    fila['url_imagen']
                ))
                contador += 1
                
        print(f"✅ ¡Se inyectaron {contador} filamentos desde el CSV con éxito!")
        
    except FileNotFoundError:
        print("⚠️ ERROR: No se encontró el archivo 'filamentos.csv'.")
    except KeyError as e:
        print(f"⚠️ ERROR DE COLUMNA: Tu CSV no tiene la columna {e}. Revisa los encabezados.")

    conexion.commit()
    conexion.close()
    print("¡Base de datos lista!")

if __name__ == "__main__":
    inicializar_base_de_datos()