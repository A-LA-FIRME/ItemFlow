from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
import os
import pyodbc
from dotenv import load_dotenv
from datetime import datetime
import humanize
import locale

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__, static_folder='static')
CORS(app)

# Configuración de la base de datos Azure SQL
def get_db_connection():
    server = os.getenv("DB_SERVER")
    database = os.getenv("DB_NAME")
    username = os.getenv("DB_USER")
    password = os.getenv("DB_PASSWORD")
    driver = '{ODBC Driver 18 for SQL Server}'

    connection_string = (
        f'DRIVER={driver};'
        f'SERVER={server};'
        f'DATABASE={database};'
        f'UID={username};'
        f'PWD={password};'
        'Encrypt=yes;'
        'TrustServerCertificate=no;'
        'Connection Timeout=30;'
    )

    try:
        return pyodbc.connect(connection_string)
    except pyodbc.Error as e:
        app.logger.error(f"Error de conexión a la BD: {str(e)}")
        return None

# Configuración de localización para humanize
def setup_localization():
    try:
        # Intentar configurar la localización en español
        locale.setlocale(locale.LC_ALL, 'es_ES.UTF-8')
    except locale.Error:
        try:
            # Alternativa si la localización específica no está disponible
            locale.setlocale(locale.LC_ALL, 'es_ES')
        except locale.Error:
            try:
                # Otra alternativa
                locale.setlocale(locale.LC_ALL, 'es')
            except locale.Error:
                # Si todo falla, usar la localización por defecto
                pass

    # Configurar humanize para español
    humanize.i18n.activate('es')

# Llamar a la función de configuración al inicio
setup_localization()

