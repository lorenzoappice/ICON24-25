import tkinter as tk
from tkinter import ttk, messagebox
import Ontologymanager as om
import utility as utils


# Funzione per cancellare l'area di output e resettare la KB
def cancel_console(interface):
    interface.consoleArea.config(state="normal")
    interface.consoleArea.delete("1.0", tk.END)
    interface.consoleArea.config(state="disabled")
    interface.selected_sym.clear()
    interface.kb = om.create_KB(interface.map_disease_symptom)


# Funzione per selezionare un sintomo dalla lista e mostrarlo nell'area di output
def select_symptom(event, interface):
    selected = interface.symptomCombo.get()
    if selected and selected not in interface.selected_sym:
        interface.selected_sym.add(selected)
        interface.consoleArea.config(state="normal")
        if interface.consoleArea.get("1.0", "end-1c").strip():
            interface.consoleArea.insert(tk.END, " + " + selected)
        else:
            interface.consoleArea.insert(tk.END, selected)
        interface.consoleArea.config(state="disabled")


# Funzione per inviare i sintomi selezionati e ottenere la diagnosi probabilistica
def send_symptom(interface):
    _input = interface.consoleArea.get("1.0", "end-1c").strip().split(" + ")
    if not _input or _input == [""]:
        messagebox.showwarning("Warning", "No symptoms selected!")
        return

    assumable = [om.lp.Clause(head=item) for item in _input]
    interface.kb.clauses += assumable
    model = utils.get_prob_model(interface.kb)

    interface.consoleArea.config(state="normal")
    interface.consoleArea.insert(tk.END, "\n\n--- RISULTATO DIAGNOSI ---\n\n")

    if model:
        interface.consoleArea.insert(tk.END, "Malattia\t\tProbabilità\n")
        interface.consoleArea.insert(tk.END, "-------------------------------------\n")
        for disease in model:
            interface.consoleArea.insert(tk.END, f"{disease.name}\t\t{disease.prob * 100:.2f}%\n")
    else:
        messagebox.showinfo("Info", "Nessuna malattia corrispondente trovata.")

    interface.consoleArea.insert(tk.END, "\n\nInserisci altri sintomi:\n" + "+".join(interface.selected_sym))
    interface.consoleArea.config(state="disabled")


# Funzione per ottenere una spiegazione sulla derivazione di un fatto nella KB
def submit_how(entry, KB):
    res = utils.how(KB, entry)
    if res:
        msg = f"La clausola usata per dimostrare {entry} è:\n{str(res)}"
        if not res.body:
            msg = f"{res.head} è un sintomo dato, quindi è vero di default."
        messagebox.showinfo("How", msg)
    else:
        messagebox.showerror("Errore", f"Nessuna prova trovata per {entry}.")


# Classe principale per l'interfaccia grafica
class StartInterface:
    def __init__(self, onto_filename):
        # Caricamento dell'ontologia
        self.onto = om.owl.get_ontology(utils.real_filename(onto_filename))
        self.onto.load()

        # Inizializzazione delle strutture dati
        self.selected_sym = set()
        self.map_disease_symptom = om.build_map(self.onto)
        self.symptoms = om.list_symptoms(self.map_disease_symptom)
        self.kb = om.create_KB(self.map_disease_symptom)

        # Creazione della finestra principale
        self.window = tk.Tk()
        self.window.geometry("800x600")
        self.window.title("Analizzatore Sintomi")
        self.window.iconphoto(True, tk.PhotoImage(file='../imgs/icon.png'))
        self.window.resizable(False, False)

        # Impostazione dello stile grafico
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Sezione superiore: selezione dei sintomi
        self.frameUpper = ttk.Frame(self.window, padding=15)
        self.frameUpper.pack(fill="x", padx=10, pady=10)
        ttk.Label(self.frameUpper, text="Seleziona i sintomi:", font=("Arial", 14, "bold")).pack(side="left", padx=5)

        self.symptomCombo = ttk.Combobox(self.frameUpper, values=self.symptoms, state="readonly", width=30,
                                         font=("Arial", 12))
        self.symptomCombo.pack(side="left", padx=10)
        self.symptomCombo.bind("<<ComboboxSelected>>", lambda event: select_symptom(event, self))

        # Sezione pulsanti: invio e reset
        self.frameButtons = ttk.Frame(self.window, padding=15)
        self.frameButtons.pack(fill="x", padx=10, pady=5)

        self.style.configure("Green.TButton", background="#4CAF50", foreground="white", font=("Arial", 12, "bold"))
        self.style.map("Green.TButton", background=[("active", "#45a049")])
        self.buttomSubmit = ttk.Button(self.frameButtons, text="Invia", command=lambda: send_symptom(self),
                                       style="Green.TButton")
        self.buttomSubmit.pack(side="left", expand=True, padx=10)

        self.style.configure("Red.TButton", background="#f44336", foreground="white", font=("Arial", 12, "bold"))
        self.style.map("Red.TButton", background=[("active", "#e53935")])
        self.buttomClear = ttk.Button(self.frameButtons, text="Resetta", command=lambda: cancel_console(self),
                                      style="Red.TButton")
        self.buttomClear.pack(side="left", expand=True, padx=10)

        # Sezione inferiore: area di output
        self.frameBottom = ttk.Frame(self.window, padding=15)
        self.frameBottom.pack(fill="both", expand=True, padx=10, pady=10)
        ttk.Label(self.frameBottom, text="Sintomi selezionati e risultati:", font=("Arial", 14, "bold")).pack(
            anchor="w")

        self.consoleArea = tk.Text(self.frameBottom, fg="black", wrap="word", height=15, font=("Arial", 12),
                                   state="disabled")
        self.consoleArea.pack(fill="both", expand=True)

        # Sezione "How" per spiegazioni
        self.frameHow = ttk.Frame(self.window, padding=10)
        self.frameHow.pack(fill="x", padx=10, pady=3)
        ttk.Label(self.frameHow, text="How:", font=("Arial", 12)).pack(side="left")

        self.howQuery = ttk.Entry(self.frameHow, width=30, font=("Arial", 12))
        self.howQuery.pack(side="left", padx=10)
        self.howSubmitButton = ttk.Button(self.frameHow, text="Invia",
                                          command=lambda: submit_how(self.howQuery.get(), self.kb),
                                          style="Green.TButton")
        self.howSubmitButton.pack(side="left", padx=10)

        # Avvio dell'interfaccia grafica
        self.window.mainloop()


# Avvio dell'applicazione
i = StartInterface("do_inferred")