from flask import Flask, render_template, request, redirect, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "secret123"

# ================= DB CONNECTION =================
def get_db():
    return sqlite3.connect("database.db")

# ================= CREATE DEFAULT ADMIN =================
def create_admin():
    db = get_db()

    user = db.execute("SELECT * FROM users WHERE username='admin'").fetchone()

    if not user:
        db.execute("""INSERT INTO users
                      (name, username, email, password, role, verified)
                      VALUES (?,?,?,?,?,1)""",
                   ("Admin",
                    "admin",
                    "admin@gmail.com",
                    generate_password_hash("admin123"),
                    "admin"))
        db.commit()
        print("Default admin created!")

    db.close()

# ================= HOME =================
@app.route('/')
def home():
    return render_template("index.html")

# ================= REGISTER =================
@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':

        if 'generate_otp' in request.form:
            otp = "1234"

            session['temp'] = {
                "name": request.form['name'],
                "username": request.form['username'],
                "email": request.form['email'],
                "password": generate_password_hash(request.form['password']),
                "role": request.form['role'],
                "otp": otp
            }

            return render_template("register.html", show_otp=True, otp=otp)

        if 'verify_otp' in request.form:
            if 'temp' not in session:
                return redirect('/register')

            if request.form['otp'] == session['temp']['otp']:
                data = session['temp']

                db = get_db()
                db.execute("""INSERT INTO users
                              (name, username, email, password, role, verified)
                              VALUES (?,?,?,?,?,1)""",
                           (data['name'], data['username'], data['email'],
                            data['password'], data['role']))
                db.commit()

                session.pop('temp')
                return redirect('/login')
            else:
                return render_template("register.html",
                                       show_otp=True,
                                       otp=session['temp']['otp'],
                                       error="Invalid OTP")

    return render_template("register.html")

# ================= LOGIN =================
@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        db = get_db()
        user = db.execute("SELECT * FROM users WHERE username=?",
                          (request.form['username'],)).fetchone()

        if user and check_password_hash(user[4], request.form['password']):
            session['user'] = user[2]
            session['role'] = user[5].strip().lower()

            if session['role'] == 'admin':
                return redirect('/admin')
            else:
                return redirect('/dashboard')
        else:
            return "Invalid Login"

    return render_template("login.html")

# ================= USER DASHBOARD =================
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    db = get_db()

    complaints = db.execute("SELECT * FROM complaints WHERE user=?",
                            (session['user'],)).fetchall()

    total = db.execute("SELECT COUNT(*) FROM complaints").fetchone()[0]
    resolved = db.execute("SELECT COUNT(*) FROM complaints WHERE status='Resolved'").fetchone()[0]
    pending = db.execute("SELECT COUNT(*) FROM complaints WHERE status='Pending'").fetchone()[0]

    return render_template("dashboard.html",
                           complaints=complaints,
                           total=total,
                           resolved=resolved,
                           pending=pending)

# ================= ADD COMPLAINT =================
@app.route('/complaint', methods=['GET','POST'])
def complaint():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':
        db = get_db()

        db.execute("""INSERT INTO complaints
                      (user, category, description, location, priority, date, status)
                      VALUES (?,?,?,?,?,?,?)""",
                   (session['user'],
                    request.form['category'],
                    request.form['description'],
                    request.form['location'],
                    request.form['priority'],
                    datetime.now().strftime("%Y-%m-%d %H:%M"),
                    "Pending"))

        db.commit()
        return redirect('/dashboard')

    return render_template("complaint.html")

# ================= ADMIN PANEL =================
@app.route('/admin')
def admin():
    if 'user' not in session or session.get('role') != 'admin':
        return "Access Denied ❌"

    db = get_db()
    complaints = db.execute("SELECT * FROM complaints").fetchall()

    return render_template("admin.html", complaints=complaints)

# ================= UPDATE STATUS =================
@app.route('/update_status/<int:id>/<status>')
def update_status(id, status):
    if 'user' not in session or session.get('role') != 'admin':
        return redirect('/login')

    db = get_db()
    db.execute("UPDATE complaints SET status=? WHERE id=?", (status, id))
    db.commit()

    return redirect('/admin')

# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

# ================= RUN =================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000, debug=False)