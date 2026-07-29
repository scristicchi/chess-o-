import tkinter as tk
from tkinter import messagebox

# Costanti di gioco
DIMENSIONE = 600
RIGHE, COLONNE = 8, 8
DIM_CASELLA = DIMENSIONE // COLONNE

# Colori stile Scacchiera in Legno
LEGNO_CHIARO = "#F0D9B5"
LEGNO_SCURO = "#B58863"

# Colori Pezzi
COLORE_BIANCO_PEZZO = "#2C2C2C"
COLORE_NERO_PEZZO = "#000000"
EVIDENZIA_SELEZIONE = "#FF3333"

# Dizionario simboli Unicode
UNICODE_PEZZI = {
    'BR': '♔', 'BQ': '♕', 'BT': '♖', 'BA': '♗', 'BC': '♘', 'BP': '♙',
    'NR': '♚', 'NQ': '♛', 'NT': '♜', 'NA': '♝', 'NC': '♞', 'NP': '♟'
}

# Valori materiali per il momentum
VALORI_PEZZI = {'P': 1, 'C': 3, 'A': 3, 'T': 5, 'Q': 9, 'R': 0}


class Pezzo:
    def __init__(self, colore, tipo):
        self.colore = colore
        self.tipo = tipo
        self.simbolo = UNICODE_PEZZI[f"{colore}{tipo}"]
        self.has_moved = False

    def ottieni_colore_grafico(self, is_selected):
        if is_selected:
            return EVIDENZIA_SELEZIONE
        return COLORE_BIANCO_PEZZO if self.colore == 'B' else COLORE_NERO_PEZZO

    def colore_destinazione_ok(self, r_a, c_a, griglia):
        pezzo = griglia[r_a][c_a]
        return pezzo is None or pezzo.colore != self.colore

    def mossa_valida(self, r_p, c_p, r_a, c_a, griglia):
        return False

    def controllo_linea_dritta(self, r_p, c_p, r_a, c_a, griglia):
        if r_p != r_a and c_p != c_a:
            return False
        step_r = 0 if r_p == r_a else (1 if r_a > r_p else -1)
        step_c = 0 if c_p == c_a else (1 if c_a > c_p else -1)
        curr_r, curr_c = r_p + step_r, c_p + step_c
        while curr_r != r_a or curr_c != c_a:
            if griglia[curr_r][curr_c] is not None:
                return False
            curr_r += step_r
            curr_c += step_c
        return True

    def controllo_diagonale(self, r_p, c_p, r_a, c_a, griglia):
        if abs(r_a - r_p) != abs(c_a - c_p):
            return False
        step_r = 1 if r_a > r_p else -1
        step_c = 1 if c_a > c_p else -1
        curr_r, curr_c = r_p + step_r, c_p + step_c
        while curr_r != r_a and curr_c != c_a:
            if griglia[curr_r][curr_c] is not None:
                return False
            curr_r += step_r
            curr_c += step_c
        return True


# --- Classi Specifiche dei Pezzi ---
class Pedone(Pezzo):
    def mossa_valida(self, r_p, c_p, r_a, c_a, griglia):
        if not self.colore_destinazione_ok(r_a, c_a, griglia):
            return False
        direzione = -1 if self.colore == 'B' else 1
        riga_iniziale = 6 if self.colore == 'B' else 1
        pezzo_arrivo = griglia[r_a][c_a]
        # Mossa semplice di 1
        if c_p == c_a and r_a == r_p + direzione and pezzo_arrivo is None:
            return True
        # Mossa doppia dalla posizione iniziale
        if c_p == c_a and r_p == riga_iniziale and r_a == r_p + 2 * direzione:
            if griglia[r_p + direzione][c_p] is None and pezzo_arrivo is None:
                return True
        # Cattura diagonale
        if abs(c_a - c_p) == 1 and r_a == r_p + direzione and pezzo_arrivo is not None:
            return True
        return False


class Torre(Pezzo):
    def mossa_valida(self, r_p, c_p, r_a, c_a, griglia):
        return self.colore_destinazione_ok(r_a, c_a, griglia) and self.controllo_linea_dritta(r_p, c_p, r_a, c_a, griglia)


class Alfiere(Pezzo):
    def mossa_valida(self, r_p, c_p, r_a, c_a, griglia):
        return self.colore_destinazione_ok(r_a, c_a, griglia) and self.controllo_diagonale(r_p, c_p, r_a, c_a, griglia)


class Cavallo(Pezzo):
    def mossa_valida(self, r_p, c_p, r_a, c_a, griglia):
        return self.colore_destinazione_ok(r_a, c_a, griglia) and (
            (abs(r_a - r_p) == 2 and abs(c_a - c_p) == 1) or
            (abs(r_a - r_p) == 1 and abs(c_a - c_p) == 2)
        )


