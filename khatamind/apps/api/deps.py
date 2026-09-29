import os
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel
from adapters.storage.sql_repos import PostgresRepos, ActionRepo
from adapters.llm.fake import FakeLLM
from adapters.memory.fake import FakeMemory
from adapters.clock.system import SystemClock
from core.app.playbook.service import PlaybookService
from core.app.playbook.ledger import TacticLedger

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./khatamind.db")
engine = create_engine(DATABASE_URL)

def get_session():
    with Session(engine) as session:
        yield session

def init_db():
    SQLModel.metadata.create_all(engine)

# Setup dependency singletons for MVP
def get_session_factory():
    return Session(engine)

repos = PostgresRepos(lambda: Session(engine))
action_repo = ActionRepo(lambda: Session(engine))
memory_port = FakeMemory()
llm_port = FakeLLM()
clock_port = SystemClock()
playbook_svc = PlaybookService(memory=memory_port, llm=llm_port)
ledger_svc = TacticLedger(repos=repos)
