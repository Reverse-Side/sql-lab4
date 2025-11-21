
from fastapi import APIRouter, HTTPException, status

from src.auth.dependencies import AuthUser
from src.tickets.schemas import TicketCreate, TicketResponse
from src.tickets.service import TicketServiceDep

router = APIRouter(
    prefix="/tickets",
    tags=["Tickets"]
)


@router.post(
    "/",
    response_model=TicketResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Придбати квиток на подію (потрібна авторизація)",
)
async def buy_ticket(
    ticket_data: TicketCreate,
    ticket_service: TicketServiceDep,
    current_user: AuthUser
):
    try:
        new_ticket = await ticket_service.create_ticket(
            ticket_data=ticket_data, 
            owner_id=current_user.sub
        )
        return new_ticket

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        ) 
    
@router.get(
    "/{ticket_id}",
    response_model=list[TicketResponse],
    summary="Отримати квиток за ID (тільки для власника)"
)
async def get_my_ticket(ticket_id: int, ticket_service: TicketServiceDep, current_user: AuthUser):
    tickets = await ticket_service.get_tickets_by_owner(owner_id=current_user.sub)
    return tickets


async def get_ticket_by_id(ticket_id: int, ticket_service: TicketServiceDep, current_user: AuthUser):
    ticket = await ticket_service.get_ticket_by_id(ticket_id)

    if not ticket or ticket.owner_id != current_user.sub:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ticket not found",
        )
    return ticket