class Regina(Pezzo):
    def mossa_valida(self, r_p, c_p, r_a, c_a, griglia):
        return self.colore_destinazione_ok(r_a, c_a, griglia) and (
            self.controllo_linea_dritta(r_p, c_p, r_a, c_a, griglia) or
            self.controllo_diagonale(r_p, c_p, r_a, c_a, griglia)
        )


class Re(Pezzo):
    def mossa_valida(self, r_p, c_p, r_a, c_a, griglia):
        return self.colore_destinazione_ok(r_a, c_a, griglia) and \
               abs(r_a - r_p) <= 1 and abs(c_a - c_p) <= 1 and \
               (r_a != r_p or c_a != c_p)


class Scacchiera:
    def __init__(self):
        self.griglia = [[None for _ in range(COLONNE)] for _ in range(RIGHE)]
        self.inizializza_pezzi()

    def inizializza_pezzi(self):
        # Pedoni
        for col in range(COLONNE):
            self.griglia[1][col] = Pedone('N', 'P')
            self.griglia[6][col] = Pedone('B', 'P')
        # Neri riga 0
        self.griglia[0][0] = Torre('N', 'T')
        self.griglia[0][1] = Cavallo('N', 'C')
        self.griglia[0][2] = Alfiere('N', 'A')
        self.griglia[0][3] = Regina('N', 'Q')
        self.griglia[0][4] = Re('N', 'R')
        self.griglia[0][5] = Alfiere('N', 'A')
        self.griglia[0][6] = Cavallo('N', 'C')
        self.griglia[0][7] = Torre('N', 'T')
        # Bianchi riga 7
        self.griglia[7][0] = Torre('B', 'T')
        self.griglia[7][1] = Cavallo('B', 'C')
        self.griglia[7][2] = Alfiere('B', 'A')
        self.griglia[7][3] = Regina('B', 'Q')
        self.griglia[7][4] = Re('B', 'R')
        self.griglia[7][5] = Alfiere('B', 'A')
        self.griglia[7][6] = Cavallo('B', 'C')
        self.griglia[7][7] = Torre('B', 'T')

    def trova_re(self, colore):
        for r in range(RIGHE):
            for c in range(COLONNE):
                p = self.griglia[r][c]
                if p is not None and p.tipo == 'R' and p.colore == colore:
                    return r, c
        return None

    def subisce_scacco(self, colore):
        pos_re = self.trova_re(colore)
        if not pos_re:
            return False
        r_re, c_re = pos_re
        colore_avversario = 'N' if colore == 'B' else 'B'
        return self.casella_sotto_attacco(r_re, c_re, colore_avversario)

    def casella_sotto_attacco(self, r, c, colore_attaccante):
        """Verifica se la casella (r,c) è minacciata da un pezzo di colore_attaccante."""
        for rr in range(RIGHE):
            for cc in range(COLONNE):
                p = self.griglia[rr][cc]
                if p is not None and p.colore == colore_attaccante:
                    if p.tipo == 'P':
                        # Il pedone attacca solo in diagonale
                        direzione = -1 if p.colore == 'B' else 1
                        if r == rr + direzione and abs(c - cc) == 1:
                            return True
                    else:
                        if p.mossa_valida(rr, cc, r, c, self.griglia):
                            return True
        return False


