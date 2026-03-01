"""
seed.py — Populates MongoDB (gym_db) with sample data.

Run once before starting the server:
    python seed.py
"""
import datetime
import sys
import os

# Ensure app/ is importable
sys.path.insert(0, os.path.dirname(__file__))

from app.database import init_db
from app.models import Member, Trainer, MembershipPlan, GymClass, ClassEnrollment, WorkoutSession

init_db()

def seed():
    # ── Wipe existing data ──────────────────────────────────────────────────
    Member.drop_collection()
    Trainer.drop_collection()
    MembershipPlan.drop_collection()
    GymClass.drop_collection()
    ClassEnrollment.drop_collection()
    WorkoutSession.drop_collection()
    print("✓ Cleared existing collections")

    # ── Trainers ─────────────────────────────────────────────────────────────
    t1 = Trainer(
        name="Carlos Mendez",
        email="carlos@gym.com",
        specialization="Strength & Conditioning",
        certification="NSCA-CSCS",
        available=True,
    ).save()

    t2 = Trainer(
        name="Priya Sharma",
        email="priya@gym.com",
        specialization="Yoga & Flexibility",
        certification="RYT-500",
        available=True,
    ).save()

    t3 = Trainer(
        name="Mike Johnson",
        email="mike@gym.com",
        specialization="HIIT & Cardio",
        certification="ACE-CPT",
        available=False,
    ).save()

    print("✓ Seeded 3 trainers")

    # ── Members ───────────────────────────────────────────────────────────────
    m1 = Member(
        name="Alice Wong",
        email="alice@example.com",
        phone="555-1001",
        join_date=datetime.datetime(2023, 6, 15),
        membership_type="premium",
        status="active",
    ).save()

    m2 = Member(
        name="Bob Martinez",
        email="bob@example.com",
        phone="555-1002",
        join_date=datetime.datetime(2022, 11, 1),
        membership_type="basic",
        status="active",
    ).save()

    m3 = Member(
        name="Clara Singh",
        email="clara@example.com",
        phone="555-1003",
        join_date=datetime.datetime(2021, 3, 20),
        membership_type="elite",
        status="expired",
    ).save()

    m4 = Member(
        name="David Lee",
        email="david@example.com",
        phone="555-1004",
        join_date=datetime.datetime(2024, 1, 10),
        membership_type="basic",
        status="suspended",
    ).save()

    print("✓ Seeded 4 members")

    # ── Membership Plans ──────────────────────────────────────────────────────
    MembershipPlan(
        name="Basic",
        price=29.99,
        duration_months=1,
        features=["Gym access", "Locker room"],
    ).save()

    MembershipPlan(
        name="Premium",
        price=59.99,
        duration_months=3,
        features=["Gym access", "Locker room", "Group classes", "Sauna"],
    ).save()

    MembershipPlan(
        name="Elite",
        price=99.99,
        duration_months=12,
        features=["All Premium", "Personal trainer sessions", "Nutrition plan"],
    ).save()

    print("✓ Seeded 3 membership plans")

    # ── Classes ───────────────────────────────────────────────────────────────
    c1 = GymClass(
        name="Power Lifting",
        description="Heavy compound lifts with progressive overload.",
        trainer=t1,
        schedule="Mon/Wed/Fri 07:00 AM",
        max_participants=10,
    ).save()

    c2 = GymClass(
        name="Morning Yoga",
        description="Energising flow yoga to start the day.",
        trainer=t2,
        schedule="Tue/Thu 06:30 AM",
        max_participants=15,
    ).save()

    c3 = GymClass(
        name="HIIT Blast",
        description="High-intensity interval training for fat burn.",
        trainer=t3,
        schedule="Sat 09:00 AM",
        max_participants=3,           # small cap for capacity-testing
    ).save()

    c4 = GymClass(
        name="Core & Stretch",
        description="Core strengthening and flexibility session.",
        trainer=t2,
        schedule="Mon/Thu 12:00 PM",
        max_participants=20,
    ).save()

    print("✓ Seeded 4 classes")

    # ── Enrollments ───────────────────────────────────────────────────────────
    e1 = ClassEnrollment(gym_class=c1, member=m1).save()
    e2 = ClassEnrollment(gym_class=c2, member=m1).save()
    e3 = ClassEnrollment(gym_class=c1, member=m2).save()

    # Fill HIIT Blast to capacity (max=3)
    ClassEnrollment(gym_class=c3, member=m1).save()
    ClassEnrollment(gym_class=c3, member=m2).save()
    ClassEnrollment(gym_class=c3, member=m3).save()

    print("✓ Seeded enrollments (HIIT Blast is now FULL for capacity testing)")

    # ── Workout Sessions ───────────────────────────────────────────────────────
    WorkoutSession(
        member=m1,
        trainer=t1,
        scheduled_time=datetime.datetime(2024, 2, 1, 10, 0),
        duration_minutes=60,
        status="completed",
    ).save()

    WorkoutSession(
        member=m2,
        trainer=t2,
        scheduled_time=datetime.datetime(2024, 2, 5, 8, 0),
        duration_minutes=45,
        status="scheduled",
    ).save()

    WorkoutSession(
        member=m1,
        trainer=t2,
        scheduled_time=datetime.datetime(2024, 2, 10, 9, 0),
        duration_minutes=30,
        status="scheduled",
    ).save()

    print("✓ Seeded 3 workout sessions")
    print("\n🌱 Seed complete! Run `python run.py` to start the server.")


if __name__ == "__main__":
    seed()
