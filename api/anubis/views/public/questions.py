from flask import Blueprint
from sqlalchemy.exc import IntegrityError, DataError

from anubis.models import db, AssignedStudentQuestion, AssignedQuestionResponse, User
from anubis.utils.users.auth import require_user, current_user
from anubis.utils.decorators import json_endpoint
from anubis.utils.http.https import success_response, error_response

questions = Blueprint("public-questions", __name__, url_prefix="/public/questions")


@questions.route("/save/<string:id>", methods=["POST"])
@require_user()
@json_endpoint(required_fields=[("response", str)])
def public_questions_save(id: str, response: str):
    """
    body = {
      response: str
    }

    :param id:
    :return:
    """
    user: User = current_user()

    assigned_question = AssignedStudentQuestion.query.filter(
        AssignedStudentQuestion.id == id,
    ).first()

    if assigned_question is None:
        return error_response("Assigned question does not exist")

    if (
            not (user.is_admin or user.is_superuser)
            and assigned_question.owner_id != user.id
    ):
        return error_response("Assigned question does not exist")

    res = AssignedQuestionResponse(
        assigned_question_id=assigned_question.id,
        response=response
    )
    db.session.add(res)

    try:
        db.session.commit()
    except (IntegrityError, DataError):
        return error_response("Server was unable to save your response.")

    return success_response({
        "status": "Response Saved",
    })
