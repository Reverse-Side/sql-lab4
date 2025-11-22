
from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.dependencies import AuthAdmin
from src.events.dependencies import EventServiceDep
from src.events.exceptions import EventNotFoundError, EventPermissionError
from src.events.schemas import EventCreate, EventResponse, EventUpdate
from src.mixin_schemas import Collection, Pagination

router = APIRouter(
    prefix="/events",
    tags=["Events"],
)


@router.post(
    "",
    response_model=EventResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create event (потрібна авторизація)",
)
async def create_event(
    event_data: EventCreate,
    # ВИПРАВЛЕНО: Видалено '= Depends()'
    event_service: EventServiceDep,
    current_user: AuthAdmin,
):

    # ВИПРАВЛЕНО: Змінено метод з 'create' на 'create_event' (як у service.py)
    new_event = await event_service.create_event(event_data, current_user.sub)
    return new_event


@router.get(
    "/{event_id}",
    response_model=EventResponse,
    summary="Get event by id (потрібна авторизація)",
)
async def get_event(
    event_id: int,
    # ВИПРАВЛЕНО: Видалено '= Depends()'
    service: EventServiceDep,
):
    try:
        return await service.get_event(event_id)
    except EventNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.get(
    "",
    response_model=Collection[EventResponse],
    summary="Отримати список усіх подій",
)
async def get_all_events(
    service: EventServiceDep,pagin=Depends(Pagination)
):
    """Повертає список усіх подій, доступних у системі."""
    return await service.get_all_events(pagin)


@router.patch(
    "/{event_id}",
    response_model=EventResponse,
    summary="Оновити дані події (потрібна авторизація та права власника)",
)
async def update_event(
    event_id: int,
    update_data: EventUpdate,
    # ВИПРАВЛЕНО: Видалено '= Depends()'
    service: EventServiceDep,
    current_user: AuthAdmin,
):
    """
    Оновлює подію. Дозволено лише власнику події.
    """
    try:
        return await service.update_event(
            event_id=event_id, update_data=update_data, current_user_id=current_user.sub
        )
    except EventNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except EventPermissionError as e:
        # Виняток, якщо користувач не є власником (403 Forbidden)
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.delete(
    "/{event_id}",
    summary="Видалити подію (потрібна авторизація та права власника)",
)
async def delete_event(
    event_id: int,
    # ВИПРАВЛЕНО: Видалено '= Depends()'
    service: EventServiceDep,
    current_user: AuthAdmin,
):
    """
    Видаляє подію. Дозволено лише власнику події.
    """
    try:
        return await service.delete_event(
            event_id=event_id, current_user_id=current_user.sub
        )
    except EventNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except EventPermissionError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
