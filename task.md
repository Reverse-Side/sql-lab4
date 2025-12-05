# 🎬 FastAPI Cinema Project — Developer Guide

## 📘 Опис

Цей документ — покроковий путівник для розробників, які працюють над REST API кінотеатру. Він описує архітектуру, таблиці бази даних, зв’язки, порядок розробки та залежності між модулями.

---

## 🧩 Основна структура проекту

```
src/
 ├── auth/              # Авторизація та користувачі
 ├── events/            # Події (фільми)
 ├── seats/             # Місця залу
 ├── tickets/           # Квитки
 ├── payments/          # Оплати
 ├── tasks/             # Фонові завдання
 ├── database.py        # Підключення до БД
 ├── config.py          # Конфігурації
 └── main.py            # Точка входу FastAPI
```

---

## 🧱 База даних — моделі та зв’язки

### 1. **Users**

| Поле            | Тип         | Примітка             |
| --------------- | ----------- | -------------------- |
| id              | int, PK     | Primary Key          |
| email           | str, unique | Унікальний email     |
| hashed_password | str         | Збережений пароль    |
| full_name       | str         | Ім’я користувача     |
| is_admin        | bool        | Права адміністратора |
| created_at      | datetime    | Автоматично          |

**Зв’язки:** 1→n `tickets`, 1→n `payments`

```python
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String)
    is_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    tickets = relationship('Ticket', back_populates='user')
```

---

### 2. **Events**

| Поле             | Тип      | Примітка       |
| ---------------- | -------- | -------------- |
| id               | int, PK  |                |
| title            | str      | Назва фільму   |
| description      | text     | Опис           |
| start_time       | datetime | Початок сеансу |
| duration_minutes | int      | Тривалість     |
| price            | float    | Ціна квитка    |
| created_at       | datetime | Дата створення |

**Зв’язки:** 1→n `seats`, 1→n `tickets`

```python
class Event(Base):
    __tablename__ = 'events'
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    start_time = Column(DateTime, nullable=False)
    duration_minutes = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    seats = relationship('Seat', back_populates='event')
```

---

### 3. **Seats**

| Поле        | Тип     | Примітка           |
| ----------- | ------- | ------------------ |
| id          | int, PK |                    |
| event_id    | FK      | Прив’язка до події |
| seat_number | str     | Номер місця        |
| is_reserved | bool    | Статус броні       |

**Зв’язки:** n→1 `events`, 1→1 `tickets`

```python
class Seat(Base):
    __tablename__ = 'seats'
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('events.id'))
    seat_number = Column(String, nullable=False)
    is_reserved = Column(Boolean, default=False)

    event = relationship('Event', back_populates='seats')
```

---

### 4. **Tickets**

| Поле       | Тип      | Примітка                    |
| ---------- | -------- | --------------------------- |
| id         | int, PK  |                             |
| user_id    | FK       | Користувач                  |
| event_id   | FK       | Подія                       |
| seat_id    | FK       | Місце                       |
| status     | enum     | reserved / paid / cancelled |
| created_at | datetime |                             |

**Зв’язки:** n→1 `users`, `events`, `seats`, 1→1 `payments`

```python
class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    event_id = Column(Integer, ForeignKey('events.id'))
    seat_id = Column(Integer, ForeignKey('seats.id'))
    status = Column(String, default='reserved')
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship('User', back_populates='tickets')
```

---

### 5. **Payments**

| Поле       | Тип      | Примітка                   |
| ---------- | -------- | -------------------------- |
| id         | int, PK  |                            |
| ticket_id  | FK       | Квиток                     |
| user_id    | FK       | Хто оплатив                |
| amount     | float    | Сума                       |
| method     | str      | Наприклад, 'card'          |
| status     | str      | pending / success / failed |
| created_at | datetime |                            |

```python
class Payment(Base):
    __tablename__ = 'payments'
    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, ForeignKey('tickets.id'))
    user_id = Column(Integer, ForeignKey('users.id'))
    amount = Column(Float, nullable=False)
    method = Column(String)
    status = Column(String, default='pending')
    created_at = Column(DateTime, default=datetime.utcnow)
```

---

## ⚙️ Залежності між модулями

```
AuthService → UserService
EventService → SeatService
SeatService → TicketService
TicketService → PaymentService
PaymentService → TaskService
```

---

## 🧠 Послідовність розробки

1️⃣ **Створити базову структуру проекту та підключення до БД**
2️⃣ **Реалізувати AuthService (реєстрація, логін, JWT)**
3️⃣ **UserService (отримання профілю, оновлення)**
4️⃣ **EventService (CRUD для фільмів)**
5️⃣ **SeatService (генерація місць, перевірка доступності)**
6️⃣ **TicketService (створення бронювання, статуси)**
7️⃣ **PaymentService (ініціювання, підтвердження, webhook)**
8️⃣ **TaskService (очищення броней, нагадування)**

---

## 🧮 Логіка процесів

### 🔸 Резервування місця

1. Користувач надсилає POST `/events/{id}/seats/{seat_id}/reserve`
2. Перевіряється, чи місце вільне
3. Створюється запис `Ticket` зі статусом *reserved*
4. `Seat.is_reserved` → True

### 🔸 Оплата квитка

1. Користувач надсилає `/tickets/purchase`
2. Створюється `Payment` зі статусом *pending*
3. Мок-система відповідає *success*
4. `Ticket.status` → *paid*, `Payment.status` → *success*

### 🔸 Скасування квитка

1. POST `/tickets/{id}/cancel`
2. Перевіряється час події
3. Якщо дозволено — `Ticket.status = cancelled`, `Seat.is_reserved = False`

---

## 🛠️ Рекомендації по роботі в команді

* Кожен модуль має свій **router**, **service**, **repository**, **schemas**.
* Для асинхронних операцій використовувати `async SQLAlchemy` + `AsyncSession`.
* Для тестів — `pytest-asyncio`.
* Валідація вхідних даних через **Pydantic**.
* Розділити `.env` (секрети, ключі JWT, URL БД).

---

## 📦 Модулі в пріоритеті

1. **Auth / Users** — базова безпека.
2. **Events / Seats** — основний контент.
3. **Tickets / Payments** — ядро бізнес-логіки.
4. **Tasks / Admin** — автоматизація й аналітика.

---

## 🚀 Завершальні кроки

* Налаштувати `alembic` для міграцій.
* Підготувати тестові дані (seeds).
* Зібрати документацію Swagger (`/docs`).
* Оформити Dockerfile (опціонально).

---

> ✅ **Мета цього гіда:** дати зрозумілий порядок дій та структурне бачення системи, щоб розробники могли швидко увійти в проект, знати залежності та не дублювати логіку.
