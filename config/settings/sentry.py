from config.env import env
from config.django.base import SERVER_ENV

SENTRY_DSN = env("SENTRY_DSN", default="")

if SENTRY_DSN and SERVER_ENV != "config.django.local":
    environment = SERVER_ENV
    track_performance = environment == "config.django.prod"

    import sentry_sdk
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.django import DjangoIntegration

    def traces_sampler(sampling_context):
        if not track_performance:
            return 0

        transaction_context = sampling_context.get("transaction_context")

        if transaction_context is None:
            return 0

        op = transaction_context.get("op")

        if op is None:
            return 0

        if op == "celery.task":
            return 0

        return 0.5

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        environment=environment,
        traces_sampler=traces_sampler,
        integrations=[
            DjangoIntegration(),
            CeleryIntegration(),
        ],
        send_default_pii=False,
    )
