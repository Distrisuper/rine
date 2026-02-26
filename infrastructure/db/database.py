from sqlmodel import SQLModel, create_engine

engine = create_engine("sqlite:////app/.data/rine.db", echo=False)


def get_engine():
    return engine
