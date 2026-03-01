from mongoengine import connect


def init_db():
    connect(
        db="gym_db",
        host="localhost",
        port=27017,
    )
