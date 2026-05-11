import os
import re
import threading
import customtkinter as ctk
from tkinter import filedialog, messagebox
from downloader import descargar

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

PLAYLIST_RE = re.compile(r"[&?]list=")


class TubeGetApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("TubeGet")
        self.geometry("750x640")
        self.resizable(False, False)

        self._descargando = False
        self._cancel_event = threading.Event()
        self._ultimo_mp3 = None
        self._completions_count = 0

        self._build_ui()
        self._bind_url_detection()

    # ==================================================================
    #  UI
    # ==================================================================
    def _build_ui(self):
        main = ctk.CTkFrame(self, fg_color="transparent")
        main.pack(fill="both", expand=True, padx=30, pady=10)

        ctk.CTkLabel(main, text="TubeGet", font=ctk.CTkFont(size=22, weight="bold")).pack(pady=(15, 20))

        # --- URL ---
        ctk.CTkLabel(main, text="URL del video", font=ctk.CTkFont(size=12), anchor="w").pack(fill="x")
        self.url_entry = ctk.CTkEntry(main, placeholder_text="https://www.youtube.com/watch?v=...", height=38)
        self.url_entry.pack(fill="x", pady=(2, 12))

        # --- Folder ---
        ctk.CTkLabel(main, text="Guardar en", font=ctk.CTkFont(size=12), anchor="w").pack(fill="x")
        frow = ctk.CTkFrame(main, fg_color="transparent")
        frow.pack(fill="x", pady=(2, 12))
        self.folder_entry = ctk.CTkEntry(frow, height=38)
        self.folder_entry.pack(side="left", fill="x", expand=True)
        self.folder_entry.insert(0, os.path.join(os.path.expanduser("~"), "Music"))
        self.browse_btn = ctk.CTkButton(frow, text="Examinar", width=100, command=self._elegir_carpeta)
        self.browse_btn.pack(side="left", padx=(8, 0))

        # --- Formato (radio buttons) ---
        ctk.CTkLabel(main, text="Formato", font=ctk.CTkFont(size=12), anchor="w").pack(fill="x")
        fmt_row = ctk.CTkFrame(main, fg_color="transparent")
        fmt_row.pack(fill="x", pady=(2, 14))

        self.fmt_var = ctk.StringVar(value="mp3")
        self.fmt_mp3 = ctk.CTkRadioButton(fmt_row, text="MP3 (solo audio)", variable=self.fmt_var, value="mp3",
                                          font=ctk.CTkFont(size=12), command=self._on_formato_change)
        self.fmt_mp3.pack(side="left", padx=(0, 20))
        self.fmt_mp4 = ctk.CTkRadioButton(fmt_row, text="MP4 (video)", variable=self.fmt_var, value="mp4",
                                          font=ctk.CTkFont(size=12), command=self._on_formato_change)
        self.fmt_mp4.pack(side="left")

        # --- Calidad (radio buttons) ---
        ctk.CTkLabel(main, text="Calidad", font=ctk.CTkFont(size=12), anchor="w").pack(fill="x")
        qual_row = ctk.CTkFrame(main, fg_color="transparent")
        qual_row.pack(fill="x", pady=(2, 14))

        self.qual_var = ctk.StringVar(value="192")
        self._qual_radios = []
        for texto, val in [("128 kbps", "128"), ("192 kbps", "192"), ("256 kbps", "256"), ("320 kbps", "320")]:
            rb = ctk.CTkRadioButton(qual_row, text=texto, variable=self.qual_var, value=val,
                                    font=ctk.CTkFont(size=12))
            rb.pack(side="left", padx=(0, 12))
            self._qual_radios.append(rb)

        # --- Checkboxes ---
        self.thumbnail_var = ctk.BooleanVar(value=True)
        self.thumb_check = ctk.CTkCheckBox(main, text="Incluir caratula en el MP3",
                                           variable=self.thumbnail_var, font=ctk.CTkFont(size=12),
                                           checkbox_width=20, checkbox_height=20)
        self.thumb_check.pack(anchor="w", pady=2)

        self.playlist_var = ctk.BooleanVar(value=False)
        self.playlist_check = ctk.CTkCheckBox(main, text="Descargar lista completa (playlist)",
                                              variable=self.playlist_var, font=ctk.CTkFont(size=12),
                                              checkbox_width=20, checkbox_height=20)
        self.playlist_check.pack(anchor="w", pady=(0, 14))

        # --- Progress ---
        self.progress_bar = ctk.CTkProgressBar(main, height=14)
        self.progress_bar.pack(fill="x", pady=(0, 4))
        self.progress_bar.set(0)
        self.status_label = ctk.CTkLabel(main, text="", text_color="#888888", font=ctk.CTkFont(size=11))
        self.status_label.pack()

        # --- Buttons ---
        btn_row = ctk.CTkFrame(main, fg_color="transparent")
        btn_row.pack(pady=(16, 10))
        self.download_btn = ctk.CTkButton(
            btn_row, text="DESCARGAR", height=44, width=200,
            font=ctk.CTkFont(size=14, weight="bold"), command=self._iniciar_descarga,
        )
        self.download_btn.pack(side="left", padx=(0, 10))
        self.cancel_btn = ctk.CTkButton(
            btn_row, text="CANCELAR", height=44, width=120,
            font=ctk.CTkFont(size=13, weight="bold"),
            fg_color="#c0392b", hover_color="#e74c3c", command=self._cancelar_descarga,
        )

        # --- Completion panel ---
        self.comp_container = ctk.CTkFrame(main, fg_color="transparent")

        sep = ctk.CTkFrame(self.comp_container, height=1, fg_color="#333333")
        sep.pack(fill="x", pady=(4, 6))

        self.comp_title = ctk.CTkLabel(self.comp_container, text="Completados",
                                       font=ctk.CTkFont(size=13, weight="bold"), text_color="#4caf50",
                                       anchor="w")
        self.comp_title.pack(fill="x", padx=2)

        self.comp_list = ctk.CTkScrollableFrame(self.comp_container, fg_color="#1a1a1a")
        self.comp_list.pack(fill="both", expand=True, pady=(4, 8))

        self.comp_status = ctk.CTkLabel(self.comp_container, text="", font=ctk.CTkFont(size=11))

        self.comp_actions = ctk.CTkFrame(self.comp_container, fg_color="transparent")
        ctk.CTkButton(self.comp_actions, text="Abrir carpeta", width=130, font=ctk.CTkFont(size=12),
                      command=self._abrir_carpeta_resultado).pack(side="left", padx=(0, 8))
        ctk.CTkButton(self.comp_actions, text="Copiar ruta", width=130, font=ctk.CTkFont(size=12),
                      command=self._copiar_ruta_resultado).pack(side="left")

    # ==================================================================
    #  Formato change
    # ==================================================================
    def _on_formato_change(self):
        es_mp4 = self.fmt_var.get() == "mp4"
        labels = [("360p", "360"), ("720p", "720"), ("1080p", "1080")] if es_mp4 else \
                 [("128 kbps", "128"), ("192 kbps", "192"), ("256 kbps", "256"), ("320 kbps", "320")]

        self.qual_var.set("")

        for i, rb in enumerate(self._qual_radios):
            if i < len(labels):
                rb.configure(text=labels[i][0], value=labels[i][1])
                rb.pack(side="left", padx=(0, 12))
            else:
                rb.pack_forget()

        self.qual_var.set(labels[1][1])

        if es_mp4:
            self.thumb_check.pack_forget()
        else:
            self.thumb_check.pack(anchor="w", pady=2, before=self.playlist_check)

    # ==================================================================
    #  URL detection
    # ==================================================================
    def _bind_url_detection(self):
        def _on_change(*_):
            es = bool(PLAYLIST_RE.search(self.url_entry.get()))
            if es:
                self.playlist_check.configure(text="Descargar lista completa (playlist detectada)", text_color="#f1c40f")
            else:
                self.playlist_check.configure(text="Descargar lista completa (playlist)", text_color=None)
        self.url_entry.bind("<KeyRelease>", _on_change)

    # ==================================================================
    #  Control states
    # ==================================================================
    def _lock_controls(self):
        for w in (self.url_entry, self.folder_entry, self.browse_btn,
                  self.fmt_mp3, self.fmt_mp4, *self._qual_radios,
                  self.thumb_check, self.playlist_check):
            try:
                w.configure(state="disabled")
            except Exception:
                pass
        self.download_btn.configure(state="disabled", text="DESCARGANDO...")
        self.cancel_btn.pack(side="left", padx=(0, 10))
        self.cancel_btn.configure(state="normal", text="CANCELAR")

    def _unlock_controls(self):
        for w in (self.url_entry, self.folder_entry, self.browse_btn,
                  self.fmt_mp3, self.fmt_mp4, *self._qual_radios,
                  self.thumb_check, self.playlist_check):
            try:
                w.configure(state="normal")
            except Exception:
                pass
        self.download_btn.configure(state="normal", text="DESCARGAR")
        self.cancel_btn.pack_forget()

    # ==================================================================
    #  Completion panel helpers
    # ==================================================================
    def _show_completion_panel(self):
        self.comp_container.pack(fill="both", expand=True, padx=0, pady=(0, 10))

    def _hide_completion_panel(self):
        self.comp_container.pack_forget()

    def _reset_completion_panel(self):
        self._completions_count = 0
        self._ultimo_mp3 = None
        for w in self.comp_list.winfo_children():
            w.destroy()
        self.comp_title.configure(text="Completados", text_color="#4caf50")
        self.comp_status.pack_forget()
        self.comp_actions.pack_forget()

    def _add_completion(self, idx, total, titulo, ruta):
        self._completions_count += 1
        if self._completions_count == 1:
            self._ultimo_mp3 = ruta
        fila = ctk.CTkFrame(self.comp_list, fg_color="transparent")
        fila.pack(fill="x", pady=1)
        ctk.CTkLabel(fila, text=f"{self._completions_count}.", width=32,
                     font=ctk.CTkFont(size=11), text_color="#4caf50").pack(side="left")
        ctk.CTkLabel(fila, text=f"{titulo}.{os.path.splitext(ruta)[1][1:]}", font=ctk.CTkFont(size=11),
                     anchor="w").pack(side="left", fill="x", expand=True)

    # ==================================================================
    #  Actions
    # ==================================================================
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

        formato = self.fmt_var.get()
        calidad = self.qual_var.get()
        incluir_caratula = self.thumbnail_var.get()
        descargar_lista = self.playlist_var.get()

        self._descargando = True
        self._cancel_event.clear()

        self._lock_controls()
        self._reset_completion_panel()
        self._show_completion_panel()
        self.status_label.configure(text="Iniciando descarga...", text_color="#888888")
        self.progress_bar.set(0)

        thread = threading.Thread(
            target=descargar,
            args=(url, output, formato, calidad),
            kwargs={
                "incluir_caratula": incluir_caratula,
                "descargar_lista": descargar_lista,
                "cancel_event": self._cancel_event,
                "progress_callback": self._on_progress,
                "item_done_callback": self._on_item_done,
                "done_callback": self._on_done,
                "error_callback": self._on_error,
            },
            daemon=True,
        )
        thread.start()

    def _cancelar_descarga(self):
        self._cancel_event.set()
        self.cancel_btn.configure(state="disabled", text="Cancelando...")

    def _abrir_carpeta_resultado(self):
        target = self._ultimo_mp3 or self.folder_entry.get().strip()
        if os.path.isfile(target):
            os.startfile(os.path.dirname(target))
        elif os.path.isdir(target):
            os.startfile(target)
        else:
            os.startfile(target)

    def _copiar_ruta_resultado(self):
        target = self._ultimo_mp3 or self.folder_entry.get().strip()
        self.clipboard_clear()
        self.clipboard_append(target)
        self.comp_status.configure(text="Ruta copiada al portapapeles", text_color="#4caf50")
        self.comp_status.pack(pady=(2, 0))

    # ==================================================================
    #  Thread callbacks
    # ==================================================================
    def _on_progress(self, d):
        self.after(0, self._update_progress, d)

    def _update_progress(self, d):
        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 1
            downloaded = d.get("downloaded_bytes", 0)
            pct = min(downloaded / total, 1.0)
            self.progress_bar.set(pct)
            speed = d.get("_speed_str", "")
            nombre = d.get("info_dict", {}).get("title", "")[:55]
            info = d.get("info_dict", {})
            pl_idx = info.get("playlist_index")
            pl_count = info.get("playlist_count")
            extra = f"Video {pl_idx}/{pl_count}  " if pl_idx is not None and pl_count else ""
            self.status_label.configure(text=f"{extra}{nombre}   {int(pct*100)}%   {speed}", text_color="#ffffff")
        elif d["status"] == "finished":
            self.progress_bar.set(1)
            info = d.get("info_dict", {})
            pl_idx = info.get("playlist_index")
            pl_count = info.get("playlist_count")
            if pl_idx is not None and pl_count:
                self.status_label.configure(text=f"Procesando video {pl_idx}/{pl_count}...", text_color="#aaaaaa")
            else:
                self.status_label.configure(text="Procesando...", text_color="#aaaaaa")

    def _on_item_done(self, idx, total, titulo, ruta):
        self.after(0, self._add_completion, idx, total, titulo, ruta)

    def _on_done(self, path, title):
        self.after(0, self._finalizar_exito, path, title)

    def _finalizar_exito(self, path, title):
        self._descargando = False
        self._unlock_controls()
        self.status_label.configure(text="")
        self.progress_bar.set(0)

        if path:
            self._add_completion(1, 1, title, path)
            self.comp_title.configure(text="Completado", text_color="#4caf50")
        else:
            self.comp_title.configure(text=f"Completados ({self._completions_count})", text_color="#4caf50")

        self.comp_actions.pack(fill="x", pady=(6, 0))

    def _on_error(self, msg):
        self.after(0, self._finalizar_error, msg)

    def _finalizar_error(self, msg):
        self._descargando = False
        self._unlock_controls()
        self.status_label.configure(text="")
        self.progress_bar.set(0)

        if self._completions_count > 0:
            self.comp_title.configure(text=f"Cancelado ({self._completions_count} ok)", text_color="#f1c40f")
            self.comp_status.configure(text=msg, text_color="#e74c3c")
            self.comp_status.pack(pady=(2, 0))
            self.comp_actions.pack(fill="x", pady=(6, 0))
        else:
            self._hide_completion_panel()


if __name__ == "__main__":
    app = TubeGetApp()
    app.mainloop()
