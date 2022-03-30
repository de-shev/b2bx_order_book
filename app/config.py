from pydantic import BaseSettings


class AppSettings(BaseSettings):
    b2bx_url: str = 'https://b2t-api-b2bx.flexprotect.org/marketdata/info'
    stream_event: str = 'Book'
    stream_event_args: list = ['btc_usd']


def get_app_settings() -> AppSettings:
    return AppSettings()