class Gioco:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Scacchi - Edizione Legno")
        
        # Turno
        self.label_turno = tk.Label(self.root, text="Turno: BIANCO", font=("Arial", 14, "bold"))
        self.label_turno.pack(pady=5)
        
        # Scacchiera
        self.canvas = tk.Canvas(self.root, width=DIMENSIONE, height=DIMENSIONE)
        self.canvas.pack()
        
        # Momentum
        self.frame_momentum = tk.Frame(self.root, pady=5)
        self.frame_momentum.pack()
        self.label_momentum = tk.Label(self.frame_momentum, text="Bianco: 39  |  Nero: 39", font=("Arial", 10, "bold"))
        self.label_momentum.pack()
        self.canvas_momentum = tk.Canvas(self.frame_momentum, width=400, height=20, bg="#CCCCCC", highlightthickness=1, highlightbackground="black")
        self.canvas_momentum.pack()
        self.rett_bianco = self.canvas_momentum.create_rectangle(0, 0, 200, 20, fill="#F0D9B5", outline="")
        self.rett_nero = self.canvas_momentum.create_rectangle(200, 0, 400, 20, fill="#B58863", outline="")
        
        # Pezzi mangiati
        self.frame_mangiati = tk.Frame(self.root, pady=10)
        self.frame_mangiati.pack()
        self.label_mangiati_bianchi = tk.Label(self.frame_mangiati, text="Mangiati dal Bianco: ", font=("Arial", 11), fg="black")
        self.label_mangiati_bianchi.grid(row=0, column=0, padx=20)
        self.label_mangiati_neri = tk.Label(self.frame_mangiati, text="Mangiati dal Nero: ", font=("Arial", 11), fg="black")
        self.label_mangiati_neri.grid(row=1, column=0, padx=20)
        
        self.mangiati_dal_bianco = []
        self.mangiati_dal_nero = []
        
        self.scacchiera = Scacchiera()
        self.posizione_selezionata = None
        self.turno = 'B'
        
        self.canvas.bind("<Button-1>", self.gestisci_click)
        self.disegna_gioco()
        self.aggiorna_momentum()

    def calcola_valore_materiale(self, colore):
        totale = 0
        for r in range(RIGHE):
            for c in range(COLONNE):
                p = self.scacchiera.griglia[r][c]
                if p is not None and p.colore == colore:
                    totale += VALORI_PEZZI.get(p.tipo, 0)
        return totale

    def aggiorna_momentum(self):
        val_b = self.calcola_valore_materiale('B')
        val_n = self.calcola_valore_materiale('N')
        totale = val_b + val_n
        if totale == 0:
            pct_b = 50.0
        else:
            pct_b = (val_b / totale) * 100
        
        larghezza_totale = 400
        larg_b = (pct_b / 100) * larghezza_totale
        
        self.canvas_momentum.coords(self.rett_bianco, 0, 0, larg_b, 20)
        self.canvas_momentum.coords(self.rett_nero, larg_b, 0, larghezza_totale, 20)
        self.label_momentum.config(text=f"Bianco: {val_b}  |  Nero: {val_n}")

    def tenta_arrocco(self, r_p, c_p, r_a, c_a):
        """Gestisce arrocco corto (verso col 7) e lungo (verso col 0)."""
        pezzo = self.scacchiera.griglia[r_p][c_p]
        if pezzo is None or pezzo.tipo != 'R' or pezzo.has_moved:
            return False
        if r_p != r_a or abs(c_a - c_p) != 2:
            return False
        
        direzione = 1 if c_a > c_p else -1
        col_torre = 7 if direzione == 1 else 0
        c_re_passaggio = c_p + direzione
        c_re_arrivo = c_p + 2 * direzione
        
        if c_a != c_re_arrivo:
            return False
        
        torre = self.scacchiera.griglia[r_p][col_torre]
        if torre is None or torre.tipo != 'T' or torre.colore != pezzo.colore or torre.has_moved:
            return False
        
        # Percorso libero tra Re e Torre
        for c in range(min(c_p, col_torre) + 1, max(c_p, col_torre)):
            if self.scacchiera.griglia[r_p][c] is not None:
                return False
        
        # Re non sotto scacco
        if self.scacchiera.subisce_scacco(pezzo.colore):
            return False
        
        # Caselle attraversate e di arrivo non sotto attacco
        colore_avv = 'N' if pezzo.colore == 'B' else 'B'
        if self.scacchiera.casella_sotto_attacco(r_p, c_re_passaggio, colore_avv):
            return False
        if self.scacchiera.casella_sotto_attacco(r_p, c_re_arrivo, colore_avv):
            return False
        
        # Esegui arrocco
        self.scacchiera.griglia[r_a][c_a] = pezzo
        self.scacchiera.griglia[r_p][c_p] = None
        pezzo.has_moved = True
        
        self.scacchiera.griglia[r_p][c_re_passaggio] = torre
        self.scacchiera.griglia[r_p][col_torre] = None
        torre.has_moved = True
        
        return True

    def gestisci_click(self, evento):
        colonna = evento.x // DIM_CASELLA
        riga = evento.y // DIM_CASELLA
        
        if not (0 <= riga < RIGHE and 0 <= colonna < COLONNE):
            return

        pezzo_cliccato = self.scacchiera.griglia[riga][colonna]

        if self.posizione_selezionata is None:
            if pezzo_cliccato is not None and pezzo_cliccato.colore == self.turno:
                self.posizione_selezionata = (riga, colonna)
        else:
            riga_partenza, col_partenza = self.posizione_selezionata
            
            if (riga, colonna) == (riga_partenza, col_partenza):
                self.posizione_selezionata = None
            elif pezzo_cliccato is not None and pezzo_cliccato.colore == self.turno:
                self.posizione_selezionata = (riga, colonna)
            else:
                pezzo_selezionato = self.scacchiera.griglia[riga_partenza][col_partenza]
                
                # --- Prova Arrocco ---
                arrocco_fatto = False
                if pezzo_selezionato.tipo == 'R' and riga == riga_partenza and abs(colonna - col_partenza) == 2:
                    arrocco_fatto = self.tenta_arrocco(riga_partenza, col_partenza, riga, colonna)
                
                if arrocco_fatto:
                    self.posizione_selezionata = None
                    self.turno = 'N' if self.turno == 'B' else 'B'
                    self.aggiorna_testo_turno()
                    self.aggiorna_momentum()
                    if self.scacchiera.subisce_scacco(self.turno):
                        messagebox.showinfo("Scacco!", f"Attenzione, il Re {'NERO' if self.turno == 'N' else 'BIANCO'} è sotto scacco!")
                    self.disegna_gioco()
                    return
                
                # --- Mossa Normale ---
                if pezzo_selezionato.mossa_valida(riga_partenza, col_partenza, riga, colonna, self.scacchiera.griglia):
                    pezzo_destinazione_salvato = self.scacchiera.griglia[riga][colonna]
                    
                    self.scacchiera.griglia[riga][colonna] = pezzo_selezionato
                    self.scacchiera.griglia[riga_partenza][col_partenza] = None
                    
                    if self.scacchiera.subisce_scacco(self.turno):
                        # Annulla mossa illegale
                        self.scacchiera.griglia[riga_partenza][col_partenza] = pezzo_selezionato
                        self.scacchiera.griglia[riga][colonna] = pezzo_destinazione_salvato
                        self.posizione_selezionata = None
                        messagebox.showwarning("Mossa Illegale", "Mossa vietata! Il tuo Re rimarrebbe sotto scacco.")
                        self.disegna_gioco()
                        return
                    
                    # Mossa confermata
                    pezzo_selezionato.has_moved = True
                    
                    if pezzo_destinazione_salvato is not None:
                        if self.turno == 'B':
                            self.mangiati_dal_bianco.append(pezzo_destinazione_salvato.simbolo)
                        else:
                            self.mangiati_dal_nero.append(pezzo_destinazione_salvato.simbolo)
                        self.aggiorna_contatori_grafici()

                    # Promozione pedone
                    if pezzo_selezionato.tipo == 'P' and (riga == 0 or riga == 7):
                        self.scacchiera.griglia[riga][colonna] = Regina(self.turno, 'Q')
                    
                    self.posizione_selezionata = None
                    self.turno = 'N' if self.turno == 'B' else 'B'
                    self.aggiorna_testo_turno()
                    self.aggiorna_momentum()
                    
                    if self.scacchiera.subisce_scacco(self.turno):
                        messagebox.showinfo("Scacco!", f"Attenzione, il Re {'NERO' if self.turno == 'N' else 'BIANCO'} è sotto scacco!")
                else:
                    self.posizione_selezionata = None
                
        self.disegna_gioco()

    def aggiorna_testo_turno(self):
        self.label_turno.config(text=f"Turno: {'BIANCO' if self.turno == 'B' else 'NERO'}")

    def aggiorna_contatori_grafici(self):
        testo_bianco = "Mangiati dal Bianco: " + " ".join(self.mangiati_dal_bianco)
        testo_nero = "Mangiati dal Nero: " + " ".join(self.mangiati_dal_nero)
        self.label_mangiati_bianchi.config(text=testo_bianco)
        self.label_mangiati_neri.config(text=testo_nero)

    def disegna_gioco(self):
        self.canvas.delete("all")
        for r in range(RIGHE):
            for c in range(COLONNE):
                x1 = c * DIM_CASELLA
                y1 = r * DIM_CASELLA
                x2 = x1 + DIM_CASELLA
                y2 = y1 + DIM_CASELLA
                colore = LEGNO_CHIARO if (r + c) % 2 == 0 else LEGNO_SCURO
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=colore, outline="")
                
                pezzo = self.scacchiera.griglia[r][c]
                if pezzo is not None:
                    is_selected = (self.posizione_selezionata == (r, c))
                    colore_pezzo = pezzo.ottieni_colore_grafico(is_selected)
                    self.canvas.create_text(
                        x1 + DIM_CASELLA // 2, y1 + DIM_CASELLA // 2,
                        text=pezzo.simbolo, font=("Arial", 36, "bold"),
                        fill=colore_pezzo
                    )
        
        # Bordo casella selezionata
        if self.posizione_selezionata:
            r, c = self.posizione_selezionata
            x1 = c * DIM_CASELLA
            y1 = r * DIM_CASELLA
            x2 = x1 + DIM_CASELLA
            y2 = y1 + DIM_CASELLA
            self.canvas.create_rectangle(x1, y1, x2, y2, outline=EVIDENZIA_SELEZIONE, width=4)


if __name__ == "__main__":
    gioco = Gioco()
    gioco.root.mainloop()