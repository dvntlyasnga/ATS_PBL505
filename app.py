"""Backend autentikasi Flask dengan SQLite."""

import os
import sqlite3

from flask import Flask, render_template, request
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.config["DATABASE"] = os.environ.get("DATABASE_PATH", "users.db")


def get_db_connection():
    """Membuka koneksi ke database aplikasi."""
    connection = sqlite3.connect(app.config["DATABASE"])
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    """Membuat tabel pengguna jika belum tersedia."""
    connection = get_db_connection()
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password_hash TEXT NOT NULL
        )
        """
    )

    # Akun awal hanya dibuat jika variabel lingkungan disediakan.
    username = os.environ.get("APP_ADMIN_USERNAME")
    password = os.environ.get("APP_ADMIN_PASSWORD")
    if username and password:
        connection.execute(
            """
            INSERT OR IGNORE INTO users (username, password_hash)
            VALUES (?, ?)
            """,
            (username, generate_password_hash(password)),
        )

    connection.commit()
    connection.close()


@app.route("/", methods=["GET", "POST"])
def index():
    """Menampilkan halaman login dan memproses autentikasi."""
    message = None
    status_class = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        connection = get_db_connection()
        user = connection.execute(
            "SELECT username, password_hash FROM users WHERE username = ?",
            (username,),
        ).fetchone()
        connection.close()

        if user and check_password_hash(user["password_hash"], password):
            message = "Login Berhasil! Selamat datang."
            status_class = "success"
        else:
            message = "Login Gagal! Kredensial tidak valid."
            status_class = "danger"

    return render_template(
        "index.html",
        message=message,
        status_class=status_class,
    )


if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=False)
