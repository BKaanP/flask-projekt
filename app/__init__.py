from flask import Flask, render_template, request, redirect, url_for, jsonify
from .models import db, Ziele, Historie
from sqlalchemy import or_, desc, asc, func
from datetime import datetime, timedelta


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')
    db.init_app(app)

    @app.route('/')
    def home():
        ziele = Ziele.query.all()
        ziele_list = []
        for ziel in ziele:
            anregung_entry = Historie.query.filter_by(ziel_id=ziel.id).order_by(Historie.datum_aenderung.desc()).first()
            anregung = anregung_entry.anregung if anregung_entry else ''
            ziele_list.append({
                "id": ziel.id,
                "abteilung": ziel.abteilung,
                "aussage": ziel.aussage,
                "kriterien": ziel.kriterien,
                "bewertung": ziel.bewertung,
                "kommentare": ziel.kommentare,
                "letzte_aenderung": ziel.letzte_aenderung.strftime('%d.%m.%Y') if ziel.letzte_aenderung else 'N/A',
                "geaendert_von": ziel.geaendert_von,
                "anregung": anregung
            })
        return render_template('home.html', ziele=ziele_list)

    @app.route('/search', methods=['GET'])
    def search():
        abteilung = request.args.get('abteilung', '')
        aussage = request.args.get('aussage', '')
        kriterien = request.args.get('kriterien', '')
        kommentar = request.args.get('kommentar', '')
        geaendert_von = request.args.get('geaendert_von', '')
        anregung = request.args.get('anregung', '')
        sort_bewertung = request.args.get('sortBewertung', '')
        sort_datum = request.args.get('sortDatum', '')
        sort_column = request.args.get('sortColumn', '')
        sort_order = request.args.get('sortOrder', 'asc')

        query = Ziele.query

        if abteilung:
            query = query.filter(Ziele.abteilung.ilike(f"%{abteilung}%"))
        if aussage:
            query = query.filter(Ziele.aussage.ilike(f"%{aussage}%"))
        if kriterien:
            query = query.filter(Ziele.kriterien.ilike(f"%{kriterien}%"))
        if kommentar:
            query = query.filter(Ziele.kommentare.ilike(f"%{kommentar}%"))
        if geaendert_von:
            query = query.filter(Ziele.geaendert_von.ilike(f"%{geaendert_von}%"))

        if anregung:
            query = query.join(Historie).filter(Historie.anregung.ilike(f"%{anregung}%"))

        if sort_column:
            sort_attr = getattr(Ziele, sort_column, None)
            if not sort_attr and sort_column == 'anregung':
                sort_attr = func.max(Historie.anregung)
                query = query.outerjoin(Historie)
                query = query.group_by(Ziele.id)
            if sort_attr:
                if sort_order == 'asc':
                    query = query.order_by(asc(sort_attr))
                else:
                    query = query.order_by(desc(sort_attr))

        ziele = query.all()

        ziele_list = []
        for ziel in ziele:
            anregung_entry = Historie.query.filter_by(ziel_id=ziel.id).order_by(Historie.datum_aenderung.desc()).first()
            anregung = anregung_entry.anregung if anregung_entry else ''
            ziele_list.append({
                "id": ziel.id,
                "abteilung": ziel.abteilung,
                "aussage": ziel.aussage,
                "kriterien": ziel.kriterien,
                "bewertung": ziel.bewertung,
                "kommentare": ziel.kommentare,
                "letzte_aenderung": ziel.letzte_aenderung.strftime('%d.%m.%Y') if ziel.letzte_aenderung else 'N/A',
                "geaendert_von": ziel.geaendert_von,
                "anregung": anregung
            })

        return jsonify(ziele=ziele_list)

    @app.route('/delete_ziel/<int:ziel_id>', methods=['GET', 'DELETE'])
    def delete_ziel(ziel_id):
        ziel = Ziele.query.get_or_404(ziel_id)
        Historie.query.filter_by(ziel_id=ziel.id).delete()
        db.session.delete(ziel)
        db.session.commit()
        return '', 204

    @app.route('/get_ziel/<int:ziel_id>', methods=['GET'])
    def get_ziel(ziel_id):
        ziel = Ziele.query.get_or_404(ziel_id)
        ziel_data = {
            "id": ziel.id,
            "abteilung": ziel.abteilung,
            "aussage": ziel.aussage,
            "kriterien": ziel.kriterien,
            "bewertung": ziel.bewertung,
            "einschaetzung": ziel.einschaetzung,
            "kommentare": ziel.kommentare,
            "geaendert_von": ziel.geaendert_von
        }
        return jsonify(ziel=ziel_data)

    @app.route('/add_ziel', methods=['POST'])
    def add_ziel():
        data = request.get_json()
        abteilung = data['abteilung']
        aussage = data['aussage']
        kriterien = data['kriterien']
        bewertung = data['bewertung']
        einschaetzung = data.get('einschaetzung', "")
        kommentare = data.get('kommentare', "")
        geaendert_von = data.get('geaendert_von', "System")

        ziel = Ziele(
            abteilung=abteilung,
            aussage=aussage,
            kriterien=kriterien,
            bewertung=int(bewertung),
            einschaetzung=einschaetzung,
            kommentare=kommentare,
            geaendert_von=geaendert_von,
            letzte_aenderung=datetime.utcnow()
        )
        db.session.add(ziel)
        db.session.commit()
        return '', 204

    from datetime import datetime

    @app.route('/edit_ziel/<int:ziel_id>', methods=['POST'])
    def edit_ziel(ziel_id):
        ziel = Ziele.query.get_or_404(ziel_id)

        data = request.get_json()
        if data:
            historie = Historie(
                ziel=ziel,
                datum_aenderung=ziel.letzte_aenderung or datetime.utcnow(),
                geaendert_von=ziel.geaendert_von,
                einschaetzung=ziel.einschaetzung,
                bewertung=ziel.bewertung,
                anregung=data.get('anregung', '')
            )
            db.session.add(historie)

            ziel.abteilung = data['abteilung']
            ziel.aussage = data['aussage']
            ziel.kriterien = data['kriterien']
            ziel.bewertung = int(data['bewertung'])
            ziel.einschaetzung = data.get('einschaetzung', ziel.einschaetzung)
            ziel.geaendert_von = data.get('geaendert_von', ziel.geaendert_von)
            ziel.kommentare = data.get('kommentare', ziel.kommentare)
            ziel.letzte_aenderung = datetime.utcnow()

            db.session.commit()
            return '', 204

        return 'Bad Request', 400

    @app.route('/view_history/<int:ziel_id>')
    def view_history(ziel_id):
        ziel = Ziele.query.get_or_404(ziel_id)
        historie_entries = Historie.query.filter_by(ziel_id=ziel.id).all()
        return render_template('history.html', ziel=ziel, historie_entries=historie_entries)

    with app.app_context():
        db.create_all()

    @app.route('/get_historie/<int:ziel_id>', methods=['GET'])
    def get_historie(ziel_id):
        ziel = Ziele.query.get_or_404(ziel_id)
        historie_entries = Historie.query.filter_by(ziel_id=ziel.id).all()
        historie_list = [
            {
                "datum_aenderung": entry.datum_aenderung.strftime('%d.%m.%Y') if entry.datum_aenderung else None,
                "geaendert_von": entry.geaendert_von,
                "bewertung": entry.bewertung,
                "einschaetzung": entry.einschaetzung,
                "anregung": entry.anregung
            }
            for entry in historie_entries
        ]
        return jsonify(historie=historie_list)

    @app.route('/grafik')
    def grafik():
        abteilungen = db.session.query(Ziele.abteilung).distinct().all()
        abteilungen_list = [a[0] for a in abteilungen]

        default_end_date = datetime.now().date()
        default_start_date = default_end_date - timedelta(days=30)

        return render_template('grafik.html', abteilungen=abteilungen_list,
                               default_start_date=default_start_date.strftime('%Y-%m-%d'),
                               default_end_date=default_end_date.strftime('%Y-%m-%d'))

    @app.route('/get_chart_data', methods=['POST'])
    def get_chart_data():
        data = request.get_json()
        abteilungen = data.get('abteilungen', [])
        start_date = data.get('startDate')
        end_date = data.get('endDate')

        print('Empfangene Filterparameter:')
        print('Abteilungen:', abteilungen)
        print('Startdatum:', start_date)
        print('Enddatum:', end_date)

        query = db.session.query(
            Historie.datum_aenderung,
            Historie.bewertung,
            Ziele.abteilung
        ).join(Ziele)

        if abteilungen:
            query = query.filter(Ziele.abteilung.in_(abteilungen))

        if start_date:
            query = query.filter(Historie.datum_aenderung >= datetime.strptime(start_date, '%Y-%m-%d'))
        if end_date:
            end_date_dt = datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)
            query = query.filter(Historie.datum_aenderung < end_date_dt)

        result = query.all()

        print('Anzahl gefundener Einträge:', len(result))

        daten = {}
        for datum_aenderung, bewertung, abteilung in result:
            if abteilung not in daten:
                daten[abteilung] = []
            daten[abteilung].append({
                'datum': datum_aenderung.isoformat(),
                'bewertung': bewertung
            })

        return jsonify({'daten': daten})

    return app
