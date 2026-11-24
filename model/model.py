from cmath import inf

from database.parco_DAO import ParcoDAO
from database.escursione_DAO import EscursioneDAO
from database.punto_interesse_DAO import PuntoInteresseDAO

class Model:
    def __init__(self):
        self.escursioni_map = {} # Mappa ID escursione -> oggetti Escursione
        self.punti_interesse_map = {} # Mappa ID punto di interesse -> oggetti PuntoInteresse
        self.escursioni_punti_map = []

        self._pacchetto_ottimo = []
        self._valore_ottimo: int = -1
        self._costo = 0
        self._costo_corrente = float("inf")

        # TODO: Aggiungere eventuali altri attributi
        self._max_budget = 0
        # Caricamento
        self.load_escursioni()
        self.load_punti_interesse()
        self.load_relazioni()

    @staticmethod
    def load_parchi():
        """ Restituisce tutti i parchi disponibili """
        return ParcoDAO.get_parchi()

    def load_escursioni(self):
        """ Carica tutte le escursioni in un dizionario [id, Escursione]"""
        self.escursioni_map = EscursioneDAO.get_escursioni()

    def load_punti_interesse(self):
        """ Carica tutti i punti di interesse in un dizionario [id, PuntoInteresse]"""
        self.punti_interesse_map = PuntoInteresseDAO.get_punti_interesse()

    def load_relazioni(self):
        """
            Interroga il database per ottenere tutte le relazioni fra escursioni e punti di interesse e salvarle nelle strutture dati
            Collega escursione <-> punti di interesse.
            --> Ogni Escursione ha un set di PuntoInteresse.
            --> Ogni PuntoInteresse ha un set di Escursioni.
        """
        # TODO
        self.escursioni_map = EscursioneDAO.get_escursioni()   # Mappa ID escursione -> oggetti Escursione
        self.punti_interesse_map = PuntoInteresseDAO.get_punti_interesse()# Mappa ID punto di interesse -> oggetti PuntoInteresse
        self.escursioni_punti_map = EscursioneDAO.get_escursioni_punti_interesse()
        print(self.escursioni_punti_map)
        print(self.punti_interesse_map)
        print(self.escursioni_map)

    def genera_pacchetto(self, id_parco: str, max_giorni: int, max_budget: float):
        """
        Calcola il pacchetto di escursioni ottimale per un parco rispettando i vincoli di durata, budget e punti di interesse unici.
        :param id_parco: id del parco
        :param max_giorni: numero massimo di giorni (può essere None --> nessun limite)
        :param max_budget: costo massimo del pacchetto (può essere None --> nessun limite)

        :return: self._pacchetto_ottimo (una lista di oggetti Escursione)
        :return: self._costo (il costo del pacchetto)
        :return: self._valore_ottimo (il voto complessivo dei visitatori per il pacchetto)
        """
        self._pacchetto_ottimo = []
        self._costo = 0
        self._valore_ottimo = -1

        # TODO
        self._max_budget = max_budget
        self._ricorsione(id_parco,[],max_giorni,max_budget,0,set())
        return self._pacchetto_ottimo, self._costo, self._valore_ottimo

    # def _ricorsione(self, start_index: str, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float, valore_corrente: int, punti_usati: set):
    #     """ Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il voto complessivo dei visitatori"""
    #     print("Ciao sono dentro")
    #     # TODO: è possibile cambiare i parametri formali della funzione se ritenuto opportuno
    #     if costo_corrente == 0 or durata_corrente == 0:
    #
    #         if valore_corrente > self._valore_ottimo:
    #
    #             self._costo = costo_corrente
    #             self._valore_ottimo = valore_corrente
    #             self._pacchetto_ottimo = pacchetto_parziale
    #
    #         return
    #
    #     else:
    #         for dizionario in self.escursioni_punti_map:
    #             if dizionario["id_escursione"] == start_index and durata_corrente-self.escursioni_map[dizionario["id_escursione"]].durata_giorni > 0 and costo_corrente - self.escursioni_map[dizionario["id_escursione"]].costo > 0 and dizionario["id_punti_interesse"] not in punti_usati:
    #
    #                 pacchetto_parziale.append(dizionario["id_escursione"])
    #                 punti_usati.add(dizionario["id_punti_interesse"])
    #
    #                 self._ricorsione(start_index,
    #                                 pacchetto_parziale,
    #                                 durata_corrente-self.escursioni_map[dizionario["id_escursione"]].durata_giorni,
    #                                 costo_corrente - self.escursioni_map[dizionario["id_escursione"]].costo,
    #                                 valore_corrente+ self.punti_interesse_map[dizionario["id_punto_interesse"]].voto_visitatori,
    #                                 punti_usati)
    #                 print(pacchetto_parziale)
    #                 pacchetto_parziale.pop()
    #                 punti_usati.remove(dizionario["id_punto_interesse"])
    def _ricorsione(self, start_index, pacchetto_parziale: list, durata_corrente: int, costo_corrente: float,
                    valore_corrente: int, punti_usati: set, escursioni_usate: set = None):
        """Algoritmo di ricorsione che deve trovare il pacchetto che massimizza il voto complessivo dei visitatori."""
        if escursioni_usate is None:
            escursioni_usate = set()


        if valore_corrente > self._valore_ottimo:
            self._valore_ottimo = valore_corrente
            self._costo = costo_corrente
            self._pacchetto_ottimo = pacchetto_parziale.copy()

        for dizionario in self.escursioni_punti_map:
            id_esc = dizionario["id_escursione"]
            id_punto = dizionario["id_punto_interesse"]

            esc = self.escursioni_map[id_esc]
            punto = self.punti_interesse_map[id_punto]

            nuova_durata = durata_corrente - esc.durata_giorni
            nuovo_costo = costo_corrente - esc.costo

            if (
                    id_esc not in escursioni_usate
                    and id_punto not in punti_usati
                    and nuova_durata >= 0
                    and nuovo_costo >= 0
            ):
                pacchetto_parziale.append(id_esc)
                escursioni_usate.add(id_esc)
                punti_usati.add(id_punto)

                self._ricorsione(
                    start_index,
                    pacchetto_parziale,
                    nuova_durata,
                    nuovo_costo,
                    valore_corrente + punto.voto_visitatori,
                    punti_usati,
                    escursioni_usate,
                )

                pacchetto_parziale.pop()
                escursioni_usate.remove(id_esc)
                punti_usati.remove(id_punto)
