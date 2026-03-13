# Counsellor Notes API

This is a Flask-based JSON CRUD API that uses MongoDB for managing counsellor private notes against student applications.

## Prerequisites
- Python 3.9+
- MongoDB

## Setup and Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Define `.env` (already provided, sets default configuration). Make sure MongoDB is running locally on `localhost:27017` or update the `MONGO_URI`.
3. Create test application in DB to use `APP-123456`:
   ```bash
   python seed.py
   ```
4. Start the server:
   ```bash
   python app.py
   ```
   The API will run on `http://localhost:5000`

## Endpoints

All endpoints require the `@internal_required` mock decorator (currently a passthrough in `utils/auth.py`) and are registered under the Blueprint (`/api/applications/<applicationId>/notes`).

### 1. Create a Note
- **Method**: POST
- **Path**: `/api/applications/<applicationId>/notes`
- **Auth**: `@internal_required`
- **Request Body**:
  ```json
  {
    "authorName": "John Doe",
    "authorEmail": "john@example.com",
    "category": "General",
    "content": "Discussed document requirements",
    "isPinned": false
  }
  ```
- **Response Format**: `201 Created` with the inserted note object.

### 2. List Notes (Pagination and Sorting)
- **Method**: GET
- **Path**: `/api/applications/<applicationId>/notes`
- **Query Params**: `?page=1&limit=10`
- **Auth**: `@internal_required`
- **Response Format**: `200 OK`
  ```json
  {
    "notes": [...],
    "totalNotes": 10,
    "totalPages": 2,
    "currentPage": 1
  }
  ```
- **Note**: Soft-deleted notes are hidden. Pinned notes appear first, then sorted by `createdAt` descending.

### 3. Edit Note
- **Method**: PATCH
- **Path**: `/api/applications/<applicationId>/notes/<noteId>`
- **Auth**: `@internal_required`
- **Request Body**: any combination of fields (e.g., `"content"`, `"isPinned"`, `"category"`).
- **Response Format**: `200 OK` with the updated note. Updates `updatedAt` without altering `createdAt`.

### 4. Delete Note (Soft Delete)
- **Method**: DELETE
- **Path**: `/api/applications/<applicationId>/notes/<noteId>`
- **Auth**: `@internal_required`
- **Response Format**: `200 OK`
- **Note**: Sets `isDeleted: true` to preserve the record.

### 5. Notes Summary
- **Method**: GET
- **Path**: `/api/applications/<applicationId>/notes/summary`
- **Auth**: `@internal_required`
- **Response Format**: `200 OK`
  ```json
  {
    "totalNotes": 1,
    "categories": {
      "General": 1
    },
    "lastNoteDate": "2026-03-12T10:00:00Z"
  }
  ```
