# -*- coding: utf-8 -*-
"""
==============================================================================
MÓDULO: CONEXIÓN A BASE DE DATOS (MySQL)
==============================================================================
Gestiona la conexión centralizada a la base de datos MySQL (movi_popayan_db).
"""

import os
from contextlib import contextmanager
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import pymysql
import pymysql.cursors

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", "19971020"),
    "database": os.getenv("DB_NAME", "movi_popayan_db"),
    "port": int(os.getenv("DB_PORT", 3306)),
    "charset": "utf8mb4",
    "cursorclass": pymysql.cursors.DictCursor,
    "autocommit": False
}

def get_db_connection():
    """
    Establece y retorna una conexión activa a MySQL con DictCursor.
    """
    return pymysql.connect(**DB_CONFIG)

@contextmanager
def get_cursor(commit: bool = False):
    """
    Context manager seguro: abre conexión y cursor con DictCursor,
    realiza commit o rollback según corresponda y garantiza el cierre.
    """
    conn = get_db_connection()
    try:
        with conn.cursor() as cursor:
            yield cursor
            if commit:
                conn.commit()
    except Exception:
        if commit:
            conn.rollback()
        raise
    finally:
        conn.close()
