from flask import Blueprint
from utils.auth import internal_required
from app.controllers import counsellor_notes_controller

api_bp = Blueprint('api_bp', __name__)

# POST /applications/<applicationId>/notes
api_bp.route('/applications/<applicationId>/notes', methods=['POST'])(
    internal_required(counsellor_notes_controller.create_note)
)

# GET /applications/<applicationId>/notes
api_bp.route('/applications/<applicationId>/notes', methods=['GET'])(
    internal_required(counsellor_notes_controller.get_notes)
)

# GET /applications/<applicationId>/notes/summary
api_bp.route('/applications/<applicationId>/notes/summary', methods=['GET'])(
    internal_required(counsellor_notes_controller.get_notes_summary)
)

# PATCH /applications/<applicationId>/notes/<noteId>
api_bp.route('/applications/<applicationId>/notes/<noteId>', methods=['PATCH'])(
    internal_required(counsellor_notes_controller.edit_note)
)

# DELETE /applications/<applicationId>/notes/<noteId>
api_bp.route('/applications/<applicationId>/notes/<noteId>', methods=['DELETE'])(
    internal_required(counsellor_notes_controller.delete_note)
)
