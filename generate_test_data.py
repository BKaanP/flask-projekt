from app import create_app
from app.models import db, Ziele, Historie
from datetime import datetime, timedelta
import random


app = create_app()

with app.app_context():
    neues_ziel = Ziele(
        abteilung='Testabteilung4',
        aussage='Testaussage4',
        kriterien='Testkriterien4',
        bewertung=7,
        einschaetzung='Initiale Einschätzung4',
        letzte_aenderung=datetime.now(),
        geaendert_von='Tester4',
        kommentare='Start des Tests4'
    )
    db.session.add(neues_ziel)
    db.session.commit()
    print(f'Neues Ziel mit ID {neues_ziel.id} erstellt.')

    anzahl_eintraege = 10
    start_datum = datetime(2024, 10, 1)

    for i in range(anzahl_eintraege):
        historie_eintrag = Historie(
            ziel_id=neues_ziel.id,
            datum_aenderung=start_datum + timedelta(days=i),
            geaendert_von=f'Tester {i}',
            einschaetzung=f'Einschätzung {i}',
            bewertung=random.randint(1, 10),
            anregung=f'Anregung {i}'
        )
        db.session.add(historie_eintrag)

    db.session.commit()
    print(f'{anzahl_eintraege} Historie-Einträge für Ziel ID {neues_ziel.id} erstellt.')
