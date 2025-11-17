from src.auth.models import RefreshTokenORM
from src.repository import RepositoryORM


class RefreshTokenRepository(RepositoryORM[RefreshTokenORM]):
    model = RefreshTokenORM
    pass

