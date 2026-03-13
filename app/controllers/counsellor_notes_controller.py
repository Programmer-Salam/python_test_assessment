from flask import request, jsonify
from utils.db import applications_collection, counsellor_notes_collection
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone

def _get_now():
    # Return ISO format string for current UTC time
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def create_note(applicationId):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON request body"}), 400

    required_fields = ["authorName", "authorEmail", "category", "content"]
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return jsonify({"error": f"Missing or empty required field: {field}"}), 400

    valid_categories = ["General", "Document Follow-up", "Payment Issue", "Visa Assistance", "Urgent"]
    if data["category"] not in valid_categories:
        return jsonify({"error": f"Invalid category"}), 400

    # Verify applicationId exists
    app_query = {"applicationId": applicationId}
    try:
        if not applications_collection.find_one({"_id": ObjectId(applicationId)}) and not applications_collection.find_one(app_query):
            return jsonify({"error": f"Application with ID {applicationId} not found"}), 404
    except InvalidId:
        if not applications_collection.find_one(app_query):
            return jsonify({"error": f"Application with ID {applicationId} not found"}), 404

    note = {
        "applicationId": applicationId,
        "authorName": data["authorName"].strip(),
        "authorEmail": data["authorEmail"].strip(),
        "category": data["category"],
        "content": data["content"].strip(),
        "isPinned": bool(data.get("isPinned", False)),
        "isDeleted": False,
        "createdAt": _get_now(),
        "updatedAt": _get_now()
    }

    result = counsellor_notes_collection.insert_one(note)
    note["_id"] = str(result.inserted_id)

    return jsonify(note), 201

def get_notes(applicationId):
    try:
        page = max(1, int(request.args.get("page", 1)))
        limit = min(50, max(1, int(request.args.get("limit", 10))))
    except ValueError:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    query = {"applicationId": applicationId, "isDeleted": {"$ne": True}}

    total_notes = counsellor_notes_collection.count_documents(query)
    total_pages = (total_notes + limit - 1) // limit

    cursor = counsellor_notes_collection.find(query)
    cursor.sort([("isPinned", -1), ("createdAt", -1)])
    cursor.skip((page - 1) * limit).limit(limit)

    notes = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        notes.append(doc)

    return jsonify({
        "notes": notes,
        "totalNotes": total_notes,
        "totalPages": total_pages,
        "currentPage": page
    }), 200

def edit_note(applicationId, noteId):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON request body"}), 400

    try:
        obj_id = ObjectId(noteId)
    except InvalidId:
        return jsonify({"error": "Invalid noteId format"}), 400

    update_fields = {}
    valid_fields = ["authorName", "authorEmail", "category", "content", "isPinned"]

    for field in valid_fields:
        if field in data:
            if field == "category":
                valid_categories = ["General", "Document Follow-up", "Payment Issue", "Visa Assistance", "Urgent"]
                if data["category"] not in valid_categories:
                    return jsonify({"error": "Invalid category"}), 400
            elif field == "isPinned":
                update_fields[field] = bool(data[field])
                continue
            update_fields[field] = data[field].strip() if isinstance(data[field], str) else data[field]

    if not update_fields:
        return jsonify({"error": "No valid fields provided for update"}), 400

    update_fields["updatedAt"] = _get_now()

    result = counsellor_notes_collection.update_one(
        {"_id": obj_id, "applicationId": applicationId, "isDeleted": {"$ne": True}},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Note not found or deleted"}), 404

    note = counsellor_notes_collection.find_one({"_id": obj_id})
    note["_id"] = str(note["_id"])
    return jsonify(note), 200

def delete_note(applicationId, noteId):
    try:
        obj_id = ObjectId(noteId)
    except InvalidId:
        return jsonify({"error": "Invalid noteId format"}), 400

    result = counsellor_notes_collection.update_one(
        {"_id": obj_id, "applicationId": applicationId},
        {"$set": {"isDeleted": True, "updatedAt": _get_now()}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "Note not found"}), 404

    return jsonify({"message": "Note deleted successfully"}), 200

def get_notes_summary(applicationId):
    pipeline = [
        {"$match": {"applicationId": applicationId, "isDeleted": {"$ne": True}}},
        {"$group": {
            "_id": "$category",
            "count": {"$sum": 1},
            "lastNoteDate": {"$max": "$createdAt"}
        }}
    ]
    
    results = list(counsellor_notes_collection.aggregate(pipeline))
    
    total_notes = 0
    categories = {}
    last_note_date = None

    for res in results:
        count = res["count"]
        cat = res["_id"]
        date_str = res["lastNoteDate"]
        
        total_notes += count
        categories[cat] = count
        
        if last_note_date is None or date_str > last_note_date:
            last_note_date = date_str

    return jsonify({
        "totalNotes": total_notes,
        "categories": categories,
        "lastNoteDate": last_note_date
    }), 200
