import graphene
from ..models import Member, Trainer, GymClass
from .types import (
    MemberType,
    TrainerType,
    MembershipPlanType,
    ClassType,
    ClassEnrollmentType,
    WorkoutSessionType,
    ClassEnrollment,
)


class Query(graphene.ObjectType):

    # ── Trainers ─────────────────────────────────────────────────────────────
    trainers = graphene.List(TrainerType)
    trainer = graphene.Field(TrainerType, id=graphene.String(required=True))

    def resolve_trainers(root, info):
        return Trainer.objects.all()

    def resolve_trainer(root, info, id):
        return Trainer.objects(pk=id).first()

    # ── Members ──────────────────────────────────────────────────────────────
    members = graphene.List(MemberType)
    member = graphene.Field(MemberType, id=graphene.String(required=True))

    def resolve_members(root, info):
        return Member.objects.all()

    def resolve_member(root, info, id):
        return Member.objects(pk=id).first()

    # ── Classes ──────────────────────────────────────────────────────────────
    classes = graphene.List(ClassType)
    gym_class = graphene.Field(ClassType, id=graphene.String(required=True))

    def resolve_classes(root, info):
        return GymClass.objects.all()

    def resolve_gym_class(root, info, id):
        return GymClass.objects(pk=id).first()

    # ── Available Classes ─────────────────────────────────────────────────────
    available_classes = graphene.List(ClassType)

    def resolve_available_classes(root, info):
        """Return classes that still have open spots."""
        result = []
        for cls in GymClass.objects.all():
            enrolled = ClassEnrollment.objects(gym_class=cls).count()
            if enrolled < cls.max_participants:
                result.append(cls)
        return result
