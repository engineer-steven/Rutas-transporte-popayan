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
import pymysql
from pymysql.cursors import DictCursor

# Configuración de los parámetros de conexión con variables de entorno y valores por defecto
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'Admin#123456'),
    'database': os.getenv('DB_NAME', 'movi_popayan_db'),
    'port': int(os.getenv('DB_PORT', 3306)),
    'charset': 'utf8mb4',
    'cursorclass': DictCursor
}


def get_db_connection():
    """
    Implementa la función que establece y retorna la conexión activa a MySQL.
    
    Retorna:
        Objeto de conexión a la base de datos listo para ejecutar consultas.
    """
    connection = pymysql.connect(**DB_CONFIG)
    return connection