from logicProblem import KB
from logicBottomUp import fixed_point
import os


class ProbItem:
    """
    Classe che rappresenta un elemento con probabilità associata.
    """

    def __init__(self, name, prob):
        self.name = name  # Nome della malattia
        self.prob = prob  # Probabilità associata

    def __str__(self):
        return f"{self.name} -> {self.prob}"

    def __repr__(self):
        return str(self)

    def __lt__(self, item):
        return self.prob < item.prob  # Ordinamento in base alla probabilità


def get_disease(kb=KB()):
    """
    Restituisce tutte le malattie che risultano vere nel punto fisso della KB,
    partendo dai sintomi veri.
    """
    fp = fixed_point(kb)  # Calcola il punto fisso della KB
    atoms = {c.head for c in kb.clauses if c.isAtom()}  # Prende tutti gli atomi (sintomi)
    return list(fp.difference(atoms))  # Restituisce solo le malattie (escludendo i sintomi)


def get_prob_model(kb=KB()):
    """
    Restituisce un elenco di oggetti ProbItem che rappresentano il modello probabilistico,
    indicando la probabilità che il paziente abbia una specifica malattia.
    Se non ci sono malattie identificate, restituisce una lista vuota.
    """
    disease = get_disease(kb)  # Ottiene le malattie vere nella KB

    if not disease:
        return []  # Nessuna malattia identificata

    model = []  # Modello con le probabilità delle malattie
    for d in disease:
        model.append(ProbItem(d, get_prob(d, kb)))  # Crea un oggetto ProbItem per ogni malattia

    sumProb = sum(item.prob for item in model)  # Somma delle probabilità (deve essere 1)

    # Normalizzazione delle probabilità
    for item in model:
        item.prob = item.prob / sumProb

    model.sort(reverse=True)  # Ordina il modello in ordine decrescente di probabilità
    return model


def get_prob(disease, kb=KB()):
    """
    Restituisce la probabilità che una malattia sia vera.
    Condizione: la malattia deve avere una clausola associata con un body non nullo.
    """
    allSym = len({c.head for c in kb.clauses if c.isAtom()})  # Numero totale di sintomi veri
    for c in kb.clauses:
        if c.head == disease:
            return len(c.body) / allSym  # Probabilità = numero di sintomi della malattia / sintomi totali veri


def how(KB, item):
    """
    Restituisce la clausola utilizzata per provare l'elemento specificato.
    Se non esiste una prova, restituisce None.
    """
    for c in KB.clauses:
        if c.head == item:
            return c
    return None


def real_filename(filename=""):
    """
    Restituisce il percorso assoluto di un file.
    """
    return os.path.realpath(filename)
