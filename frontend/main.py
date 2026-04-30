import flet as ft
import os
import sqlite3

# ---------------- DATABASE ----------------
conn = sqlite3.connect("uy1.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS etudiants (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT,
    prenom TEXT,
    matricule TEXT,
    niveau TEXT,
    filiere TEXT,
    faculte TEXT,
    annee TEXT
)
""")
conn.commit()

admin_connected = False

# ---------------- HOME ----------------
def home(page: ft.Page):

    def go_form(e):
        page.clean()
        page.add(form(page))

    def go_admin(e):
        page.clean()
        page.add(admin(page))

    def go_dashboard(e):
        page.clean()
        page.add(dashboard(page))

    return ft.Column(
        [
            ft.Text("🎓 UY1 SYSTEM", size=30),
            ft.ElevatedButton("Étudiant", on_click=go_form),
            ft.ElevatedButton("Admin", on_click=go_admin),
            ft.ElevatedButton("Dashboard", on_click=go_dashboard),
        ]
    )

# ---------------- FORM ----------------
def form(page):

    nom = ft.TextField(label="Nom")
    prenom = ft.TextField(label="Prénom")
    matricule = ft.TextField(label="Matricule")
    niveau = ft.TextField(label="Niveau")
    filiere = ft.TextField(label="Filière")
    faculte = ft.TextField(label="Faculté")
    annee = ft.TextField(label="Année")

    def save(e):
        cursor.execute("""
            INSERT INTO etudiants VALUES (NULL,?,?,?,?,?,?,?)
        """, (nom.value, prenom.value, matricule.value,
              niveau.value, filiere.value, faculte.value, annee.value))
        conn.commit()

        page.snack_bar = ft.SnackBar(ft.Text("Ajout réussi ✔"))
        page.snack_bar.open = True
        page.update()

    return ft.Column(
        [
            nom, prenom, matricule,
            niveau, filiere, faculte, annee,
            ft.ElevatedButton("Enregistrer", on_click=save),
            ft.ElevatedButton("Retour", on_click=lambda e: (page.clean(), page.add(home(page))))
        ]
    )

# ---------------- ADMIN ----------------
def admin(page):

    global admin_connected

    user = ft.TextField(label="User")
    pwd = ft.TextField(label="Password", password=True)
    msg = ft.Text()

    def login(e):
        global admin_connected
        if user.value == "admin" and pwd.value == "1234":
            admin_connected = True
            page.clean()
            page.add(dashboard(page))
        else:
            msg.value = "❌ Identifiants incorrects"
            page.update()

    return ft.Column(
        [
            ft.Text("ADMIN LOGIN"),
            user,
            pwd,
            ft.ElevatedButton("Login", on_click=login),
            msg
        ]
    )

# ---------------- DASHBOARD ----------------
def dashboard(page):

    if not admin_connected:
        return ft.Column([
            ft.Text("❌ Accès refusé"),
            ft.ElevatedButton("Retour", on_click=lambda e: (page.clean(), page.add(home(page))))
        ])

    cursor.execute("SELECT * FROM etudiants")
    data = cursor.fetchall()

    rows = []

    for d in data:
        sid = d[0]

        rows.append(
            ft.DataRow(
                cells=[
                    ft.DataCell(ft.Text(d[1])),
                    ft.DataCell(ft.Text(d[2])),
                    ft.DataCell(ft.Text(d[3])),
                    ft.DataCell(ft.Text(d[4])),
                    ft.DataCell(ft.Text(d[5])),
                    ft.DataCell(ft.Text(d[6])),
                    ft.DataCell(ft.Text(d[7])),
                    ft.DataCell(
                        ft.ElevatedButton(
                            "Supprimer",
                            on_click=lambda e, sid=sid: (
                                cursor.execute("DELETE FROM etudiants WHERE id=?", (sid,)),
                                conn.commit(),
                                page.clean(),
                                page.add(dashboard(page))
                            )
                        )
                    )
                ]
            )
        )

    return ft.Column(
        [
            ft.Text("📊 DASHBOARD ADMIN"),
            ft.DataTable(
                columns=[
                    ft.DataColumn(ft.Text("Nom")),
                    ft.DataColumn(ft.Text("Prénom")),
                    ft.DataColumn(ft.Text("Matricule")),
                    ft.DataColumn(ft.Text("Niveau")),
                    ft.DataColumn(ft.Text("Filière")),
                    ft.DataColumn(ft.Text("Faculté")),
                    ft.DataColumn(ft.Text("Année")),
                    ft.DataColumn(ft.Text("Action")),
                ],
                rows=rows
            ),
            ft.ElevatedButton("Retour", on_click=lambda e: (page.clean(), page.add(home(page))))
        ]
    )

# ---------------- MAIN ----------------
def main(page: ft.Page):
    page.title = "UY1 SYSTEM"
    page.add(home(page))

# ---------------- RENDER CONFIG ----------------
port = int(os.environ.get("PORT", 8000))

ft.app(
    target=main,
    view=ft.AppView.WEB_BROWSER,
    port=port
)
