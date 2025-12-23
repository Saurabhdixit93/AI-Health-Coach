"""
Database initialization script with seed data.
"""
import sys
from sqlalchemy.orm import Session
from app.database import engine, Base, SessionLocal
from app.models import User, Protocol
import uuid


def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✓ Tables created successfully")


def seed_protocols(db: Session):
    """Seed initial protocol data."""
    print("\nSeeding protocol data...")
    
    protocols = [
        {
            "name": "Fever Management",
            "description": "Protocol for handling fever and temperature-related concerns",
            "keywords": ["fever", "temperature", "hot", "burning", "chills", "thermometer"],
            "instructions": {
                "steps": [
                    "Ask about fever duration and current temperature",
                    "Check for accompanying symptoms (cough, body ache, throat pain)",
                    "Recommend rest and adequate hydration",
                    "Suggest paracetamol for temperature above 100°F",
                    "Advise doctor consultation if fever persists beyond 3 days"
                ],
                "warnings": [
                    "Seek immediate medical attention if temperature exceeds 103°F",
                    "Watch for signs of dehydration or difficulty breathing"
                ]
            }
        },
        {
            "name": "Stomach Issues",
            "description": "Protocol for digestive and stomach-related problems",
            "keywords": ["stomach", "ache", "pain", "nausea", "vomit", "diarrhea", "constipation", "indigestion"],
            "instructions": {
                "steps": [
                    "Ask about nature of pain (sharp, dull, cramping)",
                    "Inquire about recent food intake and dietary changes",
                    "Recommend bland diet (BRAT - Banana, Rice, Applesauce, Toast)",
                    "Suggest staying hydrated with ORS or clear fluids",
                    "Advise avoiding spicy, oily, and heavy foods"
                ],
                "warnings": [
                    "Seek immediate care for severe abdominal pain",
                    "Blood in stool or vomit requires medical attention",
                    "Persistent vomiting leading to dehydration needs medical care"
                ]
            }
        },
        {
            "name": "Cold and Cough",
            "description": "Protocol for managing common cold and cough symptoms",
            "keywords": ["cold", "cough", "sneeze", "runny nose", "congestion", "sore throat"],
            "instructions": {
                "steps": [
                    "Ask about symptom duration and severity",
                    "Recommend adequate rest and sleep",
                    "Suggest warm fluids like tea with honey and ginger",
                    "Advise steam inhalation for congestion",
                    "Recommend saltwater gargling for sore throat"
                ],
                "warnings": [
                    "If cough persists beyond 2 weeks, consult a doctor",
                    "Difficulty breathing requires immediate medical attention",
                    "High fever with cold needs medical evaluation"
                ]
            }
        },
        {
            "name": "Headache Management",
            "description": "Protocol for managing different types of headaches",
            "keywords": ["headache", "migraine", "head pain", "head ache"],
            "instructions": {
                "steps": [
                    "Ask about headache location, intensity, and duration",
                    "Inquire about triggers (stress, screen time, sleep quality)",
                    "Recommend rest in a dark, quiet room",
                    "Suggest adequate hydration",
                    "Advise mild pain relief if needed"
                ],
                "warnings": [
                    "Sudden severe headache needs immediate medical attention",
                    "Headache with vision changes or numbness requires doctor consultation",
                    "Persistent or worsening headaches should be evaluated medically"
                ]
            }
        },
        {
            "name": "Emergency Situations",
            "description": "Protocol for identifying emergency medical situations",
            "keywords": ["emergency", "severe", "urgent", "critical", "chest pain", "difficulty breathing", "unconscious", "bleeding heavily"],
            "instructions": {
                "steps": [
                    "IMMEDIATELY advise calling emergency services or visiting ER",
                    "Do not provide health advice for emergency situations",
                    "Emphasize urgency of professional medical care"
                ],
                "warnings": [
                    "This is a medical emergency",
                    "Call emergency services or visit nearest hospital immediately",
                    "Do not delay seeking professional medical help"
                ]
            }
        },
        {
            "name": "Refund Policy",
            "description": "Protocol for handling refund and subscription queries",
            "keywords": ["refund", "payment", "subscription", "cancel", "billing", "charge"],
            "instructions": {
                "steps": [
                    "Acknowledge the refund/billing query",
                    "Explain that as a health coach, financial queries are handled by support team",
                    "Provide contact information for billing support",
                    "Assure that the matter will be resolved"
                ],
                "warnings": []
            }
        }
    ]
    
    created_count = 0
    for protocol_data in protocols:
        # Check if protocol already exists
        existing = db.query(Protocol).filter(Protocol.name == protocol_data["name"]).first()
        if not existing:
            protocol = Protocol(**protocol_data)
            db.add(protocol)
            created_count += 1
    
    db.commit()
    print(f"✓ Created {created_count} new protocols")


def seed_demo_user(db: Session):
    """Create a demo user for testing."""
    print("\nCreating demo user...")
    
    # Check if demo user exists
    demo_user = db.query(User).filter(User.name == "Demo User").first()
    
    if not demo_user:
        demo_user = User(
            name="Demo User",
            user_metadata={
                "age": 28,
                "location": "Mumbai, India",
                "demo": True
            }
        )
        db.add(demo_user)
        db.commit()
        db.refresh(demo_user)
        print(f"✓ Created demo user with ID: {demo_user.id}")
        print(f"  Save this ID for testing: {demo_user.id}")
    else:
        print(f"✓ Demo user already exists with ID: {demo_user.id}")
        print(f"  Use this ID for testing: {demo_user.id}")
    
    return demo_user


def init_db():
    """Initialize database with tables and seed data."""
    print("=" * 60)
    print("Initializing Disha AI Health Coach Database")
    print("=" * 60)
    
    try:
        # Create tables
        create_tables()
        
        # Create session
        db = SessionLocal()
        
        try:
            # Seed data
            seed_protocols(db)
            demo_user = seed_demo_user(db)
            
            print("\n" + "=" * 60)
            print("✓ Database initialization completed successfully!")
            print("=" * 60)
            print(f"\nDemo User ID for testing: {demo_user.id}")
            print("\nYou can now start the server with: uvicorn app.main:app --reload")
            
        finally:
            db.close()
            
    except Exception as e:
        print(f"\n✗ Error during initialization: {e}")
        sys.exit(1)


if __name__ == "__main__":
    init_db()
