from src.database import db


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(
        db.String(100),
        nullable=False,
        unique=True
    )
    birth_date = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    component = db.Column(db.String(50))
    mos = db.Column(db.String(20))

    aft_tests = db.relationship(
        "AFTTest",
        backref="user",
        lazy=True,
        cascade="all, delete-orphan"
    )


class AFTTest(db.Model):
    __tablename__ = "aft_tests"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    test_date = db.Column(db.Date, nullable=False)

    # Raw performance
    deadlift_performance = db.Column(db.Integer)
    hrp_performance = db.Column(db.Integer)
    sdc_performance = db.Column(db.String(20))
    plank_performance = db.Column(db.String(20))
    two_mile_run_performance = db.Column(db.String(20))

    # Calculated points
    deadlift_score = db.Column(db.Integer)
    hrp_score = db.Column(db.Integer)
    sdc_score = db.Column(db.Integer)
    plank_score = db.Column(db.Integer)
    two_mile_run_score = db.Column(db.Integer)

    total_score = db.Column(db.Integer)