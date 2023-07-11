from django.shortcuts import render
from .tasks import connect_wallets
from .models import Wallet, Proxy


def connect_wallets_view(request):
    if request.method == 'POST':
        selected_wallets = request.POST.getlist('selected_wallets')
        use_proxies = request.POST.get('use_proxies')
        seed_keys = list(Wallet.objects.filter(
            pk__in=selected_wallets).values_list('seed_key', flat=True))
        proxy_params = None
        if use_proxies:
            random_proxy = Proxy.objects.order_by('?').first()
            if random_proxy:
                proxy_params = [random_proxy.host, random_proxy.port,
                                random_proxy.username, random_proxy.password]
        # запуск фоновой задачи через Celery
        connect_wallets.delay(seed_keys, proxy_params)
        return render(request, 'venomconnect/connect.html', {'message': 'Задача по подключению кошельков запущена.'})

    wallets = Wallet.objects.all()
    return render(request, 'venomconnect/connect.html', {'wallets': wallets})
