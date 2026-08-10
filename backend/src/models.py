from src.database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    component = db.Column(db.String(50))
    mos = db.Column(db.String(20))


class AFTTest(db.Model):
    __tablename__ = "aft_tests"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    test_date = db.Column(db.Date, nullable=False)
    deadlift = db.Column(db.Integer)
    hrp = db.Column(db.Integer)
    sprint_drag_carry = db.Column(db.Integer)
    plank = db.Column(db.Integer)
    two_mile_run = db.Column(db.String(20))
    total_score = db.Column(db.Integer)