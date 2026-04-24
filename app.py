import streamlit as st
import sqlite3

# Database
conn = sqlite3.connect('database.db', check_same_thread=False)
c = conn.cursor()

# Create tables
c.execute('''CREATE TABLE IF NOT EXISTS users
             (id INTEGER PRIMARY KEY, username TEXT, password TEXT, role TEXT, org_id INTEGER)''')

c.execute('''CREATE TABLE IF NOT EXISTS tasks
             (id INTEGER PRIMARY KEY, title TEXT, description TEXT, assigned_to TEXT, org_id INTEGER)''')

conn.commit()

# Session
if "user" not in st.session_state:
    st.session_state.user = None

st.title("Multi-Tenant Task Manager")

menu = ["Login", "Register"]
choice = st.sidebar.selectbox("Menu", menu)

# REGISTER
if choice == "Register":
    st.subheader("Register")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')
    role = st.selectbox("Role", ["admin", "user"])
    org_id = st.number_input("Organization ID", min_value=1)

    if st.button("Register"):
        c.execute("INSERT INTO users (username, password, role, org_id) VALUES (?, ?, ?, ?)",
                  (username, password, role, org_id))
        conn.commit()
        st.success("User Registered!")

# LOGIN
if choice == "Login":
    st.subheader("Login")
    username = st.text_input("Username")
    password = st.text_input("Password", type='password')

    if st.button("Login"):
        c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
        user = c.fetchone()
        if user:
            st.session_state.user = user
            st.success("Logged in!")
        else:
            st.error("Invalid credentials")

# DASHBOARD
if st.session_state.user:
    user = st.session_state.user
    st.sidebar.write(f"Logged in as {user[1]} ({user[3]})")

    if st.sidebar.button("Logout"):
        st.session_state.user = None

    st.header("Dashboard")

    # Admin
    if user[3] == "admin":
        st.subheader("Create Task")
        title = st.text_input("Task Title")
        desc = st.text_area("Description")
        assigned_to = st.text_input("Assign to (username)")

        if st.button("Create Task"):
            c.execute("INSERT INTO tasks (title, description, assigned_to, org_id) VALUES (?, ?, ?, ?)",
                      (title, desc, assigned_to, user[4]))
            conn.commit()
            st.success("Task Created!")

    # View tasks
    st.subheader("Your Tasks")

    if user[3] == "admin":
        c.execute("SELECT * FROM tasks WHERE org_id=?", (user[4],))
    else:
        c.execute("SELECT * FROM tasks WHERE assigned_to=? AND org_id=?", (user[1], user[4]))

    tasks = c.fetchall()

    for t in tasks:
        st.write(f"{t[1]} - {t[2]} (Assigned to: {t[3]})")