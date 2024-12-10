import tkinter as tk
from tkinter import filedialog, messagebox
import whisper
import threading
import os  # Do wymuszenia zamknięcia procesu

# Funkcja obsługująca wybór pliku wideo asd
def wybierz_plik():
    sciezka_pliku = filedialog.askopenfilename(
        title="Wybierz plik wideo",
        filetypes=[("Pliki wideo", "*.mp4 *.mkv *.avi *.mov *.flv *.wmv")]
    )
    if sciezka_pliku:
        input_path.set(sciezka_pliku)

# Funkcja obsługująca wybór ścieżki zapisu pliku SRT
def wybierz_sciezke_zapisu():
    sciezka_zapisu = filedialog.asksaveasfilename(
        title="Wybierz miejsce zapisu pliku SRT",
        defaultextension=".srt",
        filetypes=[("Plik SRT", "*.srt")]
    )
    if sciezka_zapisu:
        output_path.set(sciezka_zapisu)

# Funkcja do animacji kropek
def start_spinner():
    global animating
    animating = True
    spinner_label.place(relx=0.5, rely=0.85, anchor=tk.CENTER)
    update_spinner()

def stop_spinner():
    global animating
    animating = False
    spinner_label.place_forget()

def update_spinner():
    global spinner_step
    if animating and running:
        spinner_text.set(f"Przetwarzanie{'.' * ((spinner_step % 3) + 1)}")
        spinner_step += 1
        root.after(500, update_spinner)

# Funkcja obsługująca generowanie pliku SRT
def generuj_srt():
    sciezka_wideo = input_path.get()
    sciezka_srt = output_path.get()

    if not sciezka_wideo or not sciezka_srt:
        messagebox.showerror("Błąd", "Upewnij się, że wybrałeś plik wideo i ścieżkę zapisu.")
        return

    def transkrybuj():
        try:
            if not running:
                return

            start_spinner()
            model = whisper.load_model("base")

            result = model.transcribe(sciezka_wideo, task="transcribe", language="pl")
            if not running:
                return

            with open(sciezka_srt, "w", encoding="utf-8") as srt_file:
                for i, segment in enumerate(result["segments"]):
                    start = segment["start"]
                    end = segment["end"]
                    text = segment["text"]

                    def format_time(seconds):
                        millis = int((seconds % 1) * 1000)
                        seconds = int(seconds)
                        minutes, seconds = divmod(seconds, 60)
                        hours, minutes = divmod(minutes, 60)
                        return f"{hours:02}:{minutes:02}:{seconds:02},{millis:03}"

                    srt_file.write(f"{i + 1}\n")
                    srt_file.write(f"{format_time(start)} --> {format_time(end)}\n")
                    srt_file.write(f"{text.strip()}\n\n")

            if running:
                messagebox.showinfo("Sukces", f"Plik SRT został zapisany jako: {sciezka_srt}")

        except Exception as e:
            if running:
                messagebox.showerror("Błąd", f"Wystąpił problem: {str(e)}")
        finally:
            stop_spinner()

    thread = threading.Thread(target=transkrybuj)
    thread.daemon = True  # Wątek zakończy się po zamknięciu głównego procesu
    thread.start()

# Funkcja obsługująca zamykanie okna i przerywanie procesu
def on_closing():
    global running
    running = False
    stop_spinner()
    os._exit(0)  # Wymuszone zamknięcie procesu

# Tworzenie okna aplikacji
root = tk.Tk()
root.title("Transkrypcja Wideo do SRT")
root.geometry("600x400")

# Zmienne ścieżek i animacji
input_path = tk.StringVar()
output_path = tk.StringVar()
spinner_text = tk.StringVar(value="Przetwarzanie.")
spinner_step = 0
animating = False
running = True

# Główna ramka
frame = tk.Frame(root, padx=20, pady=20)
frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

# Wybór pliku wideo
label1 = tk.Label(frame, text="Wybierz plik wideo:", font=("Helvetica", 14))
label1.pack(pady=10)

entry1 = tk.Entry(frame, textvariable=input_path, width=70)
entry1.pack(pady=5)

browse_button1 = tk.Button(frame, text="Przeglądaj", command=wybierz_plik)
browse_button1.pack(pady=5)

# Wybór ścieżki zapisu pliku SRT
label2 = tk.Label(frame, text="Wybierz ścieżkę zapisu pliku SRT:", font=("Helvetica", 14))
label2.pack(pady=10)

entry2 = tk.Entry(frame, textvariable=output_path, width=70)
entry2.pack(pady=5)

browse_button2 = tk.Button(frame, text="Przeglądaj", command=wybierz_sciezke_zapisu)
browse_button2.pack(pady=5)

# Przycisk do rozpoczęcia transkrypcji
transcribe_button = tk.Button(frame, text="Generuj plik SRT", command=generuj_srt)
transcribe_button.pack(pady=20)

# Spinner (animowane kropki)
spinner_label = tk.Label(root, textvariable=spinner_text, font=("Helvetica", 12))

# Obsługa zamykania okna
root.protocol("WM_DELETE_WINDOW", on_closing)

root.mainloop()
