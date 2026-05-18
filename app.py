from flask import Flask, render_template, request, jsonify
from logica import diagnosticar
import os
from dotenv import load_dotenv

# Carga las variables del archivo .env
load_dotenv()

# Compatible con psycopg2 y psycopg v3.
try:
    import psycopg2
except ImportError:
    try:
        import psycopg as psycopg2
    except ImportError:
        psycopg2 = None

app = Flask(__name__)


# ------------------------------------------------------------
# CONEXIÓN A POSTGRESQL / SUPABASE
# ------------------------------------------------------------
def conectar_db():
    if psycopg2 is None:
        raise RuntimeError(
            "No está instalado el conector de PostgreSQL. Instala uno con: "
            "pip install psycopg2-binary  o  pip install psycopg[binary]"
        )

    # Primero intenta conectar con Supabase usando el archivo .env
    database_url = os.getenv("SUPABASE_DATABASE_URL")

    if database_url:
        # Limpia comillas por si quedaron pegadas
        database_url = database_url.strip().strip('"').strip("'")

        # Si copiaste la URL desde Prisma y trae pgbouncer=true, lo quitamos
        # porque psycopg2 puede marcar error con ese parámetro.
        if "pgbouncer=true" in database_url:
            database_url = database_url.replace("pgbouncer=true", "")
            database_url = database_url.replace("?&", "?").replace("&&", "&")
            database_url = database_url.rstrip("?&")

        # Supabase requiere SSL
        if "sslmode=" not in database_url.lower():
            separador = "&" if "?" in database_url else "?"
            database_url = f"{database_url}{separador}sslmode=require"

        return psycopg2.connect(database_url)

    # Si no encuentra SUPABASE_DATABASE_URL, usa PostgreSQL local
    return psycopg2.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5432"),
        dbname=os.getenv("DB_NAME", "sistema_experto"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )


def asegurar_tablas(conexion):
    """Crea o actualiza las tablas necesarias sin borrar datos existentes."""
    cursor = conexion.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS enfermedades (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            descripcion TEXT
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS sintomas (
            id SERIAL PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            enfermedad_id INT REFERENCES enfermedades(id) ON DELETE SET NULL
        );
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS evaluaciones (
            id SERIAL PRIMARY KEY,
            resultado TEXT NOT NULL,
            sintomas TEXT,
            puntos INTEGER DEFAULT 0,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
    )

    cursor.execute("ALTER TABLE evaluaciones ADD COLUMN IF NOT EXISTS sintomas TEXT;")
    cursor.execute("ALTER TABLE evaluaciones ADD COLUMN IF NOT EXISTS puntos INTEGER DEFAULT 0;")
    cursor.execute("ALTER TABLE evaluaciones ADD COLUMN IF NOT EXISTS fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP;")

    conexion.commit()
    cursor.close()


def texto_sintomas(datos):
    nombres = {
        "sed": "Mucha sed",
        "orina": "Orina frecuente",
        "cansancio": "Cansancio",
        "vision_borrosa": "Visión borrosa",
        "perdida_peso": "Pérdida de peso",
        "antecedentes": "Antecedentes familiares",
    }

    seleccionados = [
        nombres.get(k, k.replace("_", " "))
        for k, v in datos.items()
        if v == "si"
    ]

    return ", ".join(seleccionados) if seleccionados else "Ninguno"


def guardar_evaluacion(resultado_obj, sintomas_texto):
    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        asegurar_tablas(conexion)

        cursor = conexion.cursor()
        cursor.execute(
            """
            INSERT INTO evaluaciones (resultado, sintomas, puntos)
            VALUES (%s, %s, %s)
            """,
            (
                resultado_obj["nivel"],
                sintomas_texto,
                resultado_obj.get("puntos", 0),
            ),
        )

        conexion.commit()
        return True, None

    except Exception as error:
        print(f"Error al guardar en PostgreSQL/Supabase: {error}")
        return False, str(error)

    finally:
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()


# ------------------------------------------------------------
# RUTAS DE LA APLICACIÓN
# ------------------------------------------------------------
@app.route("/")
@app.route("/login")
def inicio():
    return render_template("login.html")


@app.route("/evaluacion")
@app.route("/index")
@app.route("/index.html")
def cuestionario():
    return render_template("index.html")


@app.route("/diagnostico", methods=["POST"])
def evaluar():
    datos = request.get_json(silent=True) or {}

    resultado_obj = diagnosticar(datos)
    sintomas_texto = texto_sintomas(datos)

    guardado, error_db = guardar_evaluacion(resultado_obj, sintomas_texto)

    resultado_obj["guardado"] = guardado

    if not guardado:
        resultado_obj["mensaje_db"] = "El diagnóstico se generó, pero no se pudo guardar en la base de datos."
        resultado_obj["detalle_db"] = error_db

    return jsonify(resultado_obj)


@app.route("/historial")
def historial():
    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        asegurar_tablas(conexion)

        cursor = conexion.cursor()
        cursor.execute(
            """
            SELECT resultado, sintomas, puntos, fecha
            FROM evaluaciones
            ORDER BY fecha DESC
            """
        )

        datos = []

        for resultado, sintomas, puntos, fecha in cursor.fetchall():
            datos.append(
                {
                    "resultado": resultado,
                    "sintomas": sintomas or "Ninguno",
                    "puntos": puntos or 0,
                    "fecha": fecha.isoformat(sep=" ", timespec="seconds")
                    if hasattr(fecha, "isoformat")
                    else str(fecha),
                }
            )

        return jsonify(datos)

    except Exception as error:
        print(f"Error al consultar historial: {error}")
        return jsonify({"error": "No se pudo cargar el historial de evaluaciones."}), 500

    finally:
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()


@app.route("/probar-db")
def probar_db():
    conexion = None
    cursor = None

    try:
        conexion = conectar_db()
        asegurar_tablas(conexion)

        cursor = conexion.cursor()
        cursor.execute("SELECT NOW();")
        fecha = cursor.fetchone()[0]

        return jsonify(
            {
                "conexion": "correcta",
                "base_de_datos": "Supabase/PostgreSQL",
                "fecha_servidor": str(fecha),
            }
        )

    except Exception as error:
        return jsonify(
            {
                "conexion": "fallida",
                "error": str(error),
            }
        ), 500

    finally:
        if cursor is not None:
            cursor.close()
        if conexion is not None:
            conexion.close()


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=8000, debug=True)