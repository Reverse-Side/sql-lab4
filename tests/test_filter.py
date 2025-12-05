import pytest
import logging
from sqlalchemy import Column, Integer, String, Float, Boolean, select
from sqlalchemy.orm import declarative_base
from src.filter import Filter, FilterHeadler, Op, eq, neq, gt, lt, gte, lte, like, in_

Base = declarative_base()


class UserModel(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    salary = Column(Float)
    is_active = Column(Boolean)


class UserFilter(Filter):
    name: str
    age: int = gt()


# ==================== FIXTURES ====================


@pytest.fixture
def test_orm_model():
    """Фікстура для тестової моделі"""
    return UserModel


@pytest.fixture
def filter_handler(test_orm_model):
    """Фікстура для FilterHeadler"""
    return FilterHeadler(test_orm_model)


@pytest.fixture
def basic_filter():
    """Фікстура для базового фільтра"""
    return UserFilter(name="John", age=25)


@pytest.fixture
def sample_operators():
    """Фікстура з різними операторами"""
    return {
        "eq": eq(10),
        "neq": neq(20),
        "gt": gt(30),
        "lt": lt(40),
        "gte": gte(50),
        "lte": lte(60),
        "like": like("%test%"),
        "in_": in_([1, 2, 3]),
    }


@pytest.fixture
def filter_test_data():
    """Фікстура з тестовими даними для фільтрів"""
    return [
        {"name": "Alice", "age": 30},
        {"name": "Bob", "age": 25},
        {"name": "Charlie", "age": 35},
        {"name": "David", "age": 20},
        {"name": "Eve", "age": 28},
    ]


@pytest.fixture
def complex_filter_class():
    """Фікстура для складного фільтра"""

    class ComplexFilter(Filter):
        name: str = like()
        age: int = gte()
        id: int = in_()
        salary: float = gt()
        is_active: bool = eq()

    return ComplexFilter


# ==================== ТЕСТИ ДЛЯ Op ====================


class TestOp:
    """Тести для класу Op"""

    @pytest.mark.parametrize(
        "value,operator_func",
        [
            (10, lambda col, val: col == val),
            ("test", lambda col, val: col.like(val)),
            ([1, 2, 3], lambda col, val: col.in_(val)),
            (3.14, lambda col, val: col > val),
            (True, lambda col, val: col == val),
        ],
    )
    def test_op_init_various_types(self, value, operator_func):
        """Тест ініціалізації Op з різними типами даних"""
        op = Op(value=value, operator=operator_func)
        assert op.value == value
        assert callable(op.operator)

    @pytest.mark.parametrize(
        "operator,value,column_name",
        [
            (eq(10), 10, "age"),
            (neq(20), 20, "age"),
            (gt(30), 30, "age"),
            (lt(40), 40, "age"),
            (gte(50), 50, "age"),
            (lte(60), 60, "age"),
            (like("%test%"), "%test%", "name"),
            (in_([1, 2, 3]), [1, 2, 3], "id"),
        ],
    )
    def test_op_apply_success(self, operator, value, column_name, test_orm_model):
        """Тест успішного застосування різних операторів"""
        column = getattr(test_orm_model, column_name)
        result = operator.apply(column)
        assert result.left.name == column_name
        assert result.right.value == value

    def test_op_apply_attribute_error(self, test_orm_model):
        """Тест AttributeError при застосуванні неіснуючого методу"""
        op = Op(value=10, operator=lambda col, val: col.nonexistent_method(val))
        with pytest.raises(TypeError, match="does not support this operator"):
            op.apply(test_orm_model.age)

    def test_op_apply_type_error(self, test_orm_model):
        """Тест TypeError при несумісних типах колонки та значення"""
        # String value для Integer колонки
        op = gte("лор")
        with pytest.raises(TypeError):
            op.apply(test_orm_model.age)

    def test_op_apply_runtime_error(self, test_orm_model):
        """Тест RuntimeError при неочікуваній помилці"""

        def error_operator(col, val):
            raise ValueError("Unexpected error")

        op = Op(value=10, operator=error_operator)
        with pytest.raises(RuntimeError):
            op.apply(test_orm_model.age)

    def test_op_apply_correct_type_matching(self, test_orm_model):
        """Тест правильного співставлення типів"""
        # Integer для Integer колонки
        op_int = eq(25)
        result = op_int.apply(test_orm_model.age)
        assert result.right.value == 25

        # String для String колонки
        op_str = eq("John")
        result = op_str.apply(test_orm_model.name)
        assert result.right.value == "John"

        # Float для Float колонки
        op_float = gt(50000.0)
        result = op_float.apply(test_orm_model.salary)
        assert result.right.value == 50000.0

    @pytest.mark.parametrize(
        "operator,expected_name",
        [
            (eq(5), "eq"),
            (gt(10), "gt"),
            (like("%test%"), "like"),
        ],
    )
    def test_op_repr(self, operator, expected_name):
        """Тест repr для різних операторів"""
        repr_str = repr(operator)
        assert "Op" in repr_str
        assert str(operator.value) in repr_str


# ==================== ТЕСТИ ДЛЯ ОПЕРАТОРІВ ====================


class TestOpFactories:
    """Тести для фабрик операторів"""

    @pytest.mark.parametrize(
        "factory,value,expected_value",
        [
            (eq, 5, 5),
            (neq, 10, 10),
            (gt, 18, 18),
            (lt, 30, 30),
            (gte, 21, 21),
            (lte, 65, 65),
            (like, "%pattern%", "%pattern%"),
            (in_, [1, 2, 3], [1, 2, 3]),
        ],
    )
    def test_operator_factories(self, factory, value, expected_value, test_orm_model):
        """Тест всіх фабрик операторів"""
        op = factory(value)
        assert isinstance(op, Op)
        assert op.value == expected_value

    @pytest.mark.parametrize(
        "column_name,operator,value",
        [
            ("age", eq, 25),
            ("age", neq, 30),
            ("age", gt, 18),
            ("age", lt, 65),
            ("age", gte, 21),
            ("age", lte, 60),
            ("name", like, "%John%"),
            ("id", in_, [1, 2, 3, 4, 5]),
            ("salary", gt, 50000.0),
        ],
    )
    def test_operators_on_different_columns(
        self, column_name, operator, value, test_orm_model
    ):
        """Тест застосування операторів до різних колонок"""
        op = operator(value)
        column = getattr(test_orm_model, column_name)
        result = op.apply(column)
        assert result.left.name == column_name
        assert result.right.value == value

    def test_boolean_column_operator(self, test_orm_model):
        """Окремий тест для Boolean колонки (SQLAlchemy повертає True_/False_ об'єкти)"""
        op = eq(True)
        result = op.apply(test_orm_model.is_active)
        # Boolean створює спеціальний об'єкт без атрибута right.value
        assert result is not None
        assert hasattr(result, "left")

        op_false = eq(False)
        result_false = op_false.apply(test_orm_model.is_active)
        assert result_false is not None


# ==================== ТЕСТИ ДЛЯ Filter ====================


class TestFilterClass:
    """Тести для класу Filter"""

    def test_filter_init_basic(self, basic_filter):
        """Тест базової ініціалізації фільтра"""
        assert basic_filter.name.value == "John"
        assert basic_filter.age.value == 25
        assert isinstance(basic_filter.name, Op)
        assert isinstance(basic_filter.age, Op)

    @pytest.mark.parametrize(
        "name,age",
        [
            ("Alice", 30),
            ("Bob", 25),
            ("Charlie", 35),
            ("", 0),
            ("VeryLongNameForTesting" * 10, 999),
        ],
    )
    def test_filter_init_various_data(self, name, age):
        """Тест ініціалізації фільтра з різними даними"""
        f = UserFilter(name=name, age=age)
        assert f.name.value == name
        assert f.age.value == age

    def test_filter_with_default_operator(self):
        """Тест фільтра з дефолтним оператором"""
        f = UserFilter(name="Test", age=18)
        # name має eq за замовчуванням
        assert f.name.value == "Test"
        # age має gt за замовчуванням (визначено в класі)
        assert f.age.value == 18

    @pytest.mark.parametrize(
        "name_op,name_val,age_op,age_val",
        [
            (like("%John%"), "%John%", gte(25), 25),
            (eq("Alice"), "Alice", lte(30), 30),
            (neq("Bob"), "Bob", gt(20), 20),
            (like("%test%"), "%test%", eq(18), 18),
        ],
    )
    def test_filter_overload(self, name_op, name_val, age_op, age_val):
        """Тест методу overload з різними операторами"""
        f = UserFilter(name="Initial", age=0)
        f.overload(name=name_op, age=age_op)

        assert f.name.value == name_val
        assert f.age.value == age_val

    @pytest.mark.parametrize(
        "field,invalid_value",
        [
            ("age", "not_an_integer"),
            ("age", [1, 2, 3]),
            ("age", {"key": "value"}),
            ("age", 3.14),
        ],
    )
    def test_filter_overload_type_validation_error(self, field, invalid_value):
        """Тест валідації типів при overload з невалідними даними"""
        f = UserFilter(name="Test", age=18)

        with pytest.raises(ValueError, match="must by"):
            f.overload(**{field: eq(invalid_value)})

    def test_filter_to_dict(self, basic_filter):
        """Тест методу to_dict"""
        filter_dict = basic_filter.to_dict()

        assert isinstance(filter_dict, dict)
        assert "name" in filter_dict
        assert "age" in filter_dict
        assert all(isinstance(v, Op) for v in filter_dict.values())

    def test_filter_to_dict_after_overload(self):
        """Тест to_dict після overload"""
        f = UserFilter(name="Test", age=18)
        f.overload(name=like("%Test%"), age=gte(20))

        filter_dict = f.to_dict()
        assert filter_dict["name"].value == "%Test%"
        assert filter_dict["age"].value == 20

    @pytest.mark.parametrize(
        "name,age",
        [
            ("John", 25),
            ("Alice", 30),
            ("", 0),
        ],
    )
    def test_filter_repr(self, name, age):
        """Тест repr фільтра з різними даними"""
        f = UserFilter(name=name, age=age)
        repr_str = repr(f)

        assert "UserFilter" in repr_str
        assert "name" in repr_str
        assert "age" in repr_str

    def test_filter_invalid_operator_error(self):
        """Тест помилки при невалідному операторі"""

        class BadFilter(Filter):
            name: str = "not_an_operator"

        with pytest.raises(ValueError, match="Invalid operater"):
            BadFilter(name="Test")

    def test_filter_empty(self):
        """Тест порожнього фільтра"""

        class EmptyFilter(Filter):
            pass

        f = EmptyFilter()
        assert f.to_dict() == {}

    def test_filter_single_field(self):
        """Тест фільтра з одним полем"""

        class SingleFieldFilter(Filter):
            name: str

        f = SingleFieldFilter(name="Test")
        filter_dict = f.to_dict()

        assert len(filter_dict) == 1
        assert "name" in filter_dict


# ==================== ТЕСТИ ДЛЯ FilterHeadler ====================


class TestFilterHeadler:
    """Тести для класу FilterHeadler"""

    def test_handler_init(self, filter_handler, test_orm_model):
        """Тест ініціалізації обробника"""
        assert filter_handler.model == test_orm_model

    def test_handler_call(self, filter_handler, basic_filter):
        """Тест виклику обробника як функції"""
        conditions = filter_handler(basic_filter)

        assert isinstance(conditions, list)
        assert len(conditions) == 2

    @pytest.mark.parametrize(
        "name,age,expected_count",
        [
            ("John", 25, 2),
            ("Alice", 30, 2),
            ("Bob", 18, 2),
        ],
    )
    def test_handler_to_conditions_various_data(
        self, filter_handler, name, age, expected_count
    ):
        """Тест створення умов з різними даними"""
        f = UserFilter(name=name, age=age)
        conditions = filter_handler.to_conditions(f)

        assert len(conditions) == expected_count
        assert conditions[0].right.value == name
        assert conditions[1].right.value == age

    def test_handler_to_conditions_structure(self, filter_handler, basic_filter):
        """Тест структури створених умов"""
        conditions = filter_handler.to_conditions(basic_filter)

        cond_name = conditions[0]
        cond_age = conditions[1]

        assert cond_name.left.name == "name"
        assert cond_name.right.value == "John"
        assert cond_age.left.name == "age"
        assert cond_age.right.value == 25

    @pytest.mark.parametrize(
        "name_op,age_op",
        [
            (like("%John%"), gte(20)),
            (eq("Alice"), lte(30)),
            (neq("Bob"), gt(25)),
        ],
    )
    def test_handler_with_overload(self, filter_handler, name_op, age_op):
        """Тест обробника з перевизначеними операторами"""
        f = UserFilter(name="Initial", age=0)
        f.overload(name=name_op, age=age_op)

        conditions = filter_handler.to_conditions(f)

        assert len(conditions) == 2
        assert conditions[0].right.value == name_op.value
        assert conditions[1].right.value == age_op.value

    def test_handler_nonexistent_field_error(self, filter_handler, caplog):
        """Тест обробки неіснуючого поля з перевіркою логів"""

        class FilterWithBadField(Filter):
            name: str
            nonexistent_field: str
            another_bad_field: int

        f = FilterWithBadField(
            name="Test", nonexistent_field="Bad", another_bad_field=123
        )

        with caplog.at_level(logging.ERROR):
            conditions = filter_handler.to_conditions(f)

        # Має бути створена тільки одна умова (для існуючого поля)
        assert len(conditions) == 1
        assert conditions[0].left.name == "name"

        # Перевіряємо що помилки записані в лог
        assert "does not contain" in caplog.text
        assert "FilterWithBadField" in caplog.text

    def test_handler_complex_filter(self, filter_handler, complex_filter_class):
        """Тест складного фільтра з багатьма полями"""
        f = complex_filter_class(
            name="%Test%", age=25, id=[1, 2, 3], salary=50000.0, is_active=True
        )

        conditions = filter_handler.to_conditions(f)

        assert len(conditions) == 5

        # Перевіряємо що всі умови створені правильно
        field_names = [cond.left.name for cond in conditions]
        assert "name" in field_names
        assert "age" in field_names
        assert "id" in field_names
        assert "salary" in field_names
        assert "is_active" in field_names

    def test_handler_empty_filter(self, filter_handler):
        """Тест порожнього фільтра"""

        class EmptyFilter(Filter):
            pass

        f = EmptyFilter()
        conditions = filter_handler.to_conditions(f)

        assert conditions == []

    @pytest.mark.parametrize(
        "filter_data",
        [
            {"name": "Alice", "age": 30},
            {"name": "Bob", "age": 25},
            {"name": "Charlie", "age": 35},
        ],
    )
    def test_handler_multiple_filters(self, filter_handler, filter_data):
        """Тест обробки декількох фільтрів послідовно"""
        f = UserFilter(**filter_data)
        conditions = filter_handler(f)

        assert len(conditions) == 2
        assert conditions[0].right.value == filter_data["name"]
        assert conditions[1].right.value == filter_data["age"]


# ==================== ІНТЕГРАЦІЙНІ ТЕСТИ ====================


class TestIntegration:
    """Інтеграційні тести"""

    def test_full_workflow(self, filter_handler):
        """Тест повного робочого процесу"""
        # Створюємо фільтр
        f = UserFilter(name="John", age=25)

        # Перевизначаємо оператори
        f.overload(name=like("%John%"), age=gte(25))

        # Отримуємо умови
        conditions = filter_handler(f)

        # Перевіряємо результат
        assert len(conditions) == 2
        assert conditions[0].right.value == "%John%"
        assert conditions[1].right.value == 25

    @pytest.mark.parametrize(
        "test_data",
        [
            {"name": "Alice", "age": 30, "name_op": like("%Alice%"), "age_op": gte(30)},
            {"name": "Bob", "age": 25, "name_op": eq("Bob"), "age_op": lte(25)},
            {"name": "Charlie", "age": 35, "name_op": neq("David"), "age_op": gt(30)},
        ],
    )
    def test_workflow_with_various_data(self, filter_handler, test_data):
        """Тест робочого процесу з різними даними"""
        f = UserFilter(name=test_data["name"], age=test_data["age"])
        f.overload(name=test_data["name_op"], age=test_data["age_op"])

        conditions = filter_handler(f)

        assert len(conditions) == 2
        assert conditions[0].right.value == test_data["name_op"].value
        assert conditions[1].right.value == test_data["age_op"].value

    def test_workflow_with_multiple_models(self):
        """Тест з декількома моделями"""

        class AnotherModel(Base):
            __tablename__ = "another"
            id = Column(Integer, primary_key=True)
            title = Column(String)

        class AnotherFilter(Filter):
            title: str

        handler = FilterHeadler(AnotherModel)
        f = AnotherFilter(title="Test")
        conditions = handler(f)

        assert len(conditions) == 1
        assert conditions[0].left.name == "title"

    def test_workflow_error_recovery(self, filter_handler, caplog):
        """Тест відновлення після помилок"""

        class MixedFilter(Filter):
            name: str
            nonexistent: str
            age: int

        f = MixedFilter(name="Test", nonexistent="Bad", age=25)

        with caplog.at_level(logging.ERROR):
            conditions = filter_handler(f)

        # Має обробити тільки валідні поля
        assert len(conditions) == 2
        assert "does not contain" in caplog.text


# ==================== ТЕСТИ ГРАНИЧНИХ ВИПАДКІВ ====================


class TestEdgeCases:
    """Тести граничних випадків"""

    def test_filter_with_none_values(self):
        """Тест фільтра з None значеннями"""

        class NullableFilter(Filter):
            name: str
            age: int

        # SQLAlchemy підтримує порівняння з None
        f = NullableFilter(name=None, age=None)
        assert f.name.value is None
        assert f.age.value is None

    def test_filter_with_empty_strings(self):
        """Тест фільтра з порожніми рядками"""
        f = UserFilter(name="", age=0)
