import flet as ft
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt


import flet as ft

def main(page: ft.Page):
    page.title = "Mon app"
    page.add(ft.Text("Hello depuis Render 🚀"))



PRIMARY = "#0D47A1"
IMAGE_BG = "https://images.unsplash.com/photo-1523580846011-d3a5bc25702b"

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

# ---------------- DATA ----------------
def get_all():
    cursor.execute("SELECT * FROM etudiants")
    return cursor.fetchall()

# ---------------- NAV ----------------
def show(page, view):
    page.clean()
    page.add(layout(page, view(page)))
    page.update()

# ---------------- BACKGROUND ----------------
def layout(page, content):
    return ft.Stack(
        expand=True,
        controls=[
            ft.Container(
                expand=True,
                content=ft.Image(src=IMAGE_BG, fit='cover')
            ),
            ft.Container(expand=True, bgcolor="rgba(0,0,0,0.65)"),
            ft.Container(expand=True, padding=20, content=content)
        ]
    )

# ---------------- HOME ----------------
def home(page):
    return ft.Column(
        [
            ft.Text("🎓 UY1 STUDENT SYSTEM", size=35, color="white", weight="bold"),
            ft.Container(height=40), 

            ft.ElevatedButton("Login Étudiant", on_click=lambda e: show(page, form)),
            ft.ElevatedButton("Admin Login", on_click=lambda e: show(page, admin)),

            ft.ElevatedButton(
                "📊 Analyser",
                bgcolor="#FF9800",
                color="white",
                on_click=lambda e: show(page, analyse)
            ),
        ],
        alignment=ft.MainAxisAlignment.CENTER,
        horizontal_alignment=ft.CrossAxisAlignment.CENTER
    )

# ---------------- FORM ----------------
def form(page):

    def f(label):
        return ft.TextField(label=label, bgcolor="white", color="black")

    nom = f("Nom")
    prenom = f("Prénom")
    matricule = f("Matricule")
    niveau = f("Niveau")
    filiere = f("Filière")
    faculte = f("Faculté")
    annee = f("Année")

    msg = ft.Text()

    def save(e):
        cursor.execute("""
            INSERT INTO etudiants VALUES (NULL,?,?,?,?,?,?,?)
        """, (
            nom.value, prenom.value, matricule.value,
            niveau.value, filiere.value, faculte.value, annee.value
        ))
        conn.commit()

        msg.value = "✅ Étudiant enregistré"
        page.snack_bar = ft.SnackBar(ft.Text("Ajout réussi ✔"))
        page.snack_bar.open = True
        page.update()

    return ft.Column(
        [
            nom, prenom, matricule,
            niveau, filiere, faculte, annee,

            ft.ElevatedButton("Enregistrer", on_click=save),
            msg,

            ft.ElevatedButton("Retour", on_click=lambda e: show(page, home))
        ]
    )

# ---------------- ADMIN ----------------
def admin(page):

    user = ft.TextField(label="Admin", bgcolor="white", color="black")
    pwd = ft.TextField(label="Password", password=True, bgcolor="white", color="black")

    msg = ft.Text()

    def login(e):
        global admin_connected
        if user.value == "admin" and pwd.value == "1234":
            admin_connected = True
            show(page, dashboard)
        else:
            msg.value = "❌ Identifiants incorrects"
            page.update()

    return ft.Column(
        [
            ft.Text("ADMIN LOGIN", size=25, color="white"),
            user,
            pwd,
            ft.ElevatedButton("Connexion", on_click=login),
            msg
        ]
    )

# ---------------- ANALYSE ----------------
def analyse(page):

    data = get_all()

    if not data:
        return ft.Column([
            ft.Text("📊 Aucune donnée", color="white"),
            ft.ElevatedButton("Retour", on_click=lambda e: show(page, home))
        ])

    df = pd.DataFrame(data, columns=[
        "id","nom","prenom","matricule",
        "niveau","filiere","faculte","annee"
    ])

    # ✔ FORCER valeurs positives
    fac_counts = df["faculte"].value_counts().abs()

    total = fac_counts.sum()

    bars = []

    for fac, val in fac_counts.items():

        val = abs(int(val))  # ✔ sécurité totale

        # ✔ POURCENTAGE CORRIGÉ
        if total > 0:
            percent = (val / total) * 100
        else:
            percent = 0

        # ✔ clamp 0 → 100
        percent = max(0, min(percent, 100))

        bars.append(
            ft.Column([
                ft.Text(f"{fac} - {percent:.1f}%", color="white"),

                ft.Container(
                    width=350,
                    height=20,
                    bgcolor="#333",
                    border_radius=10,
                    content=ft.Container(
                        width=(percent / 100) * 350,
                        bgcolor=(
                            "#4CAF50" if percent >= 70 else
                            "#FFC107" if percent >= 40 else
                            "#F44336"
                        ),
                        border_radius=10
                    )
                ),

                ft.Text(f"{val} étudiants", color="white")
            ])
        )

    # 📈 GRAPH
    pivot = pd.crosstab(df["faculte"], df["filiere"])

    plt.figure(figsize=(8, 4))
    for col in pivot.columns:
        plt.plot(pivot.index, pivot[col], marker="o", label=col)

    plt.legend()
    plt.tight_layout()

    img_path = "graph.png"
    plt.savefig(img_path)
    plt.close()

    return ft.Column(
        [
            ft.Text("📊 ANALYSE UY1", size=28, color="white"),
            ft.Text(f"Total étudiants : {total}", color="white"),

            ft.Container(height=20),

            ft.Row(bars, wrap=True),

            ft.Container(height=20),

            ft.Text("📈 Évolution Faculté → Filière", color="white"),
            ft.Image(src=img_path, width=650),

            ft.ElevatedButton("Retour", on_click=lambda e: show(page, home))
        ]
    )

# ---------------- DASHBOARD ----------------
def dashboard(page):

    global admin_connected

    if not admin_connected:
        return ft.Column([
            ft.Text("❌ Accès refusé", color="white"),
            ft.ElevatedButton("Retour", on_click=lambda e: show(page, home))
        ])

    data = get_all()

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
                            bgcolor="red",
                            color="white",
                            on_click=lambda e, sid=sid: (
                                cursor.execute("DELETE FROM etudiants WHERE id=?", (sid,)),
                                conn.commit(),
                                show(page, dashboard)
                            )
                        )
                    )
                ]
            )
        )

    return ft.Column(
        [
            ft.Text("📊 DASHBOARD ADMIN", size=28, color="white"),
            ft.ElevatedButton("🏠 Accueil", on_click=lambda e: show(page, home)),
            ft.Container(height=10),

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
            )
        ]
    )

# ---------------- APP ----------------
def main(page: ft.Page):
    page.title = "UY1 SYSTEM"
    show(page, home)

ft.app(target=main)
