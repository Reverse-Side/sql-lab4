from fastapi import APIRouter
from fastapi import APIRouter, Depends, status, HTTPException
from src.payments.schemas import PaymentCreate, PaymentResponse, PaymentStatusUpdate
from src.payments.service import PaymentServiceDep
from src.users.models import UserORM
from src.auth.dependencies import get_current_user 



router = APIRouter(prefix = "/payments", tags=["Payments"])

@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED, summary="Create payment (потрібна авторизація)")
async def process_payment_request(
    data: PaymentCreate,
    service: PaymentServiceDep,
    current_user: UserORM = Depends(get_current_user)
):
    try:
        new_payment = await service.process_payment(data, current_user.id)
        return new_payment
    except HTTPException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found")
    except HTTPException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Ticket already paid")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    
@router.patch(
    "/{payment_id}/status",
    response_model=PaymentResponse,
    summary="Update payment status (Admin only)"
)
async def update_payment_status(
    payment_id: int,
    data: PaymentStatusUpdate,
    payment_service: PaymentServiceDep,
    current_user: UserORM = Depends(get_current_user)
):
    try:
        return await payment_service.update_payment_status(payment_id, data)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, ddetail=f"Помилка оновлення статусу: {str(e)}")
    