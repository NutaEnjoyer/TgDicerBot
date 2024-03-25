from .main.main import register_handlers as main_handlers

def register(dp):
	handlers = (
		main_handlers,
	)

	for handler in handlers:
		handler(dp)
