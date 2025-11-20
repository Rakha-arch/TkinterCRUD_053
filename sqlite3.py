import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
import csv

DB_FILE = 'nilai_siswa.db'

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS nilai_siswa (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nama_siswa TEXT NOT NULL,
            biologi REAL NOT NULL,
            fisika REAL NOT NULL,
            inggris REAL NOT NULL,
            prediksi_fakultas TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def insert_nilai(nama, bio, fisika, inggris, prediksi):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO nilai_siswa (nama, bio, fisika, inggris, prediksi)
        VALUES (?, ?, ?, ?, ?)
    ''', (nama, bio, fisika, inggris, prediksi))
    conn.commit()
    conn.close()

def fetch_all():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute('SELECT id, nilai_siswa, biologi, fisika, inggris, prediksi_fakultas FROM nilai_siswa order by id DESC')
    rows = cur.fetchall()
    conn.close()
    return rows

def predict_fakultas(biologi, fisika, inggris):
    if biologi > fisika and biologi > inggris:
        return "Fakultas Kedokteran"
    elif fisika > biologi and fisika > inggris:
        return "Fakultas Teknik"
    elif inggris > biologi and inggris > fisika:
        return "Fakultas bahasa"
    else:
        max_val = max(biologi, fisika, inggris)
        if biologi == max_val:
            return "Fakultas Kedokteran"
        elif fisika == max_val:
            return "Fakultas Teknik"
        else:
            return "Fakultas bahasa"
        
class NilaiApp:
    def __init__(self, root):
        self.root = root
        root.title("input nilai siswa - SQlite")
        root.geometry("900x520")
        root.minsize(800, 400)

        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass
        style.configure('Tlabel', font=('Segoe UI', 10,))
        style.configure('TButton', font=('Segoe UI', 10,),padding=6)
        style.configure('Header.TLabel', font=('Segoe UI', 10,'bold'))
        style.configure('treeview.Heading', font=('Segoe UI', 10,'bold'))
        style.configure('treeview', font=('Segoe UI', 10,))

        frm_left = ttk.LabelFrame(root, text='from input', padding=(12,12))
        frm_left.grid(row=0, column=1, sticky='nsew', padx=12, pady=12)
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)

        ttk.Label(frm_left, text="Nama Siswa:', style='Header.TLabel").grid(row=0, column=0, sticky='w')
        self.entry_nama = ttk.Entry(frm_left, width=30)
        self.entry_nama.grid(row=0, column=1, sticky='w', pady=6)

        lbl_nilai = ttk.Label(frm_left, text='Nilai (0-100):', style='Header.TLabel')
        lbl_nilai.grid(row=2, column=0, sticky='w', pady=(8, 0))

        inner = ttk.Frame(frm_left)
        inner.grid(row=3, column=0, sticky='w')
        ttk.Label(inner, text='Biologi').grid(row=0, column=0, padx=(0,6))
        self.entry_bio = ttk.Entry(inner, width=8)
        self.entry_bio.grid(row=0, column=1, padx=(0,12))

        ttk.Label(inner, text='Fisika').grid(row=0, column=2, padx=(0,6))
        self.entry_fis = ttk.Entry(inner, width=8)
        self.entry_fis.grid(row=0, column=3, padx=(0,12))

        ttk.Label(inner, text='Inggris').grid(row=0, column=4, padx=(0,6))
        self.entry_ing = ttk.Entry(inner, width=8)
        self.entry_ing.grid(row=0, column=5)

        # self.lbl_info = ttk.Label(frm_left, text='Isi semua kolom, lalu tekan Submit.', foreground='#333')
        # self.lbl_info.grid(row=4, column=0, pady=(8,0), sticky='w')

        btn_frame = ttk.Frame(frm_left)
        btn_frame.grid(row=5, column=0, pady=12, sticky='w')
        self.btn_submit = ttk.Button(btn_frame, text='Submit', command=self.on_submit)
        self.btn_submit.grid(row=0, column=0, padx=(0,8))

        self.btn_clear = ttk.Button(btn_frame, text='Clear', command=self.clear_form)
        self.btn_clear.grid(row=0, column=1, padx=(0,8))

        # self.btn_refresh = ttk.Button(btn_frame, text='Refresh Table', command=self.load_table)
        # self.btn_refresh.grid(row=0, column=2, padx=(0,8))

        # self.btn_export = ttk.Button(btn_frame, text='Export CSV', command=self.export_csv)
        # self.btn_export.grid(row=0, column=3)

        columns = ('id', 'nama', 'biologi', 'fisika', 'inggris', 'prediksi')
        self.tree = ttk.Treeview(frm_left, columns=columns, show='headings')
        for col, hd in zip(columns, ['ID', 'Nama', 'Biologi', 'Fisika', 'Inggris', 'Prediksi Fakultas']):
            self.tree.heading(col, text=hd)
        self.tree.column('id', width=40, anchor='center')
        self.tree.column('nama', width=180, anchor='w')
        self.tree.column('biologi', width=80, anchor='center')
        self.tree.column('fisika', width=80, anchor='center')
        self.tree.column('inggris', width=80, anchor='center')
        self.tree.column('prediksi', width=140, anchor='center')
        #self.tree.column('created', width=170, anchor='center')

        vsb = ttk.Scrollbar(frm_left, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(frm_left, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        frm_left.grid_rowconfigure(0, weight=1)
        frm_left.grid_columnconfigure(0, weight=1)

        self.summary = ttk.Label(root, text='', anchor='w')
        self.summary.grid(row=1, column=0, columnspan=2, sticky='we', padx=14)

        self.load_table()

    def validate_inputs(self, nama, bio_s, fis_s, ing_s):
        if not nama.strip():
            messagebox.showwarning('Validasi', 'Nama siswa harus diisi.')
            return False
        try:
            bio = float(bio_s)
            fis = float(fis_s)
            ing = float(ing_s)
        except ValueError:
            messagebox.showwarning('Validasi', 'Masukkan nilai numerik untuk Biologi, Fisika, dan Inggris.')
            return False
        for v in (bio, fis, ing):
            if v < 0 or v > 100:
                messagebox.showwarning('Validasi', 'Nilai harus berada di rentang 0 - 100.')
                return False
        return True
    def on_submit(self):
        nama = self.entry_nama.get()
        bio_s = self.entry_bio.get()
        fis_s = self.entry_fis.get()
        ing_s = self.entry_ing.get()

        if not self.validate_inputs(nama, bio_s, fis_s, ing_s):
            return

        bio = float(bio_s)
        fis = float(fis_s)
        ing = float(ing_s)

        prediksi = predict_fakultas(bio, fis, ing)

        insert_nilai(nama, bio, fis, ing, prediksi)
        messagebox.showinfo('Sukses', f'Data tersimpan. Prediksi: {prediksi}')
        self.clear_form()
        self.load_table()

    def load_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        rows = fetch_all()
        for r in rows:
            self.tree.insert('', tk.END, values=r)

        total = len(rows)
        counts = {'Kedokteran':0, 'Teknik':0, 'Bahasa':0}
        for r in rows:
            if r[5] in counts:
                counts[r[5]] += 1
        self.summary.config(text=f'Total entri: {total}    Kedokteran: {counts["Kedokteran"]}    Teknik: {counts["Teknik"]}    Bahasa: {counts["Bahasa"]}')

    def clear_form(self):
        self.entry_nama.delete(0, tk.END)
        self.entry_bio.delete(0, tk.END)
        self.entry_fis.delete(0, tk.END)
        self.entry_ing.delete(0, tk.END)

    def export_csv(self):
        rows = fetch_all()
        if not rows:
            messagebox.showinfo('Export CSV', 'Tidak ada data untuk diekspor.')
            return
        filename = f'nilai_siswa_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['id','nama_siswa','biologi','fisika','inggris','prediksi_fakultas'])
            writer.writerows(rows)
        messagebox.showinfo('Export CSV', f'Data berhasil diekspor ke {filename}')


if name == 'main':
    init_db()
    root = tk.Tk()
    app = NilaiApp(root)
    root.mainloop()