"""
IDOR Vulnerability Lab - Flask Application
==========================================
WARNING: This application is INTENTIONALLY INSECURE.
It is designed for security testing practice with Burp Suite.
DO NOT deploy this in any production or public environment.
"""

import os
import sqlite3
import json
from flask import (
    Flask, request, session, redirect, url_for,
    render_template, jsonify, send_from_directory, g
)

app = Flask(__name__)
app.secret_key = "super_insecure_secret_key_do_not_use"  # VULNERABLE: Hardcoded weak secret

DATABASE = "database.db"
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ─────────────────────────────────────────
# Database Helpers
# ─────────────────────────────────────────

def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()


def init_db():
    """Create tables and seed demo data."""
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row
    cur = db.cursor()

    # Users table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT    NOT NULL UNIQUE,
            email    TEXT    NOT NULL,
            password TEXT    NOT NULL
        )
    """)

    # Notes table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            content TEXT    NOT NULL
        )
    """)

    # Files table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id       INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id  INTEGER NOT NULL,
            filename TEXT    NOT NULL
        )
    """)

    db.commit()

    # ── Seed data (only if tables are empty) ──────────────────────────
    if cur.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
        users = [
            (1, "user1", "user1@lab.com", "password1"),
            (2, "user2", "user2@lab.com", "password2"),
            (3, "admin", "admin@lab.com", "adminpass"),
        ]
        cur.executemany(
            "INSERT INTO users (id, username, email, password) VALUES (?,?,?,?)",
            users,
        )

        notes = [
            (1, 1, "user1's private note: My secret project idea."),
            (2, 1, "user1's note: Meeting at 3pm today."),
            (3, 2, "user2's private note: Bank PIN is 4321."),
            (4, 2, "user2's note: Doctor appointment Friday."),
            (5, 3, "Admin note: Server credentials stored in /etc/shadow."),
            (6, 3, "Admin note: Internal salary spreadsheet is on shared drive."),
        ]
        cur.executemany(
            "INSERT INTO notes (id, user_id, content) VALUES (?,?,?)",
            notes,
        )

        # Create seed upload files on disk
        seed_files = [
            (1, 1, "user1_private.txt"),
            (2, 2, "user2_confidential.txt"),
            (3, 3, "admin_secrets.txt"),
        ]
        for fid, uid, fname in seed_files:
            fpath = os.path.join(UPLOAD_FOLDER, fname)
            if not os.path.exists(fpath):
                with open(fpath, "w") as f:
                    f.write(f"This is a sensitive file belonging to user_id={uid}.\n")
            cur.execute(
                "INSERT INTO files (id, user_id, filename) VALUES (?,?,?)",
                (fid, uid, fname),
            )

        db.commit()

    db.close()


# ─────────────────────────────────────────
# Auth Routes
# ─────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html", user=session.get("user"))


@app.route("/signup", methods=["GET", "POST"])
def signup():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        email    = request.form.get("email")
        password = request.form.get("password")  # VULNERABLE: plaintext password storage
        db = get_db()
        try:
            db.execute(
                "INSERT INTO users (username, email, password) VALUES (?,?,?)",
                (username, email, password),
            )
            db.commit()
            return redirect(url_for("login"))
        except sqlite3.IntegrityError:
            error = "Username already exists."
    return render_template("signup.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        db  = get_db()
        # VULNERABLE: No rate limiting, no brute-force protection
        row = db.execute(
            "SELECT * FROM users WHERE username=? AND password=?",
            (username, password),
        ).fetchone()
        if row:
            session["user"]    = dict(row)
            session["user_id"] = row["id"]
            return redirect(url_for("index"))
        else:
            error = "Invalid credentials."
    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))


# ─────────────────────────────────────────
# Profile – IDOR #1
# ─────────────────────────────────────────

@app.route("/profile")
def profile():
    # VULNERABLE: IDOR here – no check that the requesting user owns this profile
    user_id = request.args.get("id")
    db  = get_db()
    row = db.execute("SELECT * FROM users WHERE id=?", (user_id,)).fetchone()
    if not row:
        return "User not found", 404
    return render_template("profile.html", profile=dict(row), current_user=session.get("user"))


# ─────────────────────────────────────────
# Notes System – IDOR #2, #3, #4
# ─────────────────────────────────────────

@app.route("/notes")
def notes():
    # VULNERABLE: IDOR here – any user_id accepted from query string
    user_id = request.args.get("user_id", session.get("user_id", 1))
    db      = get_db()
    rows    = db.execute("SELECT * FROM notes WHERE user_id=?", (user_id,)).fetchall()
    owner   = db.execute("SELECT username FROM users WHERE id=?", (user_id,)).fetchone()
    return render_template(
        "notes.html",
        notes=[dict(r) for r in rows],
        owner=owner["username"] if owner else "Unknown",
        user_id=user_id,
        current_user=session.get("user"),
    )


@app.route("/create_note", methods=["POST"])
def create_note():
    # VULNERABLE: IDOR here – user_id taken from form, not verified against session
    user_id = request.form.get("user_id", session.get("user_id"))
    content = request.form.get("content")
    db      = get_db()
    db.execute("INSERT INTO notes (user_id, content) VALUES (?,?)", (user_id, content))
    db.commit()
    return redirect(url_for("notes", user_id=user_id))


@app.route("/edit_note", methods=["GET", "POST"])
def edit_note():
    # VULNERABLE: IDOR here – no ownership check on note id
    note_id = request.args.get("id") or request.form.get("id")
    db      = get_db()
    note    = db.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone()
    if not note:
        return "Note not found", 404
    if request.method == "POST":
        new_content = request.form.get("content")
        db.execute("UPDATE notes SET content=? WHERE id=?", (new_content, note_id))
        db.commit()
        return redirect(url_for("notes", user_id=note["user_id"]))
    return render_template("notes.html", edit_note=dict(note), current_user=session.get("user"), notes=[], owner="", user_id=note["user_id"])


@app.route("/delete_note")
def delete_note():
    # VULNERABLE: IDOR here – any note can be deleted by ID, no auth check
    note_id = request.args.get("id")
    db      = get_db()
    note    = db.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone()
    if not note:
        return "Note not found", 404
    db.execute("DELETE FROM notes WHERE id=?", (note_id,))
    db.commit()
    return redirect(url_for("notes", user_id=note["user_id"]))


# ─────────────────────────────────────────
# File Upload / Download – IDOR #5
# ─────────────────────────────────────────

@app.route("/upload", methods=["GET", "POST"])
def upload():
    message = None
    if request.method == "POST":
        f = request.files.get("file")
        if f:
            filename = f.filename  # VULNERABLE: No sanitization of filename
            f.save(os.path.join(UPLOAD_FOLDER, filename))
            # VULNERABLE: IDOR here – user_id taken from form data
            user_id = request.form.get("user_id", session.get("user_id", 1))
            db = get_db()
            db.execute(
                "INSERT INTO files (user_id, filename) VALUES (?,?)",
                (user_id, filename),
            )
            db.commit()
            message = f"File '{filename}' uploaded successfully."
    return render_template("upload.html", message=message, current_user=session.get("user"))


@app.route("/download")
def download():
    # VULNERABLE: IDOR here – file_id not checked against logged-in user
    file_id = request.args.get("file_id")
    db      = get_db()
    row     = db.execute("SELECT * FROM files WHERE id=?", (file_id,)).fetchone()
    if not row:
        return "File not found", 404
    filename = row["filename"]
    return send_from_directory(UPLOAD_FOLDER, filename, as_attachment=True)


@app.route("/files")
def list_files():
    db   = get_db()
    rows = db.execute("SELECT files.*, users.username FROM files JOIN users ON files.user_id=users.id").fetchall()
    return render_template("files.html", files=[dict(r) for r in rows], current_user=session.get("user"))


# ─────────────────────────────────────────
# Admin Panel – IDOR / Broken Access #6
# ─────────────────────────────────────────

@app.route("/admin")
def admin():
    # VULNERABLE: IDOR / Broken Access Control here
    # Role is taken directly from query param or JSON body – never validated server-side
    role = request.args.get("role")
    if not role:
        data = request.get_json(silent=True) or {}
        role = data.get("role")

    if role != "admin":
        return render_template("admin.html", access=False, current_user=session.get("user"))

    db    = get_db()
    users = db.execute("SELECT * FROM users").fetchall()
    notes = db.execute("SELECT * FROM notes").fetchall()
    files = db.execute("SELECT * FROM files").fetchall()
    return render_template(
        "admin.html",
        access=True,
        users=[dict(u) for u in users],
        notes=[dict(n) for n in notes],
        files=[dict(f) for f in files],
        current_user=session.get("user"),
    )


# ─────────────────────────────────────────
# API Endpoints – IDOR #7, #8
# ─────────────────────────────────────────

@app.route("/api/update_email", methods=["POST"])
def api_update_email():
    # VULNERABLE: IDOR here – trusts user_id from client, no session check
    data    = request.get_json(silent=True) or {}
    user_id = data.get("user_id")
    email   = data.get("email")
    if not user_id or not email:
        return jsonify({"error": "user_id and email required"}), 400
    db = get_db()
    db.execute("UPDATE users SET email=? WHERE id=?", (email, user_id))
    db.commit()
    updated = db.execute("SELECT id, username, email FROM users WHERE id=?", (user_id,)).fetchone()
    return jsonify({"message": "Email updated", "user": dict(updated) if updated else None})


@app.route("/api/delete_notes", methods=["POST"])
def api_delete_notes():
    # VULNERABLE: IDOR here – deletes any notes by IDs without ownership check
    data = request.get_json(silent=True) or {}
    ids  = data.get("ids", [])
    if not ids:
        return jsonify({"error": "ids list required"}), 400
    db = get_db()
    db.executemany("DELETE FROM notes WHERE id=?", [(i,) for i in ids])
    db.commit()
    return jsonify({"message": f"Deleted notes with ids: {ids}"})


# ─────────────────────────────────────────
# Advanced IDOR – Nested Endpoint #9
# ─────────────────────────────────────────

@app.route("/api/users/<int:user_id>/notes/<int:note_id>", methods=["GET", "PUT", "DELETE"])
def api_user_note(user_id, note_id):
    # VULNERABLE: IDOR here – user_id in URL not cross-checked with session user
    db   = get_db()
    note = db.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone()
    if not note:
        return jsonify({"error": "Note not found"}), 404

    if request.method == "GET":
        return jsonify(dict(note))

    if request.method == "PUT":
        data    = request.get_json(silent=True) or {}
        content = data.get("content", note["content"])
        db.execute("UPDATE notes SET content=? WHERE id=?", (content, note_id))
        db.commit()
        return jsonify({"message": "Note updated", "note_id": note_id})

    if request.method == "DELETE":
        db.execute("DELETE FROM notes WHERE id=?", (note_id,))
        db.commit()
        return jsonify({"message": f"Note {note_id} deleted"})


# ─────────────────────────────────────────
# Blind IDOR – Change Password #10
# ─────────────────────────────────────────

@app.route("/api/change_password", methods=["POST"])
def api_change_password():
    # VULNERABLE: Blind IDOR here – changes ANY user's password using user_id from body
    data         = request.get_json(silent=True) or {}
    user_id      = data.get("user_id")
    new_password = data.get("new_password")
    if not user_id or not new_password:
        return jsonify({"error": "user_id and new_password required"}), 400
    db = get_db()
    db.execute("UPDATE users SET password=? WHERE id=?", (new_password, user_id))
    db.commit()
    # VULNERABLE: Returns 200 even for non-existent users (blind)
    return jsonify({"message": "Password changed successfully"})


# ─────────────────────────────────────────
# Bonus: All users listing (no auth)
# ─────────────────────────────────────────

@app.route("/api/users", methods=["GET"])
def api_users():
    # VULNERABLE: Exposes all user data with no authentication
    db    = get_db()
    users = db.execute("SELECT id, username, email, password FROM users").fetchall()
    return jsonify([dict(u) for u in users])


# ─────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    # VULNERABLE: Debug mode enabled – exposes stack traces and Werkzeug debugger
    app.run(debug=True, host="0.0.0.0", port=5000)
