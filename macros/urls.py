from django.urls import path
from django.contrib.auth.decorators import login_required
from .views import MacrosView, version_webhook, version_webhook_prod_otta, version_webhook_preprod_otta


urlpatterns = [
    path("macros/", login_required(MacrosView.as_view()), name='macros'),
    path("version/", version_webhook, name='version'),
    path("version/prod/otta", version_webhook_prod_otta, name='prod'),
    path("version/preprod/otta", version_webhook_preprod_otta, name='preprod')
]
