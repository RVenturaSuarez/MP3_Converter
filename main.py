import os
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from downloader import descargar_mp3

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

CALIDADES = [
    "128 kbps (ligero)",
    "192 kbps (recomendado)",
    "256 kbps (alto)",
    "320 kbps (maximo)",
]
CALIDAD_MAP = {c: c.split()[0] for c in CALIDADES}


class MP3ConverterApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("MP3 Converter")
        self.geometry("560x530")
        self.resizable(False, False)
        self._descargando = False
        self._ultimo_mp3 = None

        self._build_ui()

    def _build_ui(self):
        ctk.CTkLabel(self, text="MP3 Converter", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(20, 25))

        # --- URL ---
        url_frame = ctk.CTkFrame(self, fg_color="transparent")
        url_frame.pack(fill="x", padx=30, pady=(0, 10))
        ctk.CTkLabel(url_frame, text="URL del video", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.url_entry = ctk.CTkEntry(url_frame, placeholder_text="https://www.youtube.com/watch?v=...", height=36)
        self.url_entry.pack(fill="x", pady=(2, 0))

        # --- Carpeta ---
        folder_frame = ctk.CTkFrame(self, fg_color="transparent")
        folder_frame.pack(fill="x", padx=30, pady=(0, 10))
        ctk.CTkLabel(folder_frame, text="Guardar en", font=ctk.CTkFont(size=12)).pack(anchor="w")
        row = ctk.CTkFrame(folder_frame, fg_color="transparent")
        row.pack(fill="x", pady=(2, 0))
        self.folder_entry = ctk.CTkEntry(row, height=36)
        self.folder_entry.pack(side="left", fill="x", expand=True)
        self.folder_entry.insert(0, os.path.join(os.path.expanduser("~"), "Music"))
        ctk.CTkButton(row, text="Examinar", width=100, command=self._elegir_carpeta).pack(side="left", padx=(8, 0))

        # --- Calidad ---
        qual_frame = ctk.CTkFrame(self, fg_color="transparent")
        qual_frame.pack(fill="x", padx=30, pady=(0, 5))
        ctk.CTkLabel(qual_frame, text="Calidad", font=ctk.CTkFont(size=12)).pack(anchor="w")
        self.quality_combo = ctk.CTkComboBox(qual_frame, values=CALIDADES, state="readonly", height=32)
        self.quality_combo.set("192 kbps (recomendado)")
        self.quality_combo.pack(fill="x", pady=(2, 0))

        # --- Carátula ---
        self.thumbnail_var = ctk.BooleanVar(value=True)
        ctk.CTkCheckBox(
            self, text="Incluir caratula del video en el MP3",
            variable=self.thumbnail_var,
            font=ctk.CTkFont(size=12),
            checkbox_width=20, checkbox_height=20,
        ).pack(pady=(5, 15))

        # --- Progreso ---
        self.progress_bar = ctk.CTkProgressBar(self, height=14)
        self.progress_bar.pack(fill="x", padx=30, pady=(10, 2))
        self.progress_bar.set(0)

        self.status_label = ctk.CTkLabel(self, text="", text_color="#888888", font=ctk.CTkFont(size=11))
        self.status_label.pack()

        # --- Botón descargar ---
        self.download_btn = ctk.CTkButton(
            self, text="DESCARGAR MP3", height=46, font=ctk.CTkFont(size=15, weight="bold"),
            command=self._iniciar_descarga
        )
        self.download_btn.pack(pady=(18, 10))

        # --- Resultado ---
        self.result_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.result_frame.pack(fill="x", padx=30, pady=(5, 5))
        self.result_label = ctk.CTkLabel(self.result_frame, text="", font=ctk.CTkFont(size=12))

        self.actions_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")

    def _elegir_carpeta(self):
        path = filedialog.askdirectory(title="Seleccionar carpeta de descarga")
        if path:
            self.folder_entry.delete(0, "end")
            self.folder_entry.insert(0, path)

    def _iniciar_descarga(self):
        if self._descargando:
            return
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showwarning("Falta URL", "Pega un link de YouTube.")
            return

        output = self.folder_entry.get().strip()
        if not os.path.isdir(output):
            messagebox.showwarning("Carpeta invalida", "La carpeta de destino no existe.")
            return

        calidad = CALIDAD_MAP.get(self.quality_combo.get(), "192")
        incluir_caratula = self.thumbnail_var.get()

        self._descargando = True
        self.download_btn.configure(state="disabled", text="DESCARGANDO...")
        self.result_label.pack_forget()
        for w in self.actions_frame.winfo_children():
            w.destroy()
        self.actions_frame.pack_forget()
        self.status_label.configure(text="Iniciando descarga...", text_color="#888888")
        self.progress_bar.set(0)

        thread = threading.Thread(
            target=descargar_mp3,
            args=(url, output, calidad),
            kwargs={
                "incluir_caratula": incluir_caratula,
                "progress_callback": self._on_progress,
                "done_callback": self._on_done,
                "error_callback": self._on_error,
            },
            daemon=True,
        )
        thread.start()

    def _on_progress(self, d):
        self.after(0, self._update_progress, d)

    def _update_progress(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 1
            downloaded = d.get("downloaded_bytes", 0)
            pct = min(downloaded / total, 1.0)
            self.progress_bar.set(pct)
            speed = d.get("_speed_str", "")
            nombre = d.get("info_dict", {}).get("title", "")[:50]
            self.status_label.configure(
                text=f"Descargando: {nombre}  {int(pct*100)}%  {speed}",
                text_color="#ffffff",
            )
        elif d["status"] == "finished":
            self.progress_bar.set(1)
            self.status_label.configure(text="Convirtiendo a MP3...", text_color="#aaaaaa")

    def _on_done(self, path, title):
        self.after(0, self._finalizar_exito, path, title)

    def _finalizar_exito(self, path, title):
        self._descargando = False
        self.download_btn.configure(state="normal", text="DESCARGAR MP3")
        self.status_label.configure(text="")
        self.progress_bar.set(0)
        self._ultimo_mp3 = path

        self.result_label.configure(
            text=f"Completado: {title}.mp3",
            text_color="#4caf50",
        )
        self.result_label.pack()

        for w in self.actions_frame.winfo_children():
            w.destroy()
        ctk.CTkButton(
            self.actions_frame, text="Abrir carpeta", width=130,
            command=lambda: os.startfile(os.path.dirname(path)),
        ).pack(side="left", padx=(0, 8))
        ctk.CTkButton(
            self.actions_frame, text="Copiar ruta", width=130,
            command=lambda: self._copiar_ruta(path),
        ).pack(side="left")
        self.actions_frame.pack(pady=(4, 0))

    def _on_error(self, msg):
        self.after(0, self._finalizar_error, msg)

    def _finalizar_error(self, msg):
        self._descargando = False
        self.download_btn.configure(state="normal", text="DESCARGAR MP3")
        self.status_label.configure(text="")
        self.progress_bar.set(0)

        self.result_label.configure(text=f"Error: {msg}", text_color="#f44336")
        self.result_label.pack()
        for w in self.actions_frame.winfo_children():
            w.destroy()
        self.actions_frame.pack_forget()

    def _copiar_ruta(self, path):
        self.clipboard_clear()
        self.clipboard_append(path)
        self.result_label.configure(text="Ruta copiada al portapapeles", text_color="#4caf50")


if __name__ == "__main__":
    app = MP3ConverterApp()
    app.mainloop()