# Función para formatear la fecha en formato relativo
def format_relative_time(created_at):
    if not created_at:
        return ""

    now = datetime.now()
    diff = now - created_at

    seconds = diff.total_seconds()

    # Implementar manualmente el formato en español para garantizar consistencia
    if seconds < 60:
        return "Hace unos segundos"
    elif seconds < 3600:
        minutes = int(seconds // 60)
        return f"Hace {minutes} {'minuto' if minutes == 1 else 'minutos'}"
    elif seconds < 86400:  # 24 horas
        hours = int(seconds // 3600)
        return f"Hace {hours} {'hora' if hours == 1 else 'horas'}"
    elif seconds < 2592000:  # 30 días
        days = int(seconds // 86400)
        return f"Hace {days} {'día' if days == 1 else 'días'}"
    elif seconds < 31536000:  # 1 año
        months = int(seconds // 2592000)
        return f"Hace {months} {'mes' if months == 1 else 'meses'}"
    else:
        years = int(seconds // 31536000)
        return f"Hace {years} {'año' if years == 1 else 'años'}"

# Servir archivos estáticos (HTML, CSS, JS)
@app.route('/')
def index():
    return render_template('index.html')

# Rutas para operaciones CRUD
@app.route('/api/items', methods=['GET'])
def get_items():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, price, created_at FROM items ORDER BY created_at DESC")

        # Verificar si hay resultados
        if cursor.description is None:
            return jsonify([])  # Retornar una lista vacía si no hay datos

        columns = [column[0] for column in cursor.description]
        items = []

        for row in cursor.fetchall():
            item = dict(zip(columns, row))
            # Formatear la fecha de creación
            if 'created_at' in item and item['created_at']:
                item['created_at_formatted'] = format_relative_time(item['created_at'])
            items.append(item)

        return jsonify(items)
    except Exception as e:
        app.logger.error(f"Error al obtener items: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/items/<int:id>', methods=['GET'])
def get_item(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, description, price, created_at FROM items WHERE id = ?", (id,))
        columns = [column[0] for column in cursor.description]
        row = cursor.fetchone()

        if row:
            item = dict(zip(columns, row))
            # Formatear la fecha de creación
            if 'created_at' in item and item['created_at']:
                item['created_at_formatted'] = format_relative_time(item['created_at'])
            return jsonify(item)
        else:
            return jsonify({"error": "Item no encontrado"}), 404
    except Exception as e:
        app.logger.error(f"Error al obtener item {id}: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/items', methods=['POST'])
def create_item():
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    data = request.json

    # Validar que el nombre y precio sean obligatorios
    if not data or 'name' not in data or not data['name'].strip():
        return jsonify({"error": "El nombre del item es obligatorio"}), 400

    if 'price' not in data or data['price'] is None:
        return jsonify({"error": "El precio del item es obligatorio"}), 400

    try:
        price = float(data['price'])
        if price <= 0:
            return jsonify({"error": "El precio debe ser mayor que cero"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "El precio debe ser un número válido"}), 400


    # Validar longitud máxima del nombre
    if len(data['name']) > 100:
        return jsonify({"error": "El nombre no puede exceder los 100 caracteres"}), 400

    # Validar que el precio sea un número
    try:
        data['price'] = float(data['price'])
    except ValueError:
        return jsonify({"error": "El precio debe ser un valor numérico"}), 400

    # Garantizar que description exista
    if 'description' not in data:
        data['description'] = ""

    try:
        cursor = conn.cursor()

        # Verificar si ya existe un item con ese nombre
        cursor.execute("SELECT id FROM items WHERE name = ?", (data['name'],))
        if cursor.fetchone():
            return jsonify({"error": "Ya existe un item con ese nombre"}), 409

        cursor.execute(
            "INSERT INTO items (name, description, price) VALUES (?, ?, ?)",
            (data['name'], data['description'], data['price'])
        )
        conn.commit()

        # Obtener el ID y la fecha de creación del nuevo item
        cursor.execute("SELECT id, created_at FROM items WHERE name = ?", (data['name'],))
        result = cursor.fetchone()
        new_id = result[0]
        created_at = result[1]

        # Formatear la fecha de creación
        created_at_formatted = format_relative_time(created_at)

        return jsonify({
            "id": new_id,
            "name": data['name'],
            "description": data['description'],
            "price": data['price'],
            "created_at": created_at.isoformat() if created_at else None,
            "created_at_formatted": created_at_formatted
        }), 201
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Error al crear item: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/items/<int:id>', methods=['PUT'])
def update_item(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    data = request.json
    if not data:
        return jsonify({"error": "Datos incompletos"}), 400

    # Validar que el nombre no exceda los 100 caracteres si está presente
    if 'name' in data and len(data['name']) > 100:
        return jsonify({"error": "El nombre no puede exceder los 100 caracteres"}), 400

    # Validar que el nombre no esté vacío si está presente
    if 'name' in data and not data['name'].strip():
        return jsonify({"error": "El nombre no puede estar vacío"}), 400

    # Validar precio si está presente
    if 'price' not in data or data['price'] is None:
        return jsonify({"error": "El precio del item es obligatorio"}), 400

    try:
        price = float(data['price'])
        if price <= 0:
            return jsonify({"error": "El precio debe ser mayor que cero"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "El precio debe ser un número válido"}), 400

    try:
        cursor = conn.cursor()

        # Verificar si el item existe
        cursor.execute("SELECT * FROM items WHERE id = ?", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Item no encontrado"}), 404

        # Si se está actualizando el nombre, verificar que sea único
        if 'name' in data:
            cursor.execute("SELECT id FROM items WHERE name = ? AND id != ?", (data['name'], id))
            if cursor.fetchone():
                return jsonify({"error": "Ya existe otro item con ese nombre"}), 409

        # Construir la consulta dinámicamente basada en los campos actualizados
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        values = list(data.values())
        values.append(id)

        cursor.execute(f"UPDATE items SET {set_clause} WHERE id = ?", values)
        conn.commit()

        # Obtener el item actualizado incluyendo la fecha de creación
        cursor.execute("SELECT id, name, description, price, created_at FROM items WHERE id = ?", (id,))
        columns = [column[0] for column in cursor.description]
        row = cursor.fetchone()
        updated_item = dict(zip(columns, row))

        # Formatear la fecha de creación
        if 'created_at' in updated_item and updated_item['created_at']:
            updated_item['created_at_formatted'] = format_relative_time(updated_item['created_at'])

        return jsonify(updated_item)
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Error al actualizar item {id}: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/items/<int:id>', methods=['DELETE'])
def delete_item(id):
    conn = get_db_connection()
    if not conn:
        return jsonify({"error": "No se pudo conectar a la base de datos"}), 500

    try:
        cursor = conn.cursor()

        # Verificar si el item existe
        cursor.execute("SELECT * FROM items WHERE id = ?", (id,))
        if not cursor.fetchone():
            return jsonify({"error": "Item no encontrado"}), 404

        cursor.execute("DELETE FROM items WHERE id = ?", (id,))
        conn.commit()

        return jsonify({"message": f"Item {id} eliminado correctamente"})
    except Exception as e:
        conn.rollback()
        app.logger.error(f"Error al eliminar item {id}: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

@app.route('/api/health', methods=['GET'])
def health_check():
    # Verificar la conectividad con la base de datos
    conn = get_db_connection()
    db_status = "Connected" if conn else "Disconnected"

    if conn:
        conn.close()

    return jsonify({
        "status": "OK",
        "database": db_status,
        "timestamp": datetime.now().isoformat()
    })

# Documentación de la API
@app.route('/api/docs')
def api_docs():
    return jsonify({
        "api_version": "1.0",
        "endpoints": [
            {
                "path": "/api/items",
                "methods": ["GET", "POST"],
                "description": "Obtener todos los items o crear uno nuevo"
            },
            {
                "path": "/api/items/<id>",
                "methods": ["GET", "PUT", "DELETE"],
                "description": "Obtener, actualizar o eliminar un item específico"
            },
            {
                "path": "/api/health",
                "methods": ["GET"],
                "description": "Verificar el estado de la API"
            }
        ]
    })

if __name__ == '__main__':
    # Configurar la localización al iniciar
    setup_localization()
    app.run(host='0.0.0.0', port=5000, debug=True)