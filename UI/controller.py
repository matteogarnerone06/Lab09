import flet as ft
from UI.view import View
from model.model import Model


class Controller:
    def __init__(self, view: View, model: Model):
        self._model = model
        self._view = view

        # Variabili per memorizzare le selezioni correnti
        self.parco_selezionato = None
        self.durata = None
        self.costo = None

    def on_parco_change(self, e):
        """Aggiorna il parco selezionato e salva il valore."""
        self.parco_selezionato = e.control.value

    def popola_dropdown_parco(self):
        """Popola il menu a tendina dei parchi."""
        self._view.dd_parco.options.clear()

        parchi = self._model.load_parchi() # Ogni parco (id, nome_parco)

        if parchi:
            for parco in sorted(parchi):
                self._view.dd_parco.options.append(ft.dropdown.Option(key=parco.id, text=parco.nome))
        else:
            self._view.show_alert("Errore nel caricamento dei parchi.")

        self._view.update()

    def check_giorni(self, e):
        """Controlla che il formato sia corretto per durata in giorni"""
        try:
            self._view.durata_massima.error = None
            if e.control.value == "":
                self.durata = None
            else:
                self.durata = int(e.control.value)
        except Exception:
            self.durata = None
            self._view.durata_massima.error = "Giorni non Validi"
        self._view.update()

    def check_budget(self, e):
        """Controlla che il formato sia corretto per budget in euro"""
        try:
            self._view.budget_massimo.error = None
            if e.control.value == "":
                self.costo = None
            else:
                e.control.value = e.control.value.replace(".", "")
                self.costo = float(e.control.value.replace(",", "."))
        except Exception:
            self.costo = None
            self._view.budget_massimo.error = "Budget non valido"
        self._view.update()

    def genera_pacchetto(self, e):
        """Chiama il Model per generare il pacchetto ottimo"""
        if self.parco_selezionato is None:
            self._view.show_alert("Selezionare un Parco!")
        elif self._view.budget_massimo.error is not None or self._view.durata_massima.error is not None:
            self._view.show_alert("Dati non validi!")
        else:
            pacchetto, costo, voto_totale = self._model.genera_pacchetto(self.parco_selezionato, self.durata, self.costo)
            costo = f"{costo:.2f}".replace(".", ",")
            self._view.lista_visualizzazione.controls.clear()
            self._view.lista_visualizzazione.controls.append(
                ft.Text(f"Il pacchetto ottimo costa {costo}€ e ha un voto complessivo pari a {voto_totale}:"))
            for escursione in pacchetto:
                self._view.lista_visualizzazione.controls.append(ft.Text(f" •    {escursione} → {escursione.punti_interesse}"))
            self._view.update()
