from src.repository import RepositoryORM
from src.seats.models import SeatsORM

class SeatsRepository(RepositoryORM[SeatsORM]): 
    model = SeatsORM
    pass