from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'

# Simulazione della banca
class Bancomat:
    def __init__(self):
        self.saldo = 2400.0  # saldo iniziale aggiornato a 2400
        self.pin = "1234"
        self.storico_transazioni = []
        self.totale_prelievi_oggi = 0.0
        self.data_ultimo_prelievo = None

    def verifica_pin(self, pin_inserito):
        return pin_inserito == self.pin

    def preleva(self, importo):
        oggi = datetime.now().date()
        # Reset del totale giornaliero se cambia il giorno
        if self.data_ultimo_prelievo != oggi:
            self.totale_prelievi_oggi = 0.0
            self.data_ultimo_prelievo = oggi

        if importo <= 0:
            return "L'importo deve essere maggiore di zero."
        if importo > 200:
            return "Il prelievo massimo per operazione è di 200€."
        if self.totale_prelievi_oggi + importo > 500:
            return "Hai raggiunto il limite giornaliero di prelievo di 500€."
        if importo > self.saldo:
            return "Saldo insufficiente."
        else:
            self.saldo -= importo
            self.totale_prelievi_oggi += importo
            self.storico_transazioni.append(f"Prelievo: {importo}€")
            return f"Prelievo di {importo}€ effettuato. Saldo attuale: {self.saldo}€"

    def versa(self, importo):
        if importo <= 0:
            return "L'importo deve essere maggiore di zero."
        else:
            self.saldo += importo
            self.storico_transazioni.append(f"Versamento: {importo}€")
            return f"Versamento di {importo}€ effettuato. Saldo attuale: {self.saldo}€"

    def bonifico(self, destinatario, importo):
        if importo <= 0:
            return "L'importo deve essere maggiore di zero."
        elif importo > self.saldo:
            return "Saldo insufficiente."
        else:
            self.saldo -= importo
            self.storico_transazioni.append(f"Bonifico di {importo}€ a {destinatario}")
            return f"Bonifico di {importo}€ a {destinatario} effettuato. Saldo attuale: {self.saldo}€"

    def ricarica_telefonica(self, numero, importo):
        if importo <= 0:
            return "L'importo deve essere maggiore di zero."
        elif importo > self.saldo:
            return "Saldo insufficiente."
        else:
            self.saldo -= importo
            self.storico_transazioni.append(f"Ricarica telefonica di {importo}€ al numero {numero}")
            return f"Ricarica di {importo}€ al numero {numero} effettuata. Saldo attuale: {self.saldo}€"

    def mostra_saldo(self):
        return f"Saldo attuale: {self.saldo}€"

    def mostra_storico(self):
        return "\n".join(self.storico_transazioni) if self.storico_transazioni else "Nessuna transazione effettuata."


bancomat = Bancomat()

# Home Page con il Login
@app.route('/')
def home():
    return render_template('index.html')

# Pagina di Login
@app.route('/login', methods=['POST'])
def login():
    pin = request.form.get('pin')
    if bancomat.verifica_pin(pin):
        return redirect(url_for('operazioni'))
    else:
        flash("PIN errato! Riprova.")
        return redirect(url_for('home'))

# Operazioni disponibili dopo il login
@app.route('/operazioni')
def operazioni():
    return render_template('operazioni.html', saldo=bancomat.mostra_saldo())

# Prelievo
@app.route('/prelievo', methods=['POST'])
def prelievo():
    importo = float(request.form.get('importo'))
    risultato = bancomat.preleva(importo)
    flash(risultato)
    return redirect(url_for('operazioni'))

# Versamento
@app.route('/versamento', methods=['POST'])
def versamento():
    importo = float(request.form.get('importo'))
    risultato = bancomat.versa(importo)
    flash(risultato)
    return redirect(url_for('operazioni'))

# Bonifico
@app.route('/bonifico', methods=['POST'])
def bonifico():
    destinatario = request.form.get('destinatario')
    importo = float(request.form.get('importo'))
    risultato = bancomat.bonifico(destinatario, importo)
    if "Saldo insufficiente" in risultato:
        flash(risultato, "error")
    else:
        flash(risultato, "success")
    return redirect(url_for('operazioni'))

# Ricarica telefonica
@app.route('/ricarica', methods=['POST'])
def ricarica():
    numero = request.form.get('numero')
    importo = float(request.form.get('importo'))
    risultato = bancomat.ricarica_telefonica(numero, importo)
    if "Saldo insufficiente" in risultato:
        flash(risultato, "error")
    else:
        flash(risultato, "success")
    return redirect(url_for('operazioni'))

# Storico delle transazioni
@app.route('/storico')
def storico():
    return render_template('storico.html', storico=bancomat.mostra_storico())

# Logout
@app.route('/logout')
def logout():
    return redirect(url_for('home'))

if __name__ == "__main__":
    app.run(debug=True)
