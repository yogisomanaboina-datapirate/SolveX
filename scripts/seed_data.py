import sys
import os

# Ensure healthtrack_backend root is on python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.security import db, init_firebase

def seed_hospitals():
    init_firebase()
    if not db:
        print("⚠️ Firebase DB client not available. Please verify firebase_service_account.json path.")
        return

    hospitals = [
        {
            "hospitalId": "hosp_1",
            "name": "Apollo Hospitals, Jubilee Hills",
            "location": {"lat": 17.4239, "lng": 78.4116},
            "specialties": ["cardiology", "neurology", "trauma", "emergency"],
            "ICU": 25,
            "ventilator": 12,
            "general": 80
        },
        {
            "hospitalId": "hosp_2",
            "name": "Care Hospitals, Banjara Hills",
            "location": {"lat": 17.4156, "lng": 78.4487},
            "specialties": ["cardiology", "orthopedics", "nephrology"],
            "ICU": 18,
            "ventilator": 8,
            "general": 60
        },
        {
            "hospitalId": "hosp_3",
            "name": "KIMS Hospitals, Secunderabad",
            "location": {"lat": 17.4375, "lng": 78.4983},
            "specialties": ["trauma", "emergency", "pulmonology"],
            "ICU": 30,
            "ventilator": 15,
            "general": 100
        },
        {
            "hospitalId": "hosp_4",
            "name": "Yashoda Hospitals, Somajiguda",
            "location": {"lat": 17.4258, "lng": 78.4597},
            "specialties": ["oncology", "gastroenterology", "emergency"],
            "ICU": 20,
            "ventilator": 10,
            "general": 75
        },
        {
            "hospitalId": "hosp_5",
            "name": "Continental Hospitals, Gachibowli",
            "location": {"lat": 17.4204, "lng": 78.3488},
            "specialties": ["cardiology", "neurology", "trauma", "pediatrics"],
            "ICU": 22,
            "ventilator": 11,
            "general": 90
        }
    ]

    print("🌱 Seeding Firestore database with sample hospital records...")
    for hosp in hospitals:
        db.collection("hospitals").document(hosp["hospitalId"]).set(hosp)
        print(f"  ✅ Added {hosp['name']} (ID: {hosp['hospitalId']})")
    print("🎉 Seeding complete!")

if __name__ == "__main__":
    seed_hospitals()
