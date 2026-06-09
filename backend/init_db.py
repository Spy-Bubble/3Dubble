import sqlite3
import csv
import os

def inicializar_base_de_datos():
    ruta_db = os.path.join(os.path.dirname(__file__), "inventario3d.db")
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()

    # 1. Crear Tablas (Todas con url_imagen ahora)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS impresoras (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            modelo TEXT NOT NULL,
            marca TEXT NOT NULL,
            volumen_impresion TEXT,
            stock INTEGER,
            precio REAL,
            url_imagen TEXT
        )
    ''')

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

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS accesorios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            compatibilidad TEXT,
            stock INTEGER,
            precio REAL,
            url_imagen TEXT
        )
    ''')

    # Limpiamos datos viejos
    cursor.execute("DELETE FROM impresoras")
    cursor.execute("DELETE FROM filamentos")
    cursor.execute("DELETE FROM accesorios")

    # --- FUNCIÓN AUTOMÁTICA PARA LEER CUALQUIER CSV ---
    def inyectar_csv(nombre_archivo, tabla, columnas, query_insert):
        ruta_csv = os.path.join(os.path.dirname(__file__), nombre_archivo)
        try:
            with open(ruta_csv, mode='r', encoding='utf-8') as archivo_csv:
                lector = csv.DictReader(archivo_csv)
                contador = 0
                for fila in lector:
                    # Extraemos los valores basados en la lista de columnas que le pasemos
                    valores = tuple(fila[columna] for columna in columnas)
                    cursor.execute(query_insert, valores)
                    contador += 1
            print(f"✅ Se inyectaron {contador} {tabla} desde {nombre_archivo}.")
        except FileNotFoundError:
            print(f"⚠️ AVISO: No se encontró '{nombre_archivo}'. La tabla de {tabla} quedará vacía por ahora.")
        except KeyError as e:
            print(f"⚠️ ERROR EN {nombre_archivo}: Falta la columna {e}. Revisa tus encabezados.")

    # --- INYECCIÓN DE LOS 3 ARCHIVOS ---
    
    # 1. Filamentos
    inyectar_csv(
        'filamentos.csv', 'filamentos',
        ['marca', 'material', 'color', 'stock', 'precio', 'url_imagen'],
        "INSERT INTO filamentos (marca, material, color, stock, precio, url_imagen) VALUES (?, ?, ?, ?, ?, ?)"
    )

    # 2. Impresoras
    inyectar_csv(
        'impresoras.csv', 'impresoras',
        ['modelo', 'marca', 'volumen_impresion', 'stock', 'precio', 'url_imagen'],
        "INSERT INTO impresoras (modelo, marca, volumen_impresion, stock, precio, url_imagen) VALUES (?, ?, ?, ?, ?, ?)"
    )

    # 3. Accesorios
    inyectar_csv(
        'accesorios.csv', 'accesorios',
        ['nombre', 'compatibilidad', 'stock', 'precio', 'url_imagen'],
        "INSERT INTO accesorios (nombre, compatibilidad, stock, precio, url_imagen) VALUES (?, ?, ?, ?, ?)"
    )

    conexion.commit()
    conexion.close()
    print("¡Base de datos estructurada y poblada con éxito!")

if __name__ == "__main__":
    inicializar_base_de_datos()