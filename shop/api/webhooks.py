import json
from ninja import Router, Schema
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from yookassa.domain.notification import WebhookNotification

from shop.models import Order

router = Router()

@router.post("/yookassa", auth=None)
@csrf_exempt
def yookassa_webhook(request):
    """
    Handle webhooks from Yookassa.
    """
    try:
        event_json = json.loads(request.body)
        notification_object = WebhookNotification(event_json)
        event = notification_object.event
        payment = notification_object.object

        if event == 'payment.succeeded':
            order_id = payment.metadata.get('order_id')
            if order_id:
                order = get_object_or_404(Order, id=int(order_id))
                # Можно добавить проверку, что сумма платежа совпадает с суммой заказа
                if order.status == 'pending':
                    order.status = 'confirmed'
                    order.save()

        # Другие статусы можно обработать тут (canceled, waiting_for_capture)

    except json.JSONDecodeError:
        return HttpResponse(status=400)
    except Exception as e:
        # Логирование ошибки
        print(f"Error handling Yookassa webhook: {e}")
        return HttpResponse(status=500)

    return HttpResponse(status=200) 