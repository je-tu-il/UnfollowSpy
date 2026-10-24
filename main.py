#!/usr/bin/env python3
"""
UnfollowSpy (GhostTrack) — Analyseur d'abonnements Instagram 100% Hors-Ligne & Privé
Identifiez qui ne vous suit pas en retour et qui vous ne suivez pas, sans mot de passe ni risque de ban.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from bs4 import BeautifulSoup
import webbrowser
import os
import sys
import json
import csv
import sv_ttk


# ===========================
# --- UTILITAIRES SYSTEME ---
# ===========================

def get_app_path():
    """
    Retourne le dossier où se trouve l'exécutable.
    Permet de garder le fichier whitelist.txt à côté du .exe
    """
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    else:
        return os.path.dirname(os.path.abspath(__file__))


WHITELIST_FILE = os.path.join(get_app_path(), "whitelist.txt")


# ===========================
# --- LOGIQUE MÉTIER ---
# ===========================

def load_whitelist():
    if not os.path.exists(WHITELIST_FILE):
        return set()
    try:
        with open(WHITELIST_FILE, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except Exception:
        return set()


def save_whitelist(whitelist_set):
    try:
        with open(WHITELIST_FILE, "w", encoding="utf-8") as f:
            for name in whitelist_set:
                f.write(f"{name}\n")
    except Exception as e:
        messagebox.showerror("Erreur Sauvegarde", f"Impossible de sauvegarder la whitelist :\n{e}")


def extract_data(file_path):
    data_map = {}
    base_url = "https://www.instagram.com"

    if not os.path.exists(file_path):
        return {}

    try:
        # JSON Parsing
        if file_path.lower().endswith(".json"):
            with open(file_path, "r", encoding="utf-8") as f:
                json_data = json.load(f)

            def find_values(obj):
                if isinstance(obj, dict):
                    for k, v in obj.items():
                        if k == "value":
                            yield v
                        elif isinstance(v, (dict, list)):
                            yield from find_values(v)
                elif isinstance(obj, list):
                    for item in obj:
                        yield from find_values(item)

            for username in find_values(json_data):
                if username:
                    data_map[username] = f"{base_url}/{username}/"

        # HTML Parsing
        else:
            with open(file_path, "r", encoding="utf-8") as f:
                raw = f.read()
            soup = BeautifulSoup(raw, "html.parser")

            for a in soup.find_all("a"):
                href = a.get("href")
                if href:
                    parts = href.strip("/").split("/")
                    if parts:
                        username = parts[-1]
                        if username and username != "_u":
                            data_map[username] = f"{base_url}/{username}/"

    except Exception as e:
        print(f"Erreur de parsing sur {file_path}: {e}")
        return {}

    return data_map


# ===========================
# --- INTERFACE GRAPHIQUE ---
# ===========================

class InstaAnalyzerApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("UnfollowSpy (GhostTrack) — Instagram Analyzer")
        self.geometry("1000x850")
        self.minsize(900, 700)

        try:
            sv_ttk.set_theme("dark")
        except Exception:
            pass

        self.whitelist = load_whitelist()
        self.full_nfb_results = []
        self.full_idf_results = []
        self.current_tab = "nfb"
        self.whitelist_window = None

        self.configure_styles()

        self.path_followers = tk.StringVar()
        self.path_following = tk.StringVar()
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search_change)

        self.stats_var = tk.StringVar(value="En attente de fichiers...")
        self.status_var = tk.StringVar(value="Prêt.")

        self.build_ui()

    def configure_styles(self):
        style = ttk.Style(self)
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", rowheight=30, font=("Segoe UI", 10))
        style.configure("Action.TButton", font=("Segoe UI", 12, "bold"))
        style.configure("File.TButton", font=("Segoe UI", 9))

    def build_ui(self):
        main = ttk.Frame(self, padding=25)
        main.pack(fill="both", expand=True)

        # HEADER
        header_frame = ttk.Frame(main)
        header_frame.pack(fill="x", pady=(0, 20))

        ttk.Label(header_frame, text="GhostTrack / UnfollowSpy", font=("Segoe UI", 22, "bold")).pack(side="left")

        # STATISTIQUES
        stats_frame = ttk.LabelFrame(header_frame, text=" Statistiques ", padding=(15, 5))
        stats_frame.pack(side="right")
        ttk.Label(stats_frame, textvariable=self.stats_var, font=("Segoe UI", 11, "bold"), foreground="#00d1b2").pack()

        # IMPORTATION
        files_frame = ttk.LabelFrame(main, text=" 1. Importation des fichiers Instagram (JSON ou HTML) ", padding=15)
        files_frame.pack(fill="x", pady=(0, 20))
        files_frame.columnconfigure(1, weight=1)

        ttk.Label(files_frame, text="Fichier Followers :").grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(files_frame, textvariable=self.path_followers).grid(row=0, column=1, sticky="ew", padx=5, ipady=3)
        ttk.Button(files_frame, text="📁 Parcourir", style="File.TButton", command=self.select_followers).grid(
            row=0, column=2, padx=(5, 0), ipadx=10
        )

        ttk.Label(files_frame, text="Fichier Following :").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        ttk.Entry(files_frame, textvariable=self.path_following).grid(
            row=1, column=1, sticky="ew", padx=5, pady=(10, 0), ipady=3
        )
        ttk.Button(files_frame, text="📁 Parcourir", style="File.TButton", command=self.select_following).grid(
            row=1, column=2, padx=(5, 0), pady=(10, 0), ipadx=10
        )

        # BOUTON ANALYSE
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill="x", pady=(0, 20))

        self.btn_run = ttk.Button(
            btn_frame,
            text="🚀 LANCER L'ANALYSE COMPLÈTE",
            style="Accent.TButton",
            cursor="hand2",
            command=self.run_analysis,
        )
        self.btn_run.pack(fill="x", ipady=10)

        # OUTILS
        tools_frame = ttk.Frame(main)
        tools_frame.pack(fill="x", pady=(0, 10))

        search_frame = ttk.Frame(tools_frame)
        search_frame.pack(side="left", fill="x", expand=True)
        ttk.Label(search_frame, text="🔍 Filtrer : ").pack(side="left")
        ttk.Entry(search_frame, textvariable=self.search_var).pack(side="left", fill="x", expand=True, padx=5)

        ttk.Button(tools_frame, text="🛡️ Gérer Whitelist", command=self.open_whitelist_manager).pack(side="right", padx=5)
        ttk.Button(tools_frame, text="💾 Exporter CSV", command=self.export_csv).pack(side="right", padx=5)

        # RESULTATS
        self.notebook = ttk.Notebook(main)
        self.notebook.pack(fill="both", expand=True)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_change)

        self.tab_nfb = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_nfb, text=" Ils ne me suivent pas ")
        self.tree_nfb = self.create_tree(self.tab_nfb)

        self.tab_idf = ttk.Frame(self.notebook)
        self.notebook.add(self.tab_idf, text=" Je ne suis pas en retour ")
        self.tree_idf = self.create_tree(self.tab_idf)

        # STATUS BAR
        status = ttk.Label(self, textvariable=self.status_var, relief=tk.SUNKEN, anchor="w", padding=(10, 5))
        status.pack(side="bottom", fill="x")

    def create_tree(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, pady=5)

        scroll = ttk.Scrollbar(frame, orient=tk.VERTICAL)
        cols = ("Pseudo", "Lien")
        tree = ttk.Treeview(frame, columns=cols, show="headings", yscrollcommand=scroll.set)
        scroll.config(command=tree.yview)

        tree.heading("Pseudo", text="Pseudo", anchor="w")
        tree.heading("Lien", text="Lien Profil", anchor="w")
        tree.column("Pseudo", width=250, anchor="w")
        tree.column("Lien", width=550, anchor="w")

        tree.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        tree.bind("<Double-1>", self.on_double_click)
        tree.bind("<Button-3>", self.show_context_menu)
        tree.bind("<Button-2>", self.show_context_menu)

        return tree

    # --- LOGIQUE ---

    def select_followers(self):
        f = filedialog.askopenfilename(filetypes=[("Données Instagram", "*.html *.json"), ("Tous les fichiers", "*.*")])
        if f:
            self.path_followers.set(f)

    def select_following(self):
        f = filedialog.askopenfilename(filetypes=[("Données Instagram", "*.html *.json"), ("Tous les fichiers", "*.*")])
        if f:
            self.path_following.set(f)

    def run_analysis(self):
        f1, f2 = self.path_followers.get(), self.path_following.get()
        if not (os.path.exists(f1) and os.path.exists(f2)):
            messagebox.showerror("Erreur", "Veuillez sélectionner les fichiers followers et following valides.")
            return

        self.config(cursor="watch")
        self.btn_run.config(state="disabled")
        self.status_var.set("Analyse en cours...")
        self.update()

        try:
            followers_map = extract_data(f1)
            following_map = extract_data(f2)

            self.full_nfb_results = [
                (u, link)
                for u, link in following_map.items()
                if u not in followers_map and u not in self.whitelist
            ]
            self.full_nfb_results.sort(key=lambda x: x[0].lower())

            self.full_idf_results = [
                (u, link)
                for u, link in followers_map.items()
                if u not in following_map and u not in self.whitelist
            ]
            self.full_idf_results.sort(key=lambda x: x[0].lower())

            total_flw = len(followers_map)
            total_flg = len(following_map)
            count_nfb = len(self.full_nfb_results)
            count_idf = len(self.full_idf_results)

            self.stats_var.set(
                f"Abonnés: {total_flw} | Abonnements: {total_flg}\n"
                f"Ne suivent pas: {count_nfb} | Non suivis: {count_idf}"
            )

            self.apply_search_filter()
            self.status_var.set("Analyse terminée avec succès.")

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur critique lors de l'analyse :\n{e}")
            self.status_var.set("Erreur.")
        finally:
            self.config(cursor="")
            self.btn_run.config(state="normal")

    def apply_search_filter(self):
        query = self.search_var.get().lower()

        tree = self.tree_nfb if self.current_tab == "nfb" else self.tree_idf
        data = self.full_nfb_results if self.current_tab == "nfb" else self.full_idf_results

        tree.delete(*tree.get_children())
        for u, link in data:
            if query in u.lower():
                tree.insert("", "end", values=(u, link))

    def on_search_change(self, *args):
        self.apply_search_filter()

    def on_tab_change(self, event):
        idx = self.notebook.index(self.notebook.select())
        self.current_tab = "nfb" if idx == 0 else "idf"
        self.apply_search_filter()

    def on_double_click(self, event):
        tree = self.tree_nfb if self.current_tab == "nfb" else self.tree_idf
        item = tree.identify_row(event.y)
        if item:
            url = tree.item(item, "values")[1]
            webbrowser.open(url)

    def show_context_menu(self, event):
        tree = self.tree_nfb if self.current_tab == "nfb" else self.tree_idf
        item = tree.identify_row(event.y)
        if not item:
            return

        tree.selection_set(item)
        username = tree.item(item, "values")[0]
        url = tree.item(item, "values")[1]

        menu = tk.Menu(self, tearoff=0)
        menu.add_command(label=f"Ouvrir @{username} sur Instagram", command=lambda: webbrowser.open(url))
        menu.add_command(label="Copier le pseudo", command=lambda: self.copy_to_clipboard(username))
        menu.add_separator()
        menu.add_command(label="🛡️ Ajouter à la Whitelist", command=lambda: self.add_to_whitelist(username))

        menu.tk_popup(event.x_root, event.y_root)

    def copy_to_clipboard(self, text):
        self.clipboard_clear()
        self.clipboard_append(text)
        self.status_var.set(f"'{text}' copié dans le presse-papiers.")

    def add_to_whitelist(self, username):
        self.whitelist.add(username)
        save_whitelist(self.whitelist)
        self.full_nfb_results = [x for x in self.full_nfb_results if x[0] != username]
        self.full_idf_results = [x for x in self.full_idf_results if x[0] != username]
        self.apply_search_filter()
        self.status_var.set(f"@{username} ajouté à la Whitelist.")

    def open_whitelist_manager(self):
        if self.whitelist_window and self.whitelist_window.winfo_exists():
            self.whitelist_window.lift()
            return

        self.whitelist_window = tk.Toplevel(self)
        self.whitelist_window.title("Gestion de la Whitelist")
        self.whitelist_window.geometry("400x500")

        frame = ttk.Frame(self.whitelist_window, padding=15)
        frame.pack(fill="both", expand=True)

        ttk.Label(frame, text="Pseudos ignorés :", font=("Segoe UI", 11, "bold")).pack(anchor="w")

        listbox_frame = ttk.Frame(frame)
        listbox_frame.pack(fill="both", expand=True, pady=10)

        scroll = ttk.Scrollbar(listbox_frame, orient=tk.VERTICAL)
        listbox = tk.Listbox(listbox_frame, yscrollcommand=scroll.set, bg="#1e1e1e", fg="white", font=("Segoe UI", 10))
        scroll.config(command=listbox.yview)

        listbox.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")

        for u in sorted(self.whitelist):
            listbox.insert("end", u)

        def remove_selected():
            sel = listbox.curselection()
            if sel:
                val = listbox.get(sel[0])
                self.whitelist.remove(val)
                save_whitelist(self.whitelist)
                listbox.delete(sel[0])
                self.status_var.set(f"@{val} retiré de la Whitelist.")
                self.run_analysis()

        ttk.Button(frame, text="Retirer de la Whitelist", command=remove_selected).pack(fill="x")

    def export_csv(self):
        data = self.full_nfb_results if self.current_tab == "nfb" else self.full_idf_results
        if not data:
            messagebox.showinfo("Export", "Aucune donnée à exporter.")
            return

        tab_name = "ne_me_suivent_pas" if self.current_tab == "nfb" else "non_suivis_en_retour"
        path = filedialog.asksaveasfilename(
            defaultextension=".csv",
            initialfile=f"instagram_{tab_name}.csv",
            filetypes=[("Fichier CSV", "*.csv")],
        )
        if not path:
            return

        try:
            with open(path, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(["Pseudo", "Lien Instagram"])
                writer.writerows(data)
            messagebox.showinfo("Export Réussi", f"Fichier CSV enregistré avec succès :\n{path}")
        except Exception as e:
            messagebox.showerror("Erreur Export", f"Impossible d'enregistrer le fichier CSV :\n{e}")


def main():
    app = InstaAnalyzerApp()
    app.mainloop()


if __name__ == "__main__":
    main()
