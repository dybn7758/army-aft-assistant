import os

from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request
from flask_migrate import Migrate
from flask_cors import CORS
from sqlalchemy import URL

from src.database import db
from src.models import User, AFTTest
from src.aft_calculator import calculate_event_score, get_age_group
from src.rag import ask_rag


load_dotenv()

app = Flask(__name__)

CORS(app)

database_url = URL.create(
    drivername="postgresql+psycopg2",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME"),
)

app.config["SQLALCHEMY_DATABASE_URI"] = database_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False


db.init_app(app)

migrate = Migrate(app, db)


def calculate_age(birth_date, test_date):
    age = test_date.year - birth_date.year

    if (
        test_date.month,
        test_date.day,
    ) < (
        birth_date.month,
        birth_date.day,
    ):
        age -= 1

    return age


@app.get("/api/health")
def health():
    return {"status": "ok"}

@app.post("/api/users")
def create_user():
    data = request.get_json()

    user = User(
        username=data["username"],
        birth_date=datetime.strptime(
            data["birth_date"], "%Y-%m-%d"
        ).date(),
        gender=data["gender"],
        component=data.get("component"),
        mos=data.get("mos"),
    )

    db.session.add(user)
    db.session.commit()

    return {
        "id": user.id,
        "username": user.username
    }, 201

@app.post("/api/aft-scores")
def create_aft_score():
    data = request.get_json()

    try:
        user_id = data["user_id"]
        test_date = datetime.strptime(
            data["test_date"],
            "%Y-%m-%d",
        ).date()

        user = db.session.get(User, user_id)

        if not user:
            return {
                "error": "User not found"
            }, 404

        age = calculate_age(
            user.birth_date,
            test_date,
        )

        standard_type = data.get(
            "standard_type",
            "general",
        )

        deadlift_performance = data["deadlift_performance"]
        hrp_performance = data["hrp_performance"]
        sdc_performance = data["sdc_performance"]
        plank_performance = data["plank_performance"]
        two_mile_run_performance = data[
            "two_mile_run_performance"
        ]

        deadlift_score = calculate_event_score(
            age=age,
            gender=user.gender,
            event="mdl",
            performance=deadlift_performance,
            standard_type=standard_type,
        )

        hrp_score = calculate_event_score(
            age=age,
            gender=user.gender,
            event="hrp",
            performance=hrp_performance,
            standard_type=standard_type,
        )

        sdc_score = calculate_event_score(
            age=age,
            gender=user.gender,
            event="sdc",
            performance=sdc_performance,
            standard_type=standard_type,
        )

        plank_score = calculate_event_score(
            age=age,
            gender=user.gender,
            event="plank",
            performance=plank_performance,
            standard_type=standard_type,
        )

        two_mile_run_score = calculate_event_score(
            age=age,
            gender=user.gender,
            event="two_mile_run",
            performance=two_mile_run_performance,
            standard_type=standard_type,
        )

        total_score = sum([
            deadlift_score,
            hrp_score,
            sdc_score,
            plank_score,
            two_mile_run_score,
        ])

        aft_test = AFTTest(
            user_id=user.id,
            test_date=test_date,

            deadlift_performance=deadlift_performance,
            hrp_performance=hrp_performance,
            sdc_performance=sdc_performance,
            plank_performance=plank_performance,
            two_mile_run_performance=two_mile_run_performance,

            deadlift_score=deadlift_score,
            hrp_score=hrp_score,
            sdc_score=sdc_score,
            plank_score=plank_score,
            two_mile_run_score=two_mile_run_score,

            total_score=total_score,
        )

        db.session.add(aft_test)
        db.session.commit()

        return {
            "id": aft_test.id,
            "user_id": aft_test.user_id,
            "test_date": aft_test.test_date.isoformat(),
            "age": age,
            "age_group": get_age_group(age),
            "standard_type": standard_type,
            "events": {
                "deadlift": {
                    "performance": aft_test.deadlift_performance,
                    "score": aft_test.deadlift_score,
                },
                "hrp": {
                    "performance": aft_test.hrp_performance,
                    "score": aft_test.hrp_score,
                },
                "sdc": {
                    "performance": aft_test.sdc_performance,
                    "score": aft_test.sdc_score,
                },
                "plank": {
                    "performance": aft_test.plank_performance,
                    "score": aft_test.plank_score,
                },
                "two_mile_run": {
                    "performance": aft_test.two_mile_run_performance,
                    "score": aft_test.two_mile_run_score,
                },
            },
            "total_score": aft_test.total_score,
        }, 201

    except (KeyError, ValueError) as error:
        db.session.rollback()

        return {
            "error": str(error)
        }, 400

    except Exception as error:
        db.session.rollback()

        return {
            "error": str(error)
        }, 500

@app.get("/api/aft-scores/<int:user_id>")
def get_aft_scores(user_id):
    user = db.session.get(User, user_id)

    if not user:
        return {
            "error": "User not found"
        }, 404

    scores = (
        AFTTest.query
        .filter_by(user_id=user_id)
        .order_by(AFTTest.test_date.asc())
        .all()
    )

    return [
        {
            "id": score.id,
            "test_date": score.test_date.isoformat(),

            "deadlift": {
                "performance": score.deadlift_performance,
                "score": score.deadlift_score,
            },

            "hrp": {
                "performance": score.hrp_performance,
                "score": score.hrp_score,
            },

            "sdc": {
                "performance": score.sdc_performance,
                "score": score.sdc_score,
            },

            "plank": {
                "performance": score.plank_performance,
                "score": score.plank_score,
            },

            "two_mile_run": {
                "performance": score.two_mile_run_performance,
                "score": score.two_mile_run_score,
            },

            "total_score": score.total_score,
        }

        for score in scores
    ]

@app.get("/api/users/<int:user_id>")
def get_user(user_id):
    user = db.session.get(User, user_id)

    if not user:
        return {
            "error": "User not found"
        }, 404

    return {
        "id": user.id,
        "username": user.username,
        "birth_date": user.birth_date.isoformat(),
        "gender": user.gender,
        "component": user.component,
        "mos": user.mos,
    }


@app.post("/api/aft/calculate")
def calculate_aft():
    data = request.get_json()

    try:
        score = calculate_event_score(
            age=data["age"],
            gender=data["gender"],
            event=data["event"],
            performance=data["performance"],
            standard_type=data.get("standard_type", "general"),
        )

        return {
            "age": data["age"],
            "age_group": get_age_group(data["age"]),
            "gender": data["gender"],
            "event": data["event"],
            "performance": data["performance"],
            "standard_type": data.get("standard_type", "general"),
            "score": score,
        }

    except (KeyError, ValueError) as error:
        return {
            "error": str(error)
        }, 400


@app.post("/api/chat")
def chat():
    data = request.get_json()

    message = data.get("message")
    user_id = data.get("user_id")
    session_id = data.get("session_id")

    if not message:
        return {"error": "message is required"}, 400

    if not user_id:
        return {"error": "user_id is required"}, 400

    if not session_id:
        return {"error": "session_id is required"}, 400

    try:
        result = ask_rag(
            question=message,
            user_id=user_id,
            session_id=session_id,
        )

        return result

    except Exception as error:
        return {
            "error": str(error)
        }, 500

        
if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,
    )