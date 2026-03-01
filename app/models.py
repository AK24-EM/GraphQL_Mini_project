import datetime
from mongoengine import (
    Document,
    StringField,
    EmailField,
    FloatField,
    IntField,
    BooleanField,
    DateTimeField,
    ReferenceField,
    ListField,
    CASCADE,
)


# ── Member ──────────────────────────────────────────────────────────────────

class Member(Document):
    meta = {"collection": "members"}

    name = StringField(required=True, max_length=200)
    email = EmailField(required=True, unique=True)
    phone = StringField(max_length=20)
    join_date = DateTimeField(default=datetime.datetime.utcnow)
    membership_type = StringField(
        required=True,
        choices=["basic", "premium", "elite"],
        default="basic",
    )
    status = StringField(
        required=True,
        choices=["active", "expired", "suspended"],
        default="active",
    )


# ── Trainer ─────────────────────────────────────────────────────────────────

class Trainer(Document):
    meta = {"collection": "trainers"}

    name = StringField(required=True, max_length=200)
    email = EmailField(required=True, unique=True)
    specialization = StringField(required=True, max_length=200)
    certification = StringField(max_length=200)
    available = BooleanField(default=True)


# ── MembershipPlan ──────────────────────────────────────────────────────────

class MembershipPlan(Document):
    meta = {"collection": "membership_plans"}

    name = StringField(required=True, max_length=200)
    price = FloatField(required=True)
    duration_months = IntField(required=True)
    features = ListField(StringField())


# ── Class ────────────────────────────────────────────────────────────────────

class GymClass(Document):
    meta = {"collection": "classes"}

    name = StringField(required=True, max_length=200)
    description = StringField()
    trainer = ReferenceField(Trainer, required=True)
    schedule = StringField(required=True)        # e.g. "Mon/Wed 09:00 AM"
    max_participants = IntField(required=True, default=20)


# ── ClassEnrollment ──────────────────────────────────────────────────────────

class ClassEnrollment(Document):
    meta = {"collection": "class_enrollments"}

    gym_class = ReferenceField(GymClass, required=True)
    member = ReferenceField(Member, required=True)
    enrolled_at = DateTimeField(default=datetime.datetime.utcnow)


# ── WorkoutSession ───────────────────────────────────────────────────────────

class WorkoutSession(Document):
    meta = {"collection": "workout_sessions"}

    member = ReferenceField(Member, required=True)
    trainer = ReferenceField(Trainer, required=True)
    scheduled_time = DateTimeField(required=True)
    duration_minutes = IntField(required=True, default=60)
    status = StringField(
        required=True,
        choices=["scheduled", "completed", "cancelled"],
        default="scheduled",
    )
