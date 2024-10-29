from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Ziele(db.Model):
    __tablename__ = 'ziele'
    id = db.Column(db.Integer, primary_key=True)
    abteilung = db.Column(db.String(50))
    aussage = db.Column(db.String(255))
    kriterien = db.Column(db.String(255))
    bewertung = db.Column(db.Integer)
    einschaetzung = db.Column(db.String(255))
    letzte_aenderung = db.Column(db.DateTime)
    geaendert_von = db.Column(db.String(50))
    kommentare = db.Column(db.Text)

    historie_entries = db.relationship('Historie', backref='ziel', lazy=True)


class Historie(db.Model):
    __tablename__ = 'historie'
    id = db.Column(db.Integer, primary_key=True)
    ziel_id = db.Column(db.Integer, db.ForeignKey('ziele.id'))
    datum_aenderung = db.Column(db.DateTime)
    geaendert_von = db.Column(db.String(50))
    einschaetzung = db.Column(db.String(255))
    bewertung = db.Column(db.Integer)
    anregung = db.Column(db.Text)
