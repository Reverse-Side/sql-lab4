from fastapi import APIRouter, Depends, HTTPException, status

from src.auth.dependencies import AuthAdmin, AuthUser
from src.payments.schemas import PaymentCreate, PaymentResponse, PaymentStatusUpdate
from src.payments.service import PaymentServiceDep
from src.users.models import UserORM

router = APIRouter(prefix="/payments", tags=["Payments"])


@router.post(
    "",
    response_model=PaymentResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create payment (потрібна авторизація)",
)
async def process_payment_request(
    data: PaymentCreate, service: PaymentServiceDep, current_user: AuthUser
):
    try:
        new_payment = await service.process_payment(data, current_user.sub)
        return new_payment
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ticket not found"
        )
    except HTTPException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Ticket already paid"
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.patch(
    "/{payment_id}/status",
    response_model=PaymentResponse,
    summary="Update payment status (Admin only)",
)
async def update_payment_status(
    payment_id: int,
    data: PaymentStatusUpdate,
    payment_service: PaymentServiceDep,
    current_user: AuthAdmin,
):
    try:
        return await payment_service.update_payment_status(payment_id, data)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Помилка оновлення статусу: {str(e)}",
        )
