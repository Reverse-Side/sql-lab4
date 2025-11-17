from src.repository import RepositoryORM
from src.tickets.models import TicketsORM


class TicketsRepository(RepositoryORM[TicketsORM]):
    model = TicketsORM
    pass
