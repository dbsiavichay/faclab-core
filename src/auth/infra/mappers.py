from wireup import injectable

from src.auth.domain.entities import User
from src.auth.infra.models import UserModel
from src.shared.infra.mappers import Mapper


@injectable(lifetime="singleton")
class UserMapper(Mapper[User, UserModel]):
    __entity__ = User
    __exclude_fields__ = frozenset({"created_at"})
