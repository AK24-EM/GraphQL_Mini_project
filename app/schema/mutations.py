import graphene
import datetime
from ..models import Member, Trainer, GymClass, ClassEnrollment, WorkoutSession
from .types import (
    ClassEnrollmentType,
    WorkoutSessionType,
)


# ══════════════════════════════
#  enrollInClass
# ══════════════════════════════

class EnrollInClassInput(graphene.InputObjectType):
    member_id = graphene.String(required=True)
    class_id = graphene.String(required=True)


class EnrollInClass(graphene.Mutation):
    class Arguments:
        input = EnrollInClassInput(required=True)

    enrollment = graphene.Field(ClassEnrollmentType)
    error = graphene.String()

    def mutate(root, info, input):
        member = Member.objects(pk=input.member_id).first()
        if not member:
            return EnrollInClass(error="Member not found.")

        gym_class = GymClass.objects(pk=input.class_id).first()
        if not gym_class:
            return EnrollInClass(error="Class not found.")

        # Capacity check
        enrolled_count = ClassEnrollment.objects(gym_class=gym_class).count()
        if enrolled_count >= gym_class.max_participants:
            return EnrollInClass(error="Class is full. No available spots.")

        # Duplicate check
        existing = ClassEnrollment.objects(
            gym_class=gym_class, member=member
        ).first()
        if existing:
            return EnrollInClass(error="Member is already enrolled in this class.")

        enrollment = ClassEnrollment(
            gym_class=gym_class,
            member=member,
            enrolled_at=datetime.datetime.utcnow(),
        )
        enrollment.save()
        return EnrollInClass(enrollment=enrollment)


# ══════════════════════════════
#  scheduleWorkout
# ══════════════════════════════

class ScheduleWorkoutInput(graphene.InputObjectType):
    member_id = graphene.String(required=True)
    trainer_id = graphene.String(required=True)
    scheduled_time = graphene.String(required=True)   # ISO-8601 string
    duration_minutes = graphene.Int(required=True)


class ScheduleWorkout(graphene.Mutation):
    class Arguments:
        input = ScheduleWorkoutInput(required=True)

    session = graphene.Field(WorkoutSessionType)
    error = graphene.String()

    def mutate(root, info, input):
        member = Member.objects(pk=input.member_id).first()
        if not member:
            return ScheduleWorkout(error="Member not found.")

        trainer = Trainer.objects(pk=input.trainer_id).first()
        if not trainer:
            return ScheduleWorkout(error="Trainer not found.")

        if not trainer.available:
            return ScheduleWorkout(error="Trainer is not currently available.")

        try:
            scheduled_time = datetime.datetime.fromisoformat(input.scheduled_time)
        except ValueError:
            return ScheduleWorkout(
                error="Invalid scheduledTime format. Use ISO-8601 (e.g. 2024-02-01T10:00:00)."
            )

        session = WorkoutSession(
            member=member,
            trainer=trainer,
            scheduled_time=scheduled_time,
            duration_minutes=input.duration_minutes,
            status="scheduled",
        )
        session.save()
        return ScheduleWorkout(session=session)


# ══════════════════════════════
#  cancelEnrollment
# ══════════════════════════════

class CancelEnrollment(graphene.Mutation):
    class Arguments:
        enrollment_id = graphene.String(required=True)

    success = graphene.Boolean()
    message = graphene.String()

    def mutate(root, info, enrollment_id):
        enrollment = ClassEnrollment.objects(pk=enrollment_id).first()
        if not enrollment:
            return CancelEnrollment(success=False, message="Enrollment not found.")
        enrollment.delete()
        return CancelEnrollment(success=True, message="Enrollment cancelled successfully.")


# ══════════════════════════════
#  Root Mutation
# ══════════════════════════════

class Mutation(graphene.ObjectType):
    enroll_in_class = EnrollInClass.Field()
    schedule_workout = ScheduleWorkout.Field()
    cancel_enrollment = CancelEnrollment.Field()
