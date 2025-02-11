import logicProblem as lp
import owlready2 as owl

REAL_CLASS_LABEL = 0  # Indice della label reale della classe


def get_class(ontology, class_name):
    """
    Restituisce un elenco di sottoclassi della classe specificata.
    """
    for c in ontology.classes():
        if class_name in c.label:  # Se la classe target è trovata, restituisce tutte le sue sottoclassi
            return ontology.search(is_a=c)


def build_map(ontology):
    """
    Costruisce un dizionario in cui la chiave è il nome della malattia
    e il valore è una lista di sintomi associati.
    """
    _map = {}  # Dizionario con chiavi come malattie e valori come lista di sintomi
    malattie = get_class(ontology, "disease")  # Recupera tutte le malattie

    for malattia in malattie:
        sintomi = [sintomo.label[REAL_CLASS_LABEL] for sintomo in
                   malattia.has_symptom]  # Ottiene i nomi reali dei sintomi

        if sintomi:
            _map[malattia.label[REAL_CLASS_LABEL]] = sintomi  # Popola il dizionario solo se ci sono sintomi

    return _map


def create_KB(map_disease_symptom):
    """
    Crea una base di conoscenza (KB) come un insieme di clausole definite.
    """
    clausole = []  # Lista di clausole

    for malattia, sintomi in map_disease_symptom.items():  # Itera su tutte le malattie
        clausola_definita = lp.Clause(malattia,
                                      sintomi)  # Crea una clausola definita con la malattia come testa e i sintomi come corpo
        clausole.append(clausola_definita)

    return lp.KB(clausole)  # Restituisce l'oggetto della KB con tutte le clausole


def list_symptoms(map_disease_symptoms):
    """
    Restituisce una lista ordinata e senza duplicati di tutti i sintomi presenti nella KB.
    """
    sintomi = set()

    for lista_sintomi in map_disease_symptoms.values():
        sintomi.update(lista_sintomi)

    return sorted(sintomi)
