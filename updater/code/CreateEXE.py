# builder_gui_fixed.py
import os
import re
import shutil
import subprocess
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from pathlib import Path
import time
import tempfile

class BuilderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("App Builder")
        self.root.geometry("640x500")

        # Frame de seleção de arquivo main.py
        frm = tk.Frame(root)
        frm.pack(fill="x", padx=10, pady=6)
        tk.Label(frm, text="Main script (.py):").grid(row=0, column=0, sticky="w")
        self.main_var = tk.StringVar(value="main.py")
        tk.Entry(frm, textvariable=self.main_var, width=60).grid(row=0, column=1, padx=6)
        tk.Button(frm, text="Selecionar", command=self.select_main).grid(row=0, column=2)

        # Configurações
        cfg = tk.LabelFrame(root, text="Configurações do App")
        cfg.pack(fill="x", padx=10, pady=6)
        tk.Label(cfg, text="SERVER_URL:").grid(row=0, column=0, sticky="w", padx=6, pady=4)
        self.server_var = tk.StringVar(value="http://localhost:4000/api/v1")
        tk.Entry(cfg, textvariable=self.server_var, width=60).grid(row=0, column=1, padx=6, pady=4)

        tk.Label(cfg, text="COMMANDS_DIR:").grid(row=1, column=0, sticky="w", padx=6, pady=4)
        self.cmds_var = tk.StringVar(value="commands")
        tk.Entry(cfg, textvariable=self.cmds_var, width=60).grid(row=1, column=1, padx=6, pady=4)

        tk.Label(cfg, text="DLL_DIR:").grid(row=2, column=0, sticky="w", padx=6, pady=4)
        self.dll_var = tk.StringVar(value="dll_commands")
        tk.Entry(cfg, textvariable=self.dll_var, width=60).grid(row=2, column=1, padx=6, pady=4)

        # Build options
        opts = tk.LabelFrame(root, text="Opções de Build")
        opts.pack(fill="x", padx=10, pady=6)
        tk.Label(opts, text="Nome do EXE:").grid(row=0, column=0, sticky="w", padx=6)
        self.name_var = tk.StringVar(value="CommandUpdater")
        tk.Entry(opts, textvariable=self.name_var, width=30).grid(row=0, column=1, padx=6)

        tk.Label(opts, text="Ícone (.ico) (opcional):").grid(row=1, column=0, sticky="w", padx=6, pady=6)
        self.icon_var = tk.StringVar(value="")
        tk.Entry(opts, textvariable=self.icon_var, width=40).grid(row=1, column=1, padx=6)
        tk.Button(opts, text="Selecionar", command=self.select_icon).grid(row=1, column=2)

        tk.Label(opts, text="Pasta de saída (onde ficará o EXE):").grid(row=2, column=0, sticky="w", padx=6, pady=6)
        self.outdir_var = tk.StringVar(value=str(Path.cwd()))
        tk.Entry(opts, textvariable=self.outdir_var, width=60).grid(row=2, column=1, padx=6)
        tk.Button(opts, text="Selecionar", command=self.select_outdir).grid(row=2, column=2)

        # Botões
        btns = tk.Frame(root)
        btns.pack(fill="x", padx=10, pady=6)
        self.build_btn = tk.Button(btns, text="Gerar EXE", command=self.on_build, bg="#4CAF50", fg="white")
        self.build_btn.pack(side="left", padx=6)
        tk.Button(btns, text="Limpar logs", command=self.clear_log).pack(side="left", padx=6)

        # Log
        tk.Label(root, text="Logs:").pack(anchor="w", padx=10)
        self.log = scrolledtext.ScrolledText(root, height=14)
        self.log.pack(fill="both", expand=True, padx=10, pady=6)

        # Thread control
        self.build_thread = None
        self.stop_requested = False

    # Seletores de arquivos e pastas
    def select_main(self):
        p = filedialog.askopenfilename(title="Selecionar main.py", filetypes=[("Python files","*.py"),("All files","*.*")])
        if p:
            self.main_var.set(p)

    def select_icon(self):
        p = filedialog.askopenfilename(title="Selecionar ícone (.ico)", filetypes=[("ICO files","*.ico"),("All files","*.*")])
        if p:
            self.icon_var.set(p)

    def select_outdir(self):
        p = filedialog.askdirectory(title="Selecionar pasta de saída")
        if p:
            self.outdir_var.set(p)

    # Logs
    def log_msg(self, s: str):
        ts = time.strftime("%Y-%m-%d %H:%M:%S")
        self.log.insert(tk.END, f"[{ts}] {s}\n")
        self.log.see(tk.END)
        self.root.update()

    def clear_log(self):
        self.log.delete("1.0", tk.END)

    # Botão Build
    def on_build(self):
        if self.build_thread and self.build_thread.is_alive():
            messagebox.showinfo("Info", "Já está em execução.")
            return

        main_path = self.main_var.get().strip()
        if not main_path or not Path(main_path).exists():
            messagebox.showerror("Erro", "Selecione um main.py válido.")
            return

        # Verifica PyInstaller
        try:
            subprocess.run(["pyinstaller", "--version"], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except Exception:
            if not messagebox.askyesno("PyInstaller não encontrado", "PyInstaller parece não estar instalado. Deseja continuar e tentar mesmo assim?"):
                return

        self.build_btn.config(state="disabled")
        self.stop_requested = False
        self.build_thread = threading.Thread(target=self.build_process, daemon=True)
        self.build_thread.start()

    # Processo de Build
    def build_process(self):
        try:
            main_path = Path(self.main_var.get()).resolve()
            server_url = self.server_var.get()
            commands_dir = self.cmds_var.get()
            dll_dir = self.dll_var.get()
            exe_name = self.name_var.get().strip() or "CommandUpdater"
            icon_path = Path(self.icon_var.get()).resolve() if self.icon_var.get() else None
            outdir = Path(self.outdir_var.get()).resolve()

            self.log_msg("Iniciando build...")
            tmpdir = Path(tempfile.mkdtemp(prefix="app_build_")).resolve()
            self.log_msg(f"Pasta temporária: {tmpdir}")

            # Copia arquivos do projeto para temp
            src_root = main_path.parent
            self.log_msg(f"Copiando arquivos de {src_root} → {tmpdir}")
            shutil.copytree(src_root, tmpdir, dirs_exist_ok=True,
                            ignore=shutil.ignore_patterns('__pycache__', '*.pyc', 'dist', 'build', '*.spec'))

            temp_main = tmpdir / main_path.name

            # Substitui variáveis
            code = temp_main.read_text(encoding="utf-8")
            code_new = re.sub(r'(SERVER_URL\s*=\s*)([\'"]).*?\2', rf'\1"{server_url}"', code)
            code_new = re.sub(r'(COMMANDS_DIR\s*=\s*)([\'"]).*?\2', rf'\1"{commands_dir}"', code_new)
            code_new = re.sub(r'(DLL_DIR\s*=\s*)([\'"]).*?\2', rf'\1"{dll_dir}"', code_new)

            temp_main.write_text(code_new, encoding="utf-8")
            self.log_msg("Variáveis injetadas no main temporário.")

            # Muda working dir para o temp
            cwd = os.getcwd()
            os.chdir(tmpdir)

            # Monta comando PyInstaller
            py_cmd = ["pyinstaller", "--onefile", "--noconsole", "--name", exe_name]
            if icon_path:
                py_cmd += ["--icon", str(icon_path)]
            py_cmd.append(str(temp_main.name))

            self.log_msg("Executando PyInstaller: " + " ".join(py_cmd))
            proc = subprocess.Popen(py_cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)

            for line in proc.stdout:
                self.log_msg(line.rstrip())
            proc.wait()

            if proc.returncode != 0:
                self.log_msg(f"[ERRO] PyInstaller retornou código {proc.returncode}")
                raise RuntimeError("PyInstaller falhou. Veja logs.")

            dist_exe = tmpdir / "dist" / (exe_name + ".exe")
            if not dist_exe.exists():
                self.log_msg("[ERRO] EXE não encontrado após build.")
                raise FileNotFoundError("EXE não encontrado")

            outdir.mkdir(parents=True, exist_ok=True)
            final_path = outdir / dist_exe.name
            shutil.move(str(dist_exe), str(final_path))
            self.log_msg(f"[OK] EXE criado em: {final_path}")

            # Limpeza
            os.chdir(cwd)
            shutil.rmtree(tmpdir, ignore_errors=True)
            for name in ("build", "dist"):
                p = Path(name)
                if p.exists() and p.is_dir():
                    shutil.rmtree(p, ignore_errors=True)
            spec = exe_name + ".spec"
            if Path(spec).exists():
                Path(spec).unlink()

            self.log_msg("Build finalizado com sucesso.")
            messagebox.showinfo("Sucesso", f"EXE criado: {final_path}")

        except Exception as e:
            self.log_msg(f"[EXCEPTION] {e}")
            messagebox.showerror("Erro", f"Falha no build: {e}")
        finally:
            try:
                self.build_btn.config(state="normal")
            except:
                pass

def main():
    root = tk.Tk()
    app = BuilderApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
