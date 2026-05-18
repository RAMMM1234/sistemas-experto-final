PASOS PARA CORRER EL SISTEMA EXPERTO

1) Abre Visual Studio Code en la carpeta sistemas_experto.

2) Abre la terminal y ejecuta:

   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   pip install -r requirements.txt

   Si PowerShell bloquea la activación, ejecuta primero:
   Set-ExecutionPolicy RemoteSigned -Scope CurrentUser

3) Asegúrate de tener creada la base de datos en PostgreSQL:

   sistema_experto

4) En pgAdmin, abre Query Tool dentro de esa base de datos y ejecuta:

   BasedeDatos.sql

5) Corre la aplicación con:

   python app.py

6) Abre en el navegador:

   http://127.0.0.1:8000/

IMPORTANTE:
No corras este proyecto con php -S localhost:8000, porque no es PHP.
Este proyecto se corre con Python + Flask.
