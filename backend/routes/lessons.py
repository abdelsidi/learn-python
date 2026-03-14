from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from app import db
from models import Lesson, Exercise, Progress

lessons_bp = Blueprint("lessons", __name__)


@lessons_bp.route("/lessons", methods=["GET"])
@jwt_required()
def get_lessons():
    user_id = int(get_jwt_identity())
    lessons = Lesson.query.order_by(Lesson.order).all()
    completed_ids = {
        p.exercise_id for p in Progress.query.filter_by(user_id=user_id, completed=True).all()
    }

    result = []
    for lesson in lessons:
        exercise_ids = [e.id for e in lesson.exercises]
        completed_count = sum(1 for eid in exercise_ids if eid in completed_ids)
        data = lesson.to_dict()
        data["completed_count"] = completed_count
        result.append(data)

    return jsonify(result), 200


@lessons_bp.route("/lessons/<int:lesson_id>", methods=["GET"])
@jwt_required()
def get_lesson(lesson_id):
    user_id = int(get_jwt_identity())
    lesson = Lesson.query.get_or_404(lesson_id)
    completed_ids = {
        p.exercise_id for p in Progress.query.filter_by(user_id=user_id, completed=True).all()
    }

    saved_code = {
        p.exercise_id: p.last_code
        for p in Progress.query.filter_by(user_id=user_id).all()
        if p.last_code
    }

    data = lesson.to_dict(include_exercises=True)
    for ex in data["exercises"]:
        ex["completed"] = ex["id"] in completed_ids
        if ex["id"] in saved_code:
            ex["starter_code"] = saved_code[ex["id"]]
    return jsonify(data), 200


@lessons_bp.route("/progress", methods=["GET"])
@jwt_required()
def get_progress():
    user_id = int(get_jwt_identity())
    total_exercises = Exercise.query.count()
    completed = Progress.query.filter_by(user_id=user_id, completed=True).count()
    return jsonify({"total": total_exercises, "completed": completed}), 200
