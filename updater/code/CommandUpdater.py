import os
import zipfile
import requests
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext

class ZipUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Upload de Comandos")
        self.root.geometry("500x400")

        # Pasta de comandos
        tk.Label(root, text="Pasta de Comandos:").pack(anchor="w", padx=10, pady=2)
        self.folder_var = tk.StringVar()
        tk.Entry(root, textvariable=self.folder_var, width=50).pack(padx=10)
        tk.Button(root, text="Selecionar Pasta", command=self.select_folder).pack(padx=10, pady=2)

        # Nome do zip
        tk.Label(root, text="Nome do ZIP:").pack(anchor="w", padx=10, pady=2)
        self.zip_var = tk.StringVar(value="commands_update.zip")
        tk.Entry(root, textvariable=self.zip_var, width=50).pack(padx=10)

        # URL da API
        tk.Label(root, text="URL da API:").pack(anchor="w", padx=10, pady=2)
        self.url_var = tk.StringVar(value="http://localhost:3000/upload-commands")
        tk.Entry(root, textvariable=self.url_var, width=50).pack(padx=10)

        # Botão de upload
        tk.Button(root, text="Gerar e Enviar ZIP", command=self.generate_and_upload).pack(padx=10, pady=10)

        # Log
        tk.Label(root, text="Log:").pack(anchor="w", padx=10)
        self.log = scrolledtext.ScrolledText(root, width=60, height=10)
        self.log.pack(padx=10, pady=5)

    def log_msg(self, msg):
        self.log.insert(tk.END, msg + "\n")
        self.log.see(tk.END)
        self.root.update()

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.folder_var.set(folder)

    def zip_folder(self, folder_path, zip_path):
        with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(folder_path):
                for file in files:
                    full_path = os.path.join(root, file)
                    rel_path = os.path.relpath(full_path, folder_path)
                    zipf.write(full_path, arcname=rel_path)
        self.log_msg(f"[INFO] Zip criado: {zip_path}")

    def upload_zip(self, zip_path, upload_url):
        try:
            with open(zip_path, "rb") as f:
                files = {"commands_zip": (os.path.basename(zip_path), f, "application/zip")}
                response = requests.post(upload_url, files=files)
            if response.status_code == 200:
                self.log_msg(f"[INFO] Upload concluído: {response.json()}")
            else:
                self.log_msg(f"[ERRO] Falha no upload: {response.status_code} {response.text}")
        except Exception as e:
            self.log_msg(f"[ERRO] Exceção no upload: {e}")

    def generate_and_upload(self):
        folder = self.folder_var.get()
        zip_name = self.zip_var.get()
        url = self.url_var.get()

        if not os.path.exists(folder):
            messagebox.showerror("Erro", f"Pasta '{folder}' não encontrada")
            return

        self.zip_folder(folder, zip_name)
        self.upload_zip(zip_name, url)

if __name__ == "__main__":
    root = tk.Tk()
    app = ZipUploaderApp(root)
    root.mainloop()
