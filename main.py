from src.view import start
from nicegui import ui

start()

# TODO: Use better secret
ui.run(
    storage_secret="123",
    port=6969,
    reload=True,
    reconnect_timeout=30.0,
    binding_refresh_interval=0.2
)
