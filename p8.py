import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime
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

def insert_data(nama, bio, fis, ing, prediksi):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO nilai_siswa (nama_siswa, biologi, fisika, inggris, prediksi_fakultas)
        VALUES (?, ?, ?, ?, ?)
    ''', (nama, bio, fis, ing, prediksi))
    conn.commit()
    conn.close()

def update_data(id_val, nama, bio, fis, ing, prediksi):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE nilai_siswa
        SET nama_siswa=?, biologi=?, fisika=?, inggris=?, prediksi_fakultas=?
        WHERE id=?
    ''', (nama, bio, fis, ing, prediksi, id_val))
    conn.commit()
    conn.close()

def delete_data(id_val):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM nilai_siswa WHERE id=?', (id_val,))
    conn.commit()
    conn.close()

def fetch_all():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT id, nama_siswa, biologi, fisika, inggris, prediksi_fakultas FROM nilai_siswa ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    return rows

def predict_fakultas(biologi, fisika, inggris):
    if biologi > fisika and biologi > inggris:
        return "Kedokteran"
    elif fisika > biologi and fisika > inggris:
        return "Teknik"
    elif inggris > biologi and inggris > fisika:
        return "Bahasa"
    else:
        max_val = max(biologi, fisika, inggris)
        if biologi == max_val:
            return "Kedokteran"
        elif fisika == max_val:
            return "Teknik"
        else:
            return "Bahasa"

