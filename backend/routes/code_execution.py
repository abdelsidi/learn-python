import requests
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from app import db
from models import Exercise, Progress

code_bp = Blueprint("code", __name__)

PISTON_API = "https://emkc.org/api/v2/piston/execute"


def run_code(code: str) -> dict:
    try:
        resp = requests.post(
            PISTON_API,
            json={
                "language": "python",
                "version": "3.10.0",
                "files": [{"content": code}],
            },
            timeout=10,
        )
        resp.raise_for_status()
        result = resp.json()
        run = result.get("run", {})
        return {
            "stdout": run.get("stdout", ""),
            "stderr": run.get("stderr", ""),
            "code": run.get("code", 0),
        }
    except requests.exceptions.Timeout:
        return {"stdout": "", "stderr": "Execution timed out.", "code": 1}
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "code": 1}


@code_bp.route("/run", methods=["POST"])
@jwt_required()
def run():
    data = request.get_json()
    code = data.get("code", "")
    if not code.strip():
        return jsonify({"error": "No code provided"}), 400

    result = run_code(code)
    return jsonify(result), 200


@code_bp.route("/submit/<int:exercise_id>", methods=["POST"])
@jwt_required()
def submit(exercise_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    code = data.get("code", "")

    exercise = Exercise.query.get_or_404(exercise_id)
    result = run_code(code)

    passed = False
    feedback = ""

    if result["code"] != 0:
        feedback = result["stderr"] or "Runtime error"
    elif exercise.expected_output:
        actual = result["stdout"].strip()
        expected = exercise.expected_output.strip()
        passed = actual == expected
        if passed:
            feedback = "Correct! Well done."
        else:
            feedback = f"Output didn't match.\nExpected:\n{expected}\n\nGot:\n{actual}"
    else:
        # No expected output — just check it runs without error
        passed = True
        feedback = "Looks good! No errors."

    # Save progress
    progress = Progress.query.filter_by(user_id=user_id, exercise_id=exercise_id).first()
    if not progress:
        progress = Progress(user_id=user_id, exercise_id=exercise_id)
        db.session.add(progress)

    progress.last_code = code
    if passed and not progress.completed:
        progress.completed = True
        progress.completed_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "passed": passed,
        "feedback": feedback,
        "stdout": result["stdout"],
        "stderr": result["stderr"],
    }), 200
