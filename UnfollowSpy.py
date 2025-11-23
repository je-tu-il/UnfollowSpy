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
    if getattr(sys, 'frozen', False):
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
                        if k == "value": yield v
                        elif isinstance(v, (dict, list)): yield from find_values(v)
                elif isinstance(obj, list):
                    for item in obj: yield from find_values(item)

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

        self.title("GhostTrack - Instagram Analyzer") # J'ai mis un des noms proposés
        self.geometry("1000x850")
        self.minsize(900, 700)
        
        sv_ttk.set_theme("dark")
        
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
        
        # Texte par défaut
        self.stats_var = tk.StringVar(value="En attente de fichiers...")
        self.status_var = tk.StringVar(value="Prêt.")

        self.build_ui()

    def configure_styles(self):
        style = ttk.Style(self)
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'))
        style.configure("Treeview", rowheight=30, font=('Segoe UI', 10))
        style.configure('Action.TButton', font=('Segoe UI', 12, 'bold'))
        style.configure('File.TButton', font=('Segoe UI', 9))

    def build_ui(self):
        main = ttk.Frame(self, padding=25)
        main.pack(fill="both", expand=True)

        # HEADER
        header_frame = ttk.Frame(main)
        header_frame.pack(fill="x", pady=(0, 20))
        
        ttk.Label(header_frame, text="GhostTrack", font=("Segoe UI", 22, "bold")).pack(side="left")
        
        # BOITE STATISTIQUES (Sans Ratio)
        stats_frame = ttk.LabelFrame(header_frame, text=" Statistiques ", padding=(15, 5))
        stats_frame.pack(side="right")
        ttk.Label(stats_frame, textvariable=self.stats_var, font=("Segoe UI", 11, "bold"), foreground="#00d1b2").pack()

        # IMPORTATION
        files_frame = ttk.LabelFrame(main, text=" 1. Importation des données ", padding=15)
        files_frame.pack(fill="x", pady=(0, 20))
        files_frame.columnconfigure(1, weight=1)

        ttk.Label(files_frame, text="Fichier Followers :").grid(row=0, column=0, sticky="w", padx=(0, 10))
        ttk.Entry(files_frame, textvariable=self.path_followers).grid(row=0, column=1, sticky="ew", padx=5, ipady=3)
        ttk.Button(files_frame, text="📁 Parcourir", style="File.TButton", command=self.select_followers).grid(row=0, column=2, padx=(5, 0), ipadx=10)

        ttk.Label(files_frame, text="Fichier Following :").grid(row=1, column=0, sticky="w", padx=(0, 10), pady=(10, 0))
        ttk.Entry(files_frame, textvariable=self.path_following).grid(row=1, column=1, sticky="ew", padx=5, pady=(10, 0), ipady=3)
        ttk.Button(files_frame, text="📁 Parcourir", style="File.TButton", command=self.select_following).grid(row=1, column=2, padx=(5, 0), pady=(10, 0), ipadx=10)

        # BOUTON ANALYSE
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill="x", pady=(0, 20))
        
        self.btn_run = ttk.Button(
            btn_frame, 
            text="🚀 LANCER L'ANALYSE COMPLÈTE", 
            style="Accent.TButton", 
            cursor="hand2",
            command=self.run_analysis
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
        f = filedialog.askopenfilename(filetypes=[("Data files", "*.html *.json")], initialfile="followers_1")
        if f: self.path_followers.set(f)

    def select_following(self):
        f = filedialog.askopenfilename(filetypes=[("Data files", "*.html *.json")], initialfile="following")
        if f: self.path_following.set(f)

    def run_analysis(self):
        f1, f2 = self.path_followers.get(), self.path_following.get()
        if not (os.path.exists(f1) and os.path.exists(f2)):
            messagebox.showerror("Erreur", "Veuillez sélectionner les fichiers followers et following.")
            return

        self.config(cursor="watch")
        self.btn_run.config(state="disabled")
        self.status_var.set("Analyse en cours...")
        self.update()

        try:
            followers_map = extract_data(f1)
            following_map = extract_data(f2)
            
            # --- MODIFICATION ICI : CALCULS SANS RATIO ---
            nb_followers = len(followers_map)
            nb_following = len(following_map)
            
            # Mise à jour du texte sans le ratio
            self.stats_var.set(f"{nb_followers} Abonnés  |  {nb_following} Abonnements")

            # Comparaison
            followers_set = set(followers_map.keys())
            following_set = set(following_map.keys())

            # 1. NFB
            diff_nfb = following_set - followers_set
            self.full_nfb_results = []
            for u in diff_nfb:
                if u not in self.whitelist:
                    self.full_nfb_results.append((u, following_map[u]))
            self.full_nfb_results.sort(key=lambda x: x[0].lower())

            # 2. IDF
            diff_idf = followers_set - following_set
            self.full_idf_results = []
            for u in diff_idf:
                if u not in self.whitelist:
                    self.full_idf_results.append((u, followers_map[u]))
            self.full_idf_results.sort(key=lambda x: x[0].lower())

            # Update UI
            self.update_tree_display(self.tree_nfb, self.full_nfb_results)
            self.update_tree_display(self.tree_idf, self.full_idf_results)

            self.notebook.tab(self.tab_nfb, text=f" Ils ne me suivent pas ({len(self.full_nfb_results)}) ")
            self.notebook.tab(self.tab_idf, text=f" Je ne suis pas en retour ({len(self.full_idf_results)}) ")
            
            self.status_var.set("Analyse terminée avec succès.")

        except Exception as e:
            messagebox.showerror("Erreur", str(e))
        finally:
            self.config(cursor="")
            self.btn_run.config(state="normal")

    def update_tree_display(self, tree, data):
        search_term = self.search_var.get().lower()
        for item in tree.get_children():
            tree.delete(item)
        for pseudo, lien in data:
            if search_term in pseudo.lower():
                tree.insert("", "end", values=(pseudo, lien))

    def on_search_change(self, *args):
        self.update_tree_display(self.tree_nfb, self.full_nfb_results)
        self.update_tree_display(self.tree_idf, self.full_idf_results)

    def on_tab_change(self, event):
        tab_id = self.notebook.index(self.notebook.select())
        self.current_tab = "nfb" if tab_id == 0 else "idf"

    def on_double_click(self, event):
        tree = event.widget
        sel = tree.selection()
        if sel:
            link = tree.item(sel[0], "values")[1]
            webbrowser.open(link)

    # --- WHITELIST & MENU ---

    def show_context_menu(self, event):
        tree = event.widget
        item = tree.identify_row(event.y)
        if item:
            tree.selection_set(item)
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(label="🚫 Ignorer ce compte (Whitelist)", command=lambda: self.add_to_whitelist(tree))
            menu.post(event.x_root, event.y_root)

    def add_to_whitelist(self, tree):
        sel = tree.selection()
        if sel:
            pseudo = tree.item(sel[0], "values")[0]
            if messagebox.askyesno("Whitelist", f"Cacher {pseudo} des futurs résultats ?"):
                self.whitelist.add(pseudo)
                save_whitelist(self.whitelist)
                self.run_analysis()

    def open_whitelist_manager(self):
        if self.whitelist_window is not None and self.whitelist_window.winfo_exists():
            self.whitelist_window.lift()
            self.whitelist_window.focus()
            return

        self.whitelist_window = tk.Toplevel(self)
        self.whitelist_window.title("Gérer la Whitelist")
        self.whitelist_window.geometry("400x500")
        
        ttk.Label(self.whitelist_window, text="Comptes ignorés", font=("Segoe UI", 12, "bold")).pack(pady=10)
        
        lb = tk.Listbox(self.whitelist_window, bg="#2b2b2b", fg="white", font=("Segoe UI", 11), relief="flat")
        lb.pack(fill="both", expand=True, padx=15, pady=5)
        
        sorted_list = sorted(self.whitelist, key=str.lower)
        for name in sorted_list:
            lb.insert(tk.END, name)
            
        def remove_item(event):
            sel = lb.curselection()
            if sel:
                name = lb.get(sel[0])
                if messagebox.askyesno("Retirer", f"Retirer {name} de la liste blanche ?"):
                    self.whitelist.remove(name)
                    save_whitelist(self.whitelist)
                    lb.delete(sel[0])
                    if self.full_nfb_results or self.full_idf_results:
                        self.run_analysis()

        lb.bind("<Double-1>", remove_item)

    # --- EXPORT ---

    def export_csv(self):
        if self.current_tab == "nfb":
            data = self.full_nfb_results
            default_name = "GhostTrack_NonFollowers.csv"
        else:
            data = self.full_idf_results
            default_name = "GhostTrack_NotFollowingBack.csv"
            
        if not data:
            messagebox.showinfo("Export", "Aucune donnée à exporter.")
            return

        f = filedialog.asksaveasfilename(defaultextension=".csv", initialfile=default_name, filetypes=[("CSV", "*.csv")])
        if f:
            try:
                search_term = self.search_var.get().lower()
                filtered_data = [row for row in data if search_term in row[0].lower()]

                with open(f, "w", newline="", encoding="utf-8") as csvfile:
                    writer = csv.writer(csvfile)
                    writer.writerow(["Pseudo", "Lien Profil"])
                    writer.writerows(filtered_data)
                messagebox.showinfo("Succès", "Exportation réussie !")
            except Exception as e:
                messagebox.showerror("Erreur Export", str(e))

if __name__ == "__main__":
    app = InstaAnalyzerApp()
    app.mainloop()
