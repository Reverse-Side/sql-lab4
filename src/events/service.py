
from src.events.exceptions import EventNotFoundError, EventPermissionError
from src.events.schemas import EventCreate, EventResponse, EventUpdate
from src.filter import eq
from src.interface import IUnitOfWork
from src.mixin_schemas import Collection, Pagination
from src.tickets.schemas import TicketCreate
from src.tickets.service import TicketServiceDep


class EventService:

    def __init__(self, uow: IUnitOfWork, ticket_service: TicketServiceDep):
        self.uow = uow
        self.ticket_service = ticket_service

    async def create_event(
        self, event_data: EventCreate, owner_id: int
    ) -> EventResponse:
        
        async with self.uow as work:
            event_dict = event_data.model_dump()
            
            # ВИПРАВЛЕННЯ: Видалення інформації про часовий пояс для сумісності з PostgreSQL TIMESTAMP WITHOUT TIME ZONE
            if 'start_time' in event_dict and event_dict['start_time'].tzinfo is not None:
                event_dict['start_time'] = event_dict['start_time'].replace(tzinfo=None)
            
            if 'end_time' in event_dict and event_dict['end_time'].tzinfo is not None:
                event_dict['end_time'] = event_dict['end_time'].replace(tzinfo=None)

            new_event_orm = await work.events.add(
                data={**event_dict, "owner_id": owner_id}
            )

            # Логіка створення квитка
            if "price" in event_dict and "amount" in event_dict:
                ticket_create_data = TicketCreate(
                    event_id=new_event_orm.id,
                    ticket_type="Standard", # Припускаємо, що це стандартний тип
                    price=event_dict["price"],
                    amount=event_dict["amount"]
                )
                await self.ticket_service.create_ticket(
                    ticket_data=ticket_create_data,
                    owner_id=owner_id # Або інший логін, якщо квиток створює не адміністратор
                )

            await work.commit()

            return EventResponse.model_validate(new_event_orm)

    async def get_event(self, event_id: int) -> EventResponse:
        
        async with self.uow as work:
            event_orm = await work.events.find(id=eq(event_id))

            if not event_orm:
                raise EventNotFoundError(f"Подію з ID {event_id} не знайдено.")

            return EventResponse.model_validate(event_orm)

    async def get_all_events(self,pagin:Pagination) -> Collection[EventResponse]:
        
        async with self.uow as work:
            events_orm = await work.events.find_all(offset=pagin.offset,limit=pagin.limit)

            events_models = [EventResponse.model_validate(e) for e in events_orm]
            return Collection(offset =pagin.offset,limit=pagin.limit,collection=events_models,size=len(events_models))

    async def update_event(
        self, event_id: int, update_data: EventUpdate, current_user_id: int
    ) -> EventResponse:
        
        async with self.uow as work:
            event_orm = await work.events.find(id=eq(event_id))

            if not event_orm:
                raise EventNotFoundError(f"Подію з ID {event_id} не знайдено.")

            if event_orm.owner_id != current_user_id:
                raise EventPermissionError("Ви можете оновлювати лише власні події.")

            update_dict = update_data.model_dump(exclude_unset=True)

            # ВИПРАВЛЕННЯ: Видалення інформації про часовий пояс для оновлення
            if 'start_time' in update_dict and update_dict['start_time'].tzinfo is not None:
                update_dict['start_time'] = update_dict['start_time'].replace(tzinfo=None)
            
            if 'end_time' in update_dict and update_dict['end_time'].tzinfo is not None:
                update_dict['end_time'] = update_dict['end_time'].replace(tzinfo=None)


            updated_event_orm = await work.events.update(_id=event_id, data=update_dict)

            await work.commit()

            if updated_event_orm is None:
                raise EventNotFoundError(f"Подію з ID {event_id} не знайдено.")

            return EventResponse.model_validate(updated_event_orm)

    async def delete_event(self, event_id: int, current_user_id: int) -> bool:
        
        async with self.uow as work:
            event_orm = await work.events.find(id=eq(event_id))

            if not event_orm:
                raise EventNotFoundError(f"Подію з ID {event_id} не знайдено.")

            if event_orm.owner_id != current_user_id:
                raise EventPermissionError("Ви можете видаляти лише власні події.")

            deleted = await work.events.delete(_id=event_id)

            await work.commit()

            return EventResponse.model_validate(deleted)