from graphene_mongo import MongoengineObjectType
import graphene
from ..models import (
    Member,
    Trainer,
    MembershipPlan,
    GymClass,
    ClassEnrollment,
    WorkoutSession,
)


class MemberType(MongoengineObjectType):
    class Meta:
        model = Member

    enrollments = graphene.List(lambda: ClassEnrollmentType)
    workout_sessions = graphene.List(lambda: WorkoutSessionType)

    def resolve_enrollments(root, info):
        return ClassEnrollment.objects(member=root.id)

    def resolve_workout_sessions(root, info):
        return WorkoutSession.objects(member=root.id)


class TrainerType(MongoengineObjectType):
    class Meta:
        model = Trainer

    classes = graphene.List(lambda: ClassType)

    def resolve_classes(root, info):
        return GymClass.objects(trainer=root.id)


class MembershipPlanType(MongoengineObjectType):
    class Meta:
        model = MembershipPlan


class ClassType(MongoengineObjectType):
    class Meta:
        model = GymClass

    available_spots = graphene.Int()

    def resolve_available_spots(root, info):
        enrolled = ClassEnrollment.objects(gym_class=root.id).count()
        return max(0, root.max_participants - enrolled)


class ClassEnrollmentType(MongoengineObjectType):
    class Meta:
        model = ClassEnrollment

    # Expose nested class and member as typed objects
    gym_class = graphene.Field(lambda: ClassType)
    member = graphene.Field(lambda: MemberType)

    def resolve_gym_class(root, info):
        return root.gym_class

    def resolve_member(root, info):
        return root.member


class WorkoutSessionType(MongoengineObjectType):
    class Meta:
        model = WorkoutSession

    member = graphene.Field(lambda: MemberType)
    trainer = graphene.Field(lambda: TrainerType)

    def resolve_member(root, info):
        return root.member

    def resolve_trainer(root, info):
        return root.trainer
