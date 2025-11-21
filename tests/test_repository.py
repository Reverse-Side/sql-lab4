import pytest

from src.filter import eq
from src.seed_database import main as drop_table
from src.unit_of_work import get_unit_of_work


@pytest.mark.asyncio
async def test_repository():
    uow = get_unit_of_work()
    async with uow as work:  # отримуємо AsyncSession з unit_of_work
        await drop_table()

        # Додаємо запис
        data = {"nickname": "test", "password": "12345678", "email": "test@test.com"}
        instance = await work.users.add(data)
        assert instance.nickname == "test"

        # Знаходимо запис
        found = await work.users.find(nickname=eq("test"))
        assert found.id == instance.id

        # Оновлюємо запис
        updated = await work.users.update(_id=instance.id, data={"nickname": "updated"})
        assert updated.nickname == "updated"

        # Видаляємо запис
        deleted = await work.users.delete(_id=instance.id)
        assert deleted.id == instance.id

        # Перевіряємо find_all
        all_items = await work.users.find_all(limit=10)
        assert len(all_items) == 0  # після видалення
