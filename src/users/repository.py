from src.repository import RepositoryORM
from src.users.models import UserORM
from src.auth.models import RefreshTokenORM  
from src.events.models import EventORM
from src.tickets.models import TicketsORM

class UserRepository(RepositoryORM[UserORM]):
    model = UserORM 

class RefreshTokenRepository(RepositoryORM[RefreshTokenORM]):
    model = RefreshTokenORM 
    
class EventRepository(RepositoryORM[EventORM]):
    model = EventORM
    
class TicketRepository(RepositoryORM[TicketsORM]):
    model = TicketsORM