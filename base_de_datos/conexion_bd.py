# -*- coding: utf-8 -*-
"""
==============================================================================
MÓDULO: CONEXIÓN A BASE DE DATOS (MySQL)
==============================================================================

DESCRIPCIÓN:
    Este archivo debe gestionar la conexión centralizada a la base de datos
    MySQL del sistema de transporte público (movi_popayan_db).

INSTRUCCIONES DE IMPLEMENTACIÓN:
    1. Importar la librería necesaria para conectarse a MySQL (ejemplo: 'pymysql').
    2. Configurar los parámetros de conexión (Host, Usuario, Contraseña, Base de Datos, Puerto).
       - Se recomienda permitir lectura desde variables de entorno con valores por defecto.
    3. Implementar la función 'get_db_connection()':
       - Debe abrir y retornar una conexión activa con cursor tipo diccionario (DictCursor)
         para que las filas se lean como diccionarios {'columna': valor}.
       - Configurar el juego de caracteres a 'utf8mb4'.
==============================================================================
"""

import os
# TODO: Importar la librería de MySQL (ejemplo: import pymysql)

# TODO: Definir el diccionario con los parámetros de conexión
# Parámetros esperados:
#   - host: Dirección del servidor MySQL (por defecto: 'localhost')
#   - user: Usuario de la base de datos (por defecto: 'root')
#   - password: Clave de acceso a MySQL
#   - db: Nombre de la base de datos ('movi_popayan_db')
#   - port: Puerto de escucha (por defecto: 3306)
DB_CONFIG = {
    # TODO: Completar la configuración de conexión
}


def get_db_connection():
    """
    TODO: Implementar la función que establece y retorna la conexión activa a MySQL.
    
    Retorna:
        Objeto de conexión a la base de datos listo para ejecutar consultas.
    """
    # TODO: Retornar pymysql.connect(**DB_CONFIG)
    pass
