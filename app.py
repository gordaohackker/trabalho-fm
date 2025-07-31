
from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3

app = Flask(__name__)
app.secret_key = "supersecretkey"

DATABASE = 'usuarios.db'

# Credenciais do administrador fixo
ADMIN_EMAIL = "adm@loja.com"
ADMIN_SENHA = "loja123"

def init_db():
    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        senha TEXT NOT NULL
    )
    ''')
    c.execute('''
    CREATE TABLE IF NOT EXISTS candidaturas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_email TEXT,
        vaga TEXT,
        escolaridade TEXT,
        estado_civil TEXT,
        motivo TEXT,
        disponibilidade TEXT,
        nome_completo TEXT,
        telefone TEXT,
        email_contato TEXT
    )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        email = request.form['email']
        senha = request.form['senha']

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        try:
            c.execute("INSERT INTO users (email, senha) VALUES (?, ?)", (email, senha))
            conn.commit()
            session['user'] = email
            return redirect(url_for('vagas'))
        except sqlite3.IntegrityError:
            c.execute("SELECT * FROM users WHERE email=? AND senha=?", (email, senha))
            if c.fetchone():
                session['user'] = email
                return redirect(url_for('vagas'))
            else:
                return render_template("login.html", msg="Email já cadastrado ou senha incorreta.")
        finally:
            conn.close()
    return render_template("login.html")

@app.route("/vagas", methods=["GET", "POST"])
def vagas():
    if 'user' not in session:
        return redirect(url_for('index'))
    
    if request.method == "POST":
        vaga = request.form['vaga']
        escolaridade = request.form['escolaridade']
        estado_civil = request.form['estado_civil']
        motivo = request.form['motivo']
        disponibilidade = request.form['disponibilidade']
        nome = request.form['nome']
        telefone = request.form['telefone']
        email_contato = request.form['email_contato']
        user_email = session['user']

        conn = sqlite3.connect(DATABASE)
        c = conn.cursor()
        c.execute('''INSERT INTO candidaturas 
                     (user_email, vaga, escolaridade, estado_civil, motivo, disponibilidade, nome_completo, telefone, email_contato)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)''',
                  (user_email, vaga, escolaridade, estado_civil, motivo, disponibilidade, nome, telefone, email_contato))
        conn.commit()
        conn.close()
        return render_template("vagas.html", msg="Informações enviadas com sucesso em breve entraremos em contato!")
    
    return render_template("vagas.html")

@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        email = request.form['email']
        senha = request.form['senha']
        if email == ADMIN_EMAIL and senha == ADMIN_SENHA:
            session['admin'] = True
            return redirect(url_for('painel'))
        else:
            return render_template("admin_login.html", msg="Credenciais incorretas,voce esta sendo monitorado.")
    return render_template("admin_login.html")

@app.route("/painel")
def painel():
    if not session.get('admin'):
        return redirect(url_for('admin'))

    conn = sqlite3.connect(DATABASE)
    c = conn.cursor()
    c.execute("SELECT * FROM users")
    usuarios = c.fetchall()
    c.execute("SELECT * FROM candidaturas")
    candidaturas = c.fetchall()
    conn.close()
    return render_template("admin.html", usuarios=usuarios, candidaturas=candidaturas)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=False, host="0.0.0.0")
