from utils.db import applications_collection

def seed_db():
    app_doc = {"applicationId": "APP-123456", "name": "Test Application for Assessment"}
    
    # Avoid duplicate seeding
    if not applications_collection.find_one({"applicationId": app_doc["applicationId"]}):
        applications_collection.insert_one(app_doc)
        print(f"Inserted dummy application: {app_doc}")
    else:
        print("Dummy application already exists.")

if __name__ == "__main__":
    seed_db()
