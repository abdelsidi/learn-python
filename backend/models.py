from app import db
from datetime import datetime
import bcrypt

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    progress = db.relationship("Progress", backref="user", lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.hashpw(
            password.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def check_password(self, password):
        return bcrypt.checkpw(
            password.encode("utf-8"), self.password_hash.encode("utf-8")
        )

    def to_dict(self):
        completed = [p.exercise_id for p in self.progress if p.completed]
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "completed_exercises": completed,
        }


class Lesson(db.Model):
    __tablename__ = "lessons"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    order = db.Column(db.Integer, nullable=False)
    exercises = db.relationship("Exercise", backref="lesson", lazy=True, order_by="Exercise.order")

    def to_dict(self, include_exercises=False):
        data = {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "order": self.order,
            "exercise_count": len(self.exercises),
        }
        if include_exercises:
            data["exercises"] = [e.to_dict() for e in self.exercises]
        return data


class Exercise(db.Model):
    __tablename__ = "exercises"
    id = db.Column(db.Integer, primary_key=True)
    lesson_id = db.Column(db.Integer, db.ForeignKey("lessons.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    starter_code = db.Column(db.Text, default="")
    expected_output = db.Column(db.Text)
    hint = db.Column(db.Text)
    order = db.Column(db.Integer, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "lesson_id": self.lesson_id,
            "title": self.title,
            "description": self.description,
            "starter_code": self.starter_code,
            "hint": self.hint,
            "order": self.order,
        }


class Progress(db.Model):
    __tablename__ = "progress"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    exercise_id = db.Column(db.Integer, db.ForeignKey("exercises.id"), nullable=False)
    completed = db.Column(db.Boolean, default=False)
    last_code = db.Column(db.Text)
    completed_at = db.Column(db.DateTime)
    __table_args__ = (db.UniqueConstraint("user_id", "exercise_id"),)
