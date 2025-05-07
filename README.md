# Aplicación CRUD con Docker, Python y Azure SQL

Este proyecto implementa una aplicación CRUD (Crear, Leer, Actualizar, Eliminar) utilizando:

- **Backend**: Python con Flask
- **Frontend**: HTML, jQuery, Bootstrap y DataTables
- **Base de datos**: Azure SQL Database
- **Contenedorización**: Docker

## Estructura del proyecto

```
proyecto/
├── app.py                # Servidor Flask
├── Dockerfile            # Configuración de Docker
├── docker-compose.yml    # Composición de Docker
├── requirements.txt      # Dependencias de Python
├── .env                  # Variables de entorno (credenciales)
├── create_table.sql      # Script para crear la tabla en Azure SQL
└── static/               # Archivos HTML
    └── index.html        # Interfaz de usuario
└── static/               # Archivos estáticos para el frontend
│   ├── css/              # Subcarpeta para archivos CSS
│   │   └── main.css      # Estilos del proyecto
│   └── js/               # Subcarpeta para archivos JavaScript
    └── main.js           # Logica del frontend
```

## Configuración

### 1. Base de datos Azure SQL

1. Crea una base de datos en Azure SQL Database
2. Configura las reglas de firewall para permitir conexiones
3. Ejecuta el script `create_table.sql` para crear la tabla necesaria

### 2. Variables de entorno

Crea un archivo `.env` con las siguientes variables:

```
DB_SERVER=tu-servidor.database.windows.net
DB_NAME=nombre-de-tu-db
DB_USER=tu-usuario
DB_PASSWORD=tu-contraseña
```

### 3. Preparación del frontend

Crea una carpeta `static` en la raíz del proyecto y coloca el archivo `index.html` dentro.

## Ejecución con Docker

1. Construye y ejecuta el contenedor:

```bash
docker-compose up --build
```

2. Accede a la aplicación en tu navegador:

```
http://localhost:5000
```

## API REST

La aplicación expone los siguientes endpoints:

- `GET /api/items`: Obtener todos los items
- `GET /api/items/{id}`: Obtener un item específico
- `POST /api/items`: Crear un nuevo item
- `PUT /api/items/{id}`: Actualizar un item existente
- `DELETE /api/items/{id}`: Eliminar un item

## Interfaz de usuario

La interfaz de usuario proporciona:

- Tabla interactiva con DataTables (búsqueda, paginación, ordenamiento)
- Formularios para crear y editar items
- Confirmación para eliminar items
- Indicadores visuales durante las operaciones

## Solución de problemas

### Problemas de conexión con Azure SQL

Si encuentras problemas de conexión:

1. Verifica las credenciales en `.env`
2. Asegúrate de que la IP de tu servidor Docker esté permitida en las reglas de firewall de Azure
3. Prueba cambiando la versión del driver ODBC en `app.py`

### Problemas con Docker

Si hay problemas con Docker:

1. Asegúrate de que Docker está instalado y en ejecución
2. Verifica que el puerto 5000 no esté siendo utilizado por otra aplicación
3. Revisa los logs de Docker:

```bash
docker-compose logs
```

## Licencia

Este proyecto está disponible bajo la licencia MIT.
