import os
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash, abort

app = Flask(__name__)
app.secret_key = os.environ.get('FLASK_SECRET_KEY', 'patient-secret-key-default-2026')

# Database configuration
DB_DIR = os.environ.get('DB_DIR', os.path.join(os.path.dirname(__file__), 'data'))
os.makedirs(DB_DIR, exist_ok=True)
DB_PATH = os.path.join(DB_DIR, 'patients.db')

VALID_BLOOD_GROUPS = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']


def get_db_connection():
    """Create and return a database connection with Row factory."""
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize the SQLite database schema."""
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS patients (
                patient_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                age INTEGER NOT NULL,
                blood_group TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


# Initialize database on app startup
init_db()


@app.route('/')
def index():
    """Display dashboard with all patient records."""
    conn = get_db_connection()
    patients = conn.execute("SELECT patient_id, name, age, blood_group FROM patients ORDER BY rowid DESC").fetchall()
    conn.close()
    return render_template('index.html', patients=patients, blood_groups=VALID_BLOOD_GROUPS)


@app.route('/add', methods=['POST'])
def add_patient():
    """Create a new patient record."""
    patient_id = request.form.get('patient_id', '').strip()
    name = request.form.get('name', '').strip()
    age_raw = request.form.get('age', '').strip()
    blood_group = request.form.get('blood_group', '').strip().upper()

    # Field validations
    if not patient_id:
        flash('Patient ID is required.', 'danger')
        return redirect(url_for('index'))

    if not name:
        flash('Patient Name is required.', 'danger')
        return redirect(url_for('index'))

    try:
        age = int(age_raw)
        if age <= 0 or age > 150:
            flash('Please enter a valid age between 1 and 150.', 'danger')
            return redirect(url_for('index'))
    except ValueError:
        flash('Age must be a valid whole number.', 'danger')
        return redirect(url_for('index'))

    if blood_group not in VALID_BLOOD_GROUPS:
        flash(f'Invalid blood group selected. Must be one of: {", ".join(VALID_BLOOD_GROUPS)}', 'danger')
        return redirect(url_for('index'))

    # Check for unique Patient ID
    conn = get_db_connection()
    existing = conn.execute("SELECT patient_id FROM patients WHERE patient_id = ?", (patient_id,)).fetchone()
    if existing:
        conn.close()
        flash(f"Patient ID '{patient_id}' already exists. Please use a unique Patient ID.", 'danger')
        return redirect(url_for('index'))

    try:
        conn.execute(
            "INSERT INTO patients (patient_id, name, age, blood_group) VALUES (?, ?, ?, ?)",
            (patient_id, name, age, blood_group)
        )
        conn.commit()
        flash(f"Patient '{name}' (ID: {patient_id}) was successfully added!", 'success')
    except sqlite3.IntegrityError:
        flash(f"Database error: Patient ID '{patient_id}' already exists.", 'danger')
    except Exception as e:
        flash(f"An unexpected error occurred: {str(e)}", 'danger')
    finally:
        conn.close()

    return redirect(url_for('index'))


@app.route('/edit/<patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    """View and update an existing patient record."""
    conn = get_db_connection()
    patient = conn.execute("SELECT * FROM patients WHERE patient_id = ?", (patient_id,)).fetchone()

    if patient is None:
        conn.close()
        flash(f"Patient with ID '{patient_id}' was not found.", 'warning')
        return redirect(url_for('index'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        age_raw = request.form.get('age', '').strip()
        blood_group = request.form.get('blood_group', '').strip().upper()

        if not name:
            flash('Patient Name is required.', 'danger')
            conn.close()
            return render_template('edit.html', patient=patient, blood_groups=VALID_BLOOD_GROUPS)

        try:
            age = int(age_raw)
            if age <= 0 or age > 150:
                flash('Please enter a valid age between 1 and 150.', 'danger')
                conn.close()
                return render_template('edit.html', patient=patient, blood_groups=VALID_BLOOD_GROUPS)
        except ValueError:
            flash('Age must be a valid whole number.', 'danger')
            conn.close()
            return render_template('edit.html', patient=patient, blood_groups=VALID_BLOOD_GROUPS)

        if blood_group not in VALID_BLOOD_GROUPS:
            flash(f'Invalid blood group selected. Must be one of: {", ".join(VALID_BLOOD_GROUPS)}', 'danger')
            conn.close()
            return render_template('edit.html', patient=patient, blood_groups=VALID_BLOOD_GROUPS)

        conn.execute(
            "UPDATE patients SET name = ?, age = ?, blood_group = ? WHERE patient_id = ?",
            (name, age, blood_group, patient_id)
        )
        conn.commit()
        conn.close()
        flash(f"Patient details for ID '{patient_id}' updated successfully!", 'success')
        return redirect(url_for('index'))

    conn.close()
    return render_template('edit.html', patient=patient, blood_groups=VALID_BLOOD_GROUPS)


@app.route('/delete/<patient_id>', methods=['POST', 'GET'])
def delete_patient(patient_id):
    """Delete a patient record."""
    conn = get_db_connection()
    patient = conn.execute("SELECT name FROM patients WHERE patient_id = ?", (patient_id,)).fetchone()

    if patient is None:
        conn.close()
        flash(f"Patient with ID '{patient_id}' does not exist.", 'warning')
        return redirect(url_for('index'))

    patient_name = patient['name']
    conn.execute("DELETE FROM patients WHERE patient_id = ?", (patient_id,))
    conn.commit()
    conn.close()

    flash(f"Patient '{patient_name}' (ID: {patient_id}) has been removed successfully.", 'info')
    return redirect(url_for('index'))


@app.route('/health')
def health():
    """Health check endpoint for Docker / Nginx."""
    return {"status": "ok", "service": "patient-management-system"}, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
