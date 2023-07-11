from celery import shared_task
from .utils.seleniumtest import connect_venom_vallet


@shared_task
def connect_wallets(seed_keys, proxy_params=None):
    for seed_key in seed_keys:
        connect_venom_vallet(seed_key, proxy_params)
    return print('success')