class NilaiApp:
    def __init__(self, root):
        self.root = root
        root.title('Input Nilai Siswa - SQLite')
        root.geometry('900x520')
        root.minsize(800, 480)

        style = ttk.Style()
        try:
            style.theme_use('clam')
        except Exception:
            pass

        style.configure('TLabel', font=('Segoe UI', 10))
        style.configure('TButton', font=('Segoe UI', 10), padding=6)
        style.configure('Header.TLabel', font=('Segoe UI', 12, 'bold'))
        style.configure('Treeview.Heading', font=('Segoe UI', 11, 'bold'))
        style.configure('Treeview', font=('Segoe UI', 10))

        frm_left = ttk.LabelFrame(root, text='Form Input', padding=(12, 12))
        frm_left.grid(row=0, column=0, sticky='nw', padx=12, pady=12)

        frm_right = ttk.LabelFrame(root, text='Data Tersimpan', padding=(8, 8))
        frm_right.grid(row=0, column=1, sticky='nsew', padx=12, pady=12)

        ttk.Label(frm_left, text='Nama Siswa:', style='Header.TLabel').grid(row=0, column=0, sticky='w')
        self.entry_nama = ttk.Entry(frm_left, width=34)
        self.entry_nama.grid(row=1, column=0, pady=6, sticky='w')

        lbl_nilai = ttk.Label(frm_left, text='Nilai (0-100):', style='Header.TLabel')
        lbl_nilai.grid(row=2, column=0, sticky='w', pady=(8, 0))

        inner = ttk.Frame(frm_left)
        inner.grid(row=3, column=0, sticky='w')
        ttk.Label(inner, text='Biologi').grid(row=0, column=0, padx=(0, 6))
        self.entry_bio = ttk.Entry(inner, width=8)
        self.entry_bio.grid(row=0, column=1, padx=(0, 12))

        ttk.Label(inner, text='Fisika').grid(row=0, column=2, padx=(0, 6))
        self.entry_fis = ttk.Entry(inner, width=8)
        self.entry_fis.grid(row=0, column=3, padx=(0, 12))

        ttk.Label(inner, text='Inggris').grid(row=0, column=4, padx=(0, 6))
        self.entry_ing = ttk.Entry(inner, width=8)
        self.entry_ing.grid(row=0, column=5)

        # tombol CRUD
        btn_frame = ttk.Frame(frm_left)
        btn_frame.grid(row=5, column=0, pady=12, sticky='w')

        self.btn_submit = ttk.Button(btn_frame, text='Submit', command=self.on_submit)
        self.btn_submit.grid(row=0, column=0, padx=(0, 8))

        self.btn_update = ttk.Button(btn_frame, text='Update', command=self.on_update)
        self.btn_update.grid(row=0, column=1, padx=(0, 8))

        self.btn_delete = ttk.Button(btn_frame, text='Delete', command=self.on_delete)
        self.btn_delete.grid(row=0, column=2, padx=(0, 8))

        self.btn_clear = ttk.Button(btn_frame, text='Clear', command=self.clear_form)
        self.btn_clear.grid(row=0, column=3, padx=(0, 8))

        columns = ('id', 'nama', 'biologi', 'fisika', 'inggris', 'prediksi')
        self.tree = ttk.Treeview(frm_right, columns=columns, show='headings')
        for col, hd in zip(columns, ['ID', 'Nama', 'Biologi', 'Fisika', 'Inggris', 'Prediksi Fakultas']):
            self.tree.heading(col, text=hd)

        self.tree.column('id', width=40, anchor='center')
        self.tree.column('nama', width=180, anchor='w')
        self.tree.column('biologi', width=80, anchor='center')
        self.tree.column('fisika', width=80, anchor='center')
        self.tree.column('inggris', width=80, anchor='center')
        self.tree.column('prediksi', width=140, anchor='center')

        self.tree.bind("<<TreeviewSelect>>", self.on_row_select)

        vsb = ttk.Scrollbar(frm_right, orient='vertical', command=self.tree.yview)
        hsb = ttk.Scrollbar(frm_right, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=vsb.set, xscroll=hsb.set)
        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        frm_right.grid_rowconfigure(0, weight=1)
        frm_right.grid_columnconfigure(0, weight=1)

        self.summary = ttk.Label(root, text='', anchor='w')
        self.summary.grid(row=1, column=0, columnspan=2, sticky='we', padx=14)

        self.selected_id = None
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
            messagebox.showwarning('Validasi', 'Masukkan nilai numerik.')
            return False
        for v in (bio, fis, ing):
            if v < 0 or v > 100:
                messagebox.showwarning('Validasi', 'Nilai harus 0-100.')
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

        insert_data(nama, bio, fis, ing, prediksi)
        messagebox.showinfo('Sukses', f'Data tersimpan. Prediksi: {prediksi}')
        self.clear_form()
        self.load_table()

    def on_update(self):
        if self.selected_id is None:
            messagebox.showwarning("Update", "Pilih data dulu.")
            return

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

        update_data(self.selected_id, nama, bio, fis, ing, prediksi)
        messagebox.showinfo("Update", "Data berhasil diupdate.")
        self.clear_form()
        self.load_table()

    def on_delete(self):
        if self.selected_id is None:
            messagebox.showwarning("Delete", "Pilih data dulu.")
            return

        if messagebox.askyesno("Konfirmasi", "Yakin ingin menghapus data ini?"):
            delete_data(self.selected_id)
            messagebox.showinfo("Delete", "Data berhasil dihapus.")
            self.clear_form()
            self.load_table()

    def on_row_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        values = self.tree.item(selected[0], 'values')
        self.selected_id = int(values[0])

        self.entry_nama.delete(0, tk.END)
        self.entry_nama.insert(0, values[1])

        self.entry_bio.delete(0, tk.END)
        self.entry_bio.insert(0, values[2])

        self.entry_fis.delete(0, tk.END)
        self.entry_fis.insert(0, values[3])

        self.entry_ing.delete(0, tk.END)
        self.entry_ing.insert(0, values[4])

    def load_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        rows = fetch_all()
        for r in rows:
            self.tree.insert('', tk.END, values=r)

        total = len(rows)
        counts = {'Kedokteran': 0, 'Teknik': 0, 'Bahasa': 0}
        for r in rows:
            if r[5] in counts:
                counts[r[5]] += 1

        self.summary.config(text=f'Total entri: {total} | Kedokteran: {counts["Kedokteran"]} | Teknik: {counts["Teknik"]} | Bahasa: {counts["Bahasa"]}')

    def clear_form(self):
        self.entry_nama.delete(0, tk.END)
        self.entry_bio.delete(0, tk.END)
        self.entry_fis.delete(0, tk.END)
        self.entry_ing.delete(0, tk.END)
        self.selected_id = None

if __name__ == '__main__':
    init_db()
    root = tk.Tk()
    app = NilaiApp(root)
    root.mainloop()