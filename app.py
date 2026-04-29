import os
import psycopg2
from flask import Flask, render_template, request, redirect, session, send_file
import pandas as pd
import tempfile

app = Flask(__name__)
app.secret_key = "secret123"

# ✅ Works for BOTH local + Render
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:1234@localhost:5432/student_db"
)

# DATABASE CONNECTION
def get_db():
    return psycopg2.connect(DATABASE_URL, sslmode='require')

# CREATE TABLE
def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE IF NOT EXISTS students (
            id SERIAL PRIMARY KEY,
            name TEXT,
            Name_Aadhar TEXT,
            Aadhar_Number TEXT,
            Name_of_the_Mother TEXT,
            Name_of_the_Father TEXT,
            Date_of_Birth TEXT,
            Gender TEXT,
            Religion TEXT,
            Qualifying_Examination TEXT,
            Code_of_Native_State TEXT,
            Code_of_Native_District TEXT,
            Total_No_of_Years_Studied_In_Karnataka TEXT,
            You_Have_Studied_In_Rural_Areas_From_1_to_10 TEXT,
            Have_You_Studied_In_Kanada_Medium_From_1_to_10 TEXT,
            Do_You_Claming_Exemption_From_5_Years_of_Study_Rule TEXT,
            Do_You_Claiming_SNQ_Quota_Benefit TEXT,
            Do_You_Claiming_HydKar_Quota_Benefit TEXT,
            Do_You_Claiming_Special_Category_Benefit TEXT,
            Reserved_Category TEXT,
            Name_of_the_Cast TEXT,
            Annual_Income TEXT,
            Register_No_of_SSLC_Or_Equivalent_Exam TEXT,
            Year_of_Passing TEXT,
            Total_Max_Marks_In_all_Subjects TEXT,
            Total_Marks_Obtained_In_All_Subjects TEXT,
            Max_Marks_In_Science TEXT,
            Marks_Obtained_In_Science TEXT,
            Max_Marks_In_Maths TEXT,
            Marks_Obtained_In_Maths TEXT,
            course TEXT
        )
    ''')

    conn.commit()
    cur.close()
    conn.close()

init_db()

@app.route('/')
def home():
    return render_template('index.html')

# LOGIN USER
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        if request.form['username'] == 'user' and request.form['password'] == '1234':
            session['user'] = True
            return redirect('/add')
    return render_template('login.html')

# LOGIN ADMIN
@app.route('/login2', methods=['GET', 'POST'])
def login2():
    if request.method == 'POST':
        if request.form['username'] == 'admin' and request.form['password'] == '1234':
            session['user'] = True
            return redirect('/dashboard')
    return render_template('login2.html')

# DASHBOARD
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/')

    conn = get_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM students ORDER BY id DESC")
    rows = cur.fetchall()

    columns = [desc[0] for desc in cur.description]
    data = [dict(zip(columns, row)) for row in rows]

    cur.close()
    conn.close()

    return render_template('dashboard.html', data=data)

# ADD STUDENT
@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        conn = get_db()
        cur = conn.cursor()

        cur.execute("""
            INSERT INTO students (
                name, Name_Aadhar, Aadhar_Number, Name_of_the_Mother,
                Name_of_the_Father, Date_of_Birth, Gender, Religion,
                Qualifying_Examination, Code_of_Native_State, Code_of_Native_District,
                Total_No_of_Years_Studied_In_Karnataka,
                You_Have_Studied_In_Rural_Areas_From_1_to_10,
                Have_You_Studied_In_Kanada_Medium_From_1_to_10,
                Do_You_Claming_Exemption_From_5_Years_of_Study_Rule,
                Do_You_Claiming_SNQ_Quota_Benefit,
                Do_You_Claiming_HydKar_Quota_Benefit,
                Do_You_Claiming_Special_Category_Benefit,
                Reserved_Category, Name_of_the_Cast, Annual_Income,
                Register_No_of_SSLC_Or_Equivalent_Exam, Year_of_Passing,
                Total_Max_Marks_In_all_Subjects,
                Total_Marks_Obtained_In_All_Subjects,
                Max_Marks_In_Science, Marks_Obtained_In_Science,
                Max_Marks_In_Maths, Marks_Obtained_In_Maths, course
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, tuple(request.form.values()))

        conn.commit()
        cur.close()
        conn.close()

        return render_template('form.html', success=True)

    return render_template('form.html', success=False)

# DELETE
@app.route('/delete/<int:id>')
def delete(id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute("DELETE FROM students WHERE id=%s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return redirect('/dashboard')

# EDIT
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_db()
    cur = conn.cursor()

    if request.method == 'POST':
        cur.execute("""
            UPDATE students SET
                name=%s, Name_Aadhar=%s, Aadhar_Number=%s, Name_of_the_Mother=%s,
                Name_of_the_Father=%s, Date_of_Birth=%s, Gender=%s, Religion=%s,
                Qualifying_Examination=%s, Code_of_Native_State=%s, Code_of_Native_District=%s,
                Total_No_of_Years_Studied_In_Karnataka=%s,
                You_Have_Studied_In_Rural_Areas_From_1_to_10=%s,
                Have_You_Studied_In_Kanada_Medium_From_1_to_10=%s,
                Do_You_Claming_Exemption_From_5_Years_of_Study_Rule=%s,
                Do_You_Claiming_SNQ_Quota_Benefit=%s,
                Do_You_Claiming_HydKar_Quota_Benefit=%s,
                Do_You_Claiming_Special_Category_Benefit=%s,
                Reserved_Category=%s, Name_of_the_Cast=%s, Annual_Income=%s,
                Register_No_of_SSLC_Or_Equivalent_Exam=%s, Year_of_Passing=%s,
                Total_Max_Marks_In_all_Subjects=%s,
                Total_Marks_Obtained_In_All_Subjects=%s,
                Max_Marks_In_Science=%s, Marks_Obtained_In_Science=%s,
                Max_Marks_In_Maths=%s, Marks_Obtained_In_Maths=%s, course=%s
            WHERE id=%s
        """, (*request.form.values(), id))

        conn.commit()
        cur.close()
        conn.close()
        return redirect('/dashboard')

    cur.execute("SELECT * FROM students WHERE id=%s", (id,))
    row = cur.fetchone()

    columns = [desc[0] for desc in cur.description]
    student = dict(zip(columns, row))

    cur.close()
    conn.close()

    return render_template('edit.html', student=student)

# EXPORT
@app.route('/export')
def export():
    conn = get_db()
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    df.to_excel(temp.name, index=False)

    return send_file(temp.name, as_attachment=True)

# LOGOUT
@app.route('/logout')
def logout():
    session.clear()
    return redirect('/')

if __name__ == "__main__":
    app.run(debug=True)
