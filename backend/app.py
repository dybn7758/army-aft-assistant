import os

from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, request
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

with app.app_context():
    db.create_all()


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

    score = AFTTest(
        user_id=data["user_id"],
        test_date=datetime.strptime(
            data["test_date"], "%Y-%m-%d"
        ).date(),
        deadlift=data.get("deadlift"),
        hrp=data.get("hrp"),
        sprint_drag_carry=data.get("sprint_drag_carry"),
        plank=data.get("plank"),
        two_mile_run=data.get("two_mile_run"),
        total_score=data.get("total_score"),
    )

    db.session.add(score)
    db.session.commit()

    return {
        "id": score.id,
        "user_id": score.user_id,
        "total_score": score.total_score
    }, 201

@app.get("/api/aft-scores/<int:user_id>")
def get_aft_scores(user_id):
    scores = AFTTest.query.filter_by(
        user_id=user_id
    ).order_by(AFTTest.test_date.asc()).all()

    return [
        {
            "id": score.id,
            "test_date": score.test_date.isoformat(),
            "deadlift": score.deadlift,
            "hrp": score.hrp,
            "sprint_drag_carry": score.sprint_drag_carry,
            "plank": score.plank,
            "two_mile_run": score.two_mile_run,
            "total_score": score.total_score,
        }
        for score in scores
    ]



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
    app.run(debug=True)