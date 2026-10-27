"""Pengujian otomatis untuk aplikasi login Flask."""

import sqlite3

import pytest
from werkzeug.security import generate_password_hash

import app as app_module


@pytest.fixture
def client(tmp_path):
    """Menyiapkan database terpisah untuk setiap rangkaian test."""
    database_path = tmp_path / "test_users.db"
    app_module.app.config["TESTING"] = True
    app_module.app.config["DATABASE"] = str(database_path)
    app_module.init_db()

    connection = sqlite3.connect(database_path)
    connection.execute(
        """
        INSERT INTO users (username, password_hash)
        VALUES (?, ?)
        """,
        ("admin-test", generate_password_hash("password-test-123")),
    )
    connection.commit()
    connection.close()

    with app_module.app.test_client() as test_client:
        yield test_client


def test_login_page_opens(client):
    """Halaman login harus dapat dibuka."""
    response = client.get("/")
    assert response.status_code == 200
    assert b"Portal Login" in response.data


def test_login_success(client):
    """Kredensial pengujian yang benar harus diterima."""
    response = client.post(
        "/",
        data={
            "username": "admin-test",
            "password": "password-test-123",
        },
    )
    assert response.status_code == 200
    assert b"Login Berhasil" in response.data


def test_login_failure(client):
    """Password yang salah harus ditolak."""
    response = client.post(
        "/",
        data={"username": "admin-test", "password": "password-salah"},
    )
    assert response.status_code == 200
    assert b"Login Gagal" in response.data
