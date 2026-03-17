from flask import Blueprint
from utils.auth import internal_required
from api.controllers import counsellor_notes_controller, user_controller

api_bp = Blueprint('api_bp', __name__)

# Users routes
api_bp.route('/users', methods=['POST'])(
    internal_required(user_controller.create_user)
)

api_bp.route('/users', methods=['GET'])(
    internal_required(user_controller.get_users)
)

api_bp.route('/users/<userId>', methods=['GET'])(
    internal_required(user_controller.get_user)
)

api_bp.route('/users/<userId>', methods=['PATCH'])(
    internal_required(user_controller.edit_user)
)

api_bp.route('/users/<userId>', methods=['DELETE'])(
    internal_required(user_controller.delete_user)
)

# Notes routes
api_bp.route('/applications/<applicationId>/notes', methods=['POST'])(
    internal_required(counsellor_notes_controller.create_note)
)

api_bp.route('/applications/<applicationId>/notes', methods=['GET'])(
    internal_required(counsellor_notes_controller.get_notes)
)

api_bp.route('/applications/<applicationId>/notes/summary', methods=['GET'])(
    internal_required(counsellor_notes_controller.get_notes_summary)
)

api_bp.route('/applications/<applicationId>/notes/<noteId>', methods=['PATCH'])(
    internal_required(counsellor_notes_controller.edit_note)
)

api_bp.route('/applications/<applicationId>/notes/<noteId>', methods=['DELETE'])(
    internal_required(counsellor_notes_controller.delete_note)
)
