from flask import request, jsonify
from utils.db import users_collection
from bson import ObjectId
from bson.errors import InvalidId
from datetime import datetime, timezone
from typing import Any

def _get_now():
    return datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')

def create_user(): 
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON request body"}), 400

    required_fields = ["name", "email"]
    for field in required_fields:
        if field not in data or not str(data[field]).strip():
            return jsonify({"error": f"Missing or empty required field: {field}"}), 400

    # Check if user already exists
    if users_collection.find_one({"email": data["email"].strip(), "isDeleted": {"$ne": True}}):
        return jsonify({"error": "User with this email already exists"}), 409

    user = {
        "name": data["name"].strip(),
        "email": data["email"].strip(),
        "role": data.get("role", "user").strip(),
        "isDeleted": False,
        "createdAt": _get_now(),
        "updatedAt": _get_now()
    }

    result = users_collection.insert_one(user)
    user["_id"] = str(result.inserted_id)

    return jsonify(user), 201

def get_users():
    try:
        page = max(1, int(request.args.get("page", 1)))
        limit = min(50, max(1, int(request.args.get("limit", 10))))
    except ValueError:
        return jsonify({"error": "Invalid pagination parameters"}), 400

    query = {"isDeleted": {"$ne": True}}

    total_users = users_collection.count_documents(query)
    total_pages = (total_users + limit - 1) // limit

    cursor = users_collection.find(query)
    cursor.sort("createdAt", -1)
    cursor.skip((page - 1) * limit).limit(limit)

    users = []
    for doc in cursor:
        doc["_id"] = str(doc["_id"])
        users.append(doc)

    return jsonify({
        "users": users,
        "totalUsers": total_users,
        "totalPages": total_pages,
        "currentPage": page
    }), 200

def get_user(userId):
    try:
        obj_id = ObjectId(userId)
    except InvalidId:
        return jsonify({"error": "Invalid userId format"}), 400

    user = users_collection.find_one({"_id": obj_id, "isDeleted": {"$ne": True}})
    if not user:
        return jsonify({"error": "User not found"}), 404

    user["_id"] = str(user["_id"])
    return jsonify(user), 200

def edit_user(userId):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Missing JSON request body"}), 400

    try:
        obj_id = ObjectId(userId)
    except InvalidId:
        return jsonify({"error": "Invalid userId format"}), 400 

    update_fields: dict[str, Any] = {}
    valid_fields = ["name", "email", "role"]

    for field in valid_fields:
        if field in data:
            update_fields[field] = data[field].strip() if isinstance(data[field], str) else data[field]

    if not update_fields:
        return jsonify({"error": "No valid fields provided for update"}), 400

    # Ensure email uniqueness if updating email
    if "email" in update_fields:
        existing_user = users_collection.find_one({
            "email": update_fields["email"], 
            "_id": {"$ne": obj_id}, 
            "isDeleted": {"$ne": True}
        })
        if existing_user:
            return jsonify({"error": "Email is already taken"}), 409

    update_fields["updatedAt"] = _get_now()

    result = users_collection.update_one(
        {"_id": obj_id, "isDeleted": {"$ne": True}},
        {"$set": update_fields}
    )

    if result.matched_count == 0:
        return jsonify({"error": "User not found or deleted"}), 404

    user = users_collection.find_one({"_id": obj_id})
    if user:
        user["_id"] = str(user["_id"])
    return jsonify(user), 200

def delete_user(userId):
    try:
        obj_id = ObjectId(userId)
    except InvalidId:
        return jsonify({"error": "Invalid userId format"}), 400

    result = users_collection.update_one(
        {"_id": obj_id},
        {"$set": {"isDeleted": True, "updatedAt": _get_now()}}
    )

    if result.matched_count == 0:
        return jsonify({"error": "User not found"}), 404

    return jsonify({"message": "User deleted successfully"}), 200
