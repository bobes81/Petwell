"""A database lease protects checkout without holding locks over Stripe I/O."""

from contextlib import contextmanager
from datetime import timedelta
from hashlib import sha256
from uuid import uuid4

from django.db.models import Q
from django.utils import timezone

from orders.models import CheckoutState, Order


class CheckoutBusy(Exception):
    pass


def session_digest(request):
    if not request.session.session_key:
        request.session.create()
    return sha256(request.session.session_key.encode()).hexdigest()


class CheckoutLease:
    def __init__(self, state, token):
        self.key = state.pk
        self.token = token
        self.active_order = state.active_order

    def current(self):
        return CheckoutState.objects.filter(
            pk=self.key,
            processing_token=self.token,
            processing_until__gt=timezone.now(),
        )

    def assert_current(self):
        if not self.current().exists():
            raise CheckoutBusy

    def set_order(self, order):
        if not self.current().update(active_order=order):
            raise CheckoutBusy
        self.active_order = order


@contextmanager
def checkout_lease(request):
    key = session_digest(request)
    pending_id = request.session.get("pending_order")
    pending = (
        Order.objects.filter(public_id=pending_id).first()
        if pending_id
        else None
    )
    CheckoutState.objects.get_or_create(
        pk=key,
        defaults={"active_order": pending},
    )
    token = uuid4()
    now = timezone.now()
    acquired = (
        CheckoutState.objects.filter(pk=key)
        .filter(
            Q(processing_until__isnull=True) | Q(processing_until__lte=now),
        )
        .update(
            processing_token=token,
            processing_until=now + timedelta(seconds=120),
        )
    )
    if not acquired:
        raise CheckoutBusy
    try:
        state = CheckoutState.objects.select_related("active_order").get(
            pk=key
        )
        yield CheckoutLease(state, token)
    finally:
        CheckoutState.objects.filter(pk=key, processing_token=token).update(
            processing_token=None,
            processing_until=None,
        )
