# Patient Management System

A simple, lightweight, and modern **Patient Management System** built with **Python Flask**, **SQLite**, **Bootstrap 5**, **Docker**, and **Nginx**.

---

## Features

- **Four Patient Fields**:
  - `Patient ID` (Unique identifier)
  - `Patient Name` (Full name)
  - `Age` (Numeric age)
  - `Blood Group` (A+, A-, B+, B-, AB+, AB-, O+, O-)
- **Full CRUD Support**:
  - **Create**: Add new patients with field validation and unique Patient ID check.
  - **Read**: Display all patient records in a responsive medical dashboard table.
  - **Update**: Edit patient name, age, and blood group.
  - **Delete**: Remove patient records with confirmation alerts.
- **Production Architecture**:
  - Production WSGI server (**Gunicorn**).
  - Reverse proxy (**Nginx**) listening on port 80.
  - Persistent SQLite storage using a named Docker volume (`patient_db_data`).
  - Isolated Docker network (`patient_network`).

---

## Quick Start

### 1. Build and Start the Application
```bash
docker-compose up --build -d
```
*(or `docker compose up --build -d`)*

### 2. Access the Dashboard
Open your browser and navigate to:
```
http://localhost
```

### 3. Stop the Containers
```bash
docker-compose down
```

### 4. Restart the Containers
```bash
docker-compose restart
```

---

## Project Structure

```
Patient Management System/
│── app.py                   # Flask backend with SQLite CRUD logic & validation
│── requirements.txt         # Python dependencies (Flask, Gunicorn)
│── Dockerfile               # Container build instructions for Flask + Gunicorn
│── docker-compose.yml       # Multi-container orchestration (Flask + Nginx)
│── .dockerignore            # Build exclusions
│── README.md                # Documentation
│── templates/
│   ├── index.html           # Main dashboard table and Add Patient modal
│   └── edit.html            # Edit patient form
│── static/
│   └── style.css            # Medical theme styling (light blue & white)
└── nginx/
    └── default.conf         # Nginx reverse proxy configuration (port 80 -> web:5000)
```
