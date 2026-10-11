# -*- coding: utf-8 -*-

from wsgiref.simple_server import make_server

from spyne import (
    Application,
    ServiceBase,
    rpc,
    Integer,
    Unicode,
    Decimal,
    Array,
    ComplexModel,
)

from spyne.protocol.soap import Soap11
from spyne.server.wsgi import WsgiApplication

from base_de_datos.conexion_bd import get_db_connection


# ============================================================
# MODELO SOAP: Route
# ============================================================

class Route(ComplexModel):
    id = Integer
    code = Unicode
    company = Unicode
    origin = Unicode
    destination = Unicode
    fare = Decimal
    schedule = Unicode
    status = Unicode


# ============================================================
# SERVICIO SOAP DE RUTAS
# ============================================================

class RoutesService(ServiceBase):

    # ========================================================
    # 1. OBTENER TODAS LAS RUTAS
    # ========================================================

    @rpc(
        _returns=Array(Route)
    )
    def get_all_routes(ctx):

        conexion = None
        cursor = None

        try:
            conexion = get_db_connection()
            cursor = conexion.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    code,
                    company,
                    origin,
                    destination,
                    fare,
                    schedule,
                    status
                FROM routes
                ORDER BY id ASC
                """
            )

            resultados = cursor.fetchall()

            rutas = []

            for fila in resultados:

                ruta = Route(
                    id=fila["id"],
                    code=fila["code"],
                    company=fila["company"],
                    origin=fila["origin"],
                    destination=fila["destination"],
                    fare=fila["fare"],
                    schedule=fila["schedule"],
                    status=fila["status"]
                )

                rutas.append(ruta)

            return rutas

        finally:
            if cursor:
                cursor.close()

            if conexion:
                conexion.close()


    # ========================================================
    # 2. OBTENER UNA RUTA POR ID
    # ========================================================

    @rpc(
        Integer,
        _returns=Route
    )
    def get_route_by_id(ctx, route_id):

        conexion = None
        cursor = None

        try:
            conexion = get_db_connection()
            cursor = conexion.cursor()

            cursor.execute(
                """
                SELECT
                    id,
                    code,
                    company,
                    origin,
                    destination,
                    fare,
                    schedule,
                    status
                FROM routes
                WHERE id = %s
                """,
                (route_id,)
            )

            fila = cursor.fetchone()

            if not fila:
                raise Exception(
                    f"La ruta {route_id} no existe."
                )

            return Route(
                id=fila["id"],
                code=fila["code"],
                company=fila["company"],
                origin=fila["origin"],
                destination=fila["destination"],
                fare=fila["fare"],
                schedule=fila["schedule"],
                status=fila["status"]
            )

        finally:
            if cursor:
                cursor.close()

            if conexion:
                conexion.close()


    # ========================================================
    # 3. CREAR UNA RUTA
    # ========================================================

    @rpc(
        Unicode,
        Unicode,
        Unicode,
        Unicode,
        Decimal,
        Unicode,
        Unicode,
        _returns=Route
    )
    def create_route(
        ctx,
        code,
        company,
        origin,
        destination,
        fare,
        schedule,
        status
    ):

        conexion = None
        cursor = None

        try:
            conexion = get_db_connection()
            cursor = conexion.cursor()

            # Verificar que el código no esté repetido
            cursor.execute(
                """
                SELECT id
                FROM routes
                WHERE code = %s
                """,
                (code,)
            )

            ruta_existente = cursor.fetchone()

            if ruta_existente:
                raise Exception(
                    f"Ya existe una ruta con el código {code}."
                )

            # Insertar la nueva ruta
            cursor.execute(
                """
                INSERT INTO routes (
                    code,
                    company,
                    origin,
                    destination,
                    fare,
                    schedule,
                    status
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    code,
                    company,
                    origin,
                    destination,
                    fare,
                    schedule,
                    status
                )
            )

            conexion.commit()

            route_id = cursor.lastrowid

            # Recuperar la ruta recién creada
            cursor.execute(
                """
                SELECT
                    id,
                    code,
                    company,
                    origin,
                    destination,
                    fare,
                    schedule,
                    status
                FROM routes
                WHERE id = %s
                """,
                (route_id,)
            )

            fila = cursor.fetchone()

            if not fila:
                raise Exception(
                    "No fue posible recuperar la ruta creada."
                )

            return Route(
                id=fila["id"],
                code=fila["code"],
                company=fila["company"],
                origin=fila["origin"],
                destination=fila["destination"],
                fare=fila["fare"],
                schedule=fila["schedule"],
                status=fila["status"]
            )

        except Exception:
            if conexion:
                conexion.rollback()

            raise

        finally:
            if cursor:
                cursor.close()

            if conexion:
                conexion.close()


    # ========================================================
    # 4. ACTUALIZAR UNA RUTA
    # ========================================================

    @rpc(
        Integer,
        Unicode,
        Unicode,
        Unicode,
        Unicode,
        Decimal,
        Unicode,
        Unicode,
        _returns=Route
    )
    def update_route(
        ctx,
        route_id,
        code,
        company,
        origin,
        destination,
        fare,
        schedule,
        status
    ):

        conexion = None
        cursor = None

        try:
            conexion = get_db_connection()
            cursor = conexion.cursor()

            # Verificar que la ruta exista
            cursor.execute(
                """
                SELECT id
                FROM routes
                WHERE id = %s
                """,
                (route_id,)
            )

            ruta = cursor.fetchone()

            if not ruta:
                raise Exception(
                    f"La ruta {route_id} no existe."
                )

            # Verificar que el código no pertenezca a otra ruta
            cursor.execute(
                """
                SELECT id
                FROM routes
                WHERE code = %s
                  AND id <> %s
                """,
                (code, route_id)
            )

            codigo_existente = cursor.fetchone()

            if codigo_existente:
                raise Exception(
                    f"El código {code} ya pertenece a otra ruta."
                )

            # Actualizar la ruta
            cursor.execute(
                """
                UPDATE routes
                SET
                    code = %s,
                    company = %s,
                    origin = %s,
                    destination = %s,
                    fare = %s,
                    schedule = %s,
                    status = %s
                WHERE id = %s
                """,
                (
                    code,
                    company,
                    origin,
                    destination,
                    fare,
                    schedule,
                    status,
                    route_id
                )
            )

            conexion.commit()

            # Recuperar la ruta actualizada
            cursor.execute(
                """
                SELECT
                    id,
                    code,
                    company,
                    origin,
                    destination,
                    fare,
                    schedule,
                    status
                FROM routes
                WHERE id = %s
                """,
                (route_id,)
            )

            fila = cursor.fetchone()

            return Route(
                id=fila["id"],
                code=fila["code"],
                company=fila["company"],
                origin=fila["origin"],
                destination=fila["destination"],
                fare=fila["fare"],
                schedule=fila["schedule"],
                status=fila["status"]
            )

        except Exception:
            if conexion:
                conexion.rollback()

            raise

        finally:
            if cursor:
                cursor.close()

            if conexion:
                conexion.close()


    # ========================================================
    # 5. ELIMINAR UNA RUTA
    # ========================================================

    @rpc(
        Integer,
        _returns=Unicode
    )
    def delete_route(ctx, route_id):

        conexion = None
        cursor = None

        try:
            conexion = get_db_connection()
            cursor = conexion.cursor()

            # Verificar que la ruta exista
            cursor.execute(
                """
                SELECT id
                FROM routes
                WHERE id = %s
                """,
                (route_id,)
            )

            ruta = cursor.fetchone()

            if not ruta:
                raise Exception(
                    f"La ruta {route_id} no existe."
                )

            # Eliminar la ruta
            #
            # Las tablas stops, dispatches e incidents
            # tienen ON DELETE CASCADE, por lo que sus
            # registros relacionados también serán eliminados.
            cursor.execute(
                """
                DELETE FROM routes
                WHERE id = %s
                """,
                (route_id,)
            )

            conexion.commit()

            return f"La ruta {route_id} fue eliminada correctamente."

        except Exception:
            if conexion:
                conexion.rollback()

            raise

        finally:
            if cursor:
                cursor.close()

            if conexion:
                conexion.close()


# ============================================================
# CONFIGURACIÓN DE LA APLICACIÓN SOAP
# ============================================================

application = Application(
    [RoutesService],
    tns="http://rutas.popayan/routes",
    in_protocol=Soap11(validator="lxml"),
    out_protocol=Soap11()
)


# ============================================================
# CONFIGURACIÓN WSGI
# ============================================================

wsgi_application = WsgiApplication(application)


# ============================================================
# INICIAR SERVIDOR
# ============================================================

if __name__ == "__main__":

    host = "127.0.0.1"
    port = 8001

    print("=" * 60)
    print("MICROSERVICIO DE RUTAS")
    print("=" * 60)
    print(f"Servidor SOAP iniciado en http://{host}:{port}")
    print(f"WSDL disponible en http://{host}:{port}/?wsdl")
    print("=" * 60)

    servidor = make_server(
        host,
        port,
        wsgi_application
    )

    servidor.serve_forever()
