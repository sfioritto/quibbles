from config import settings
from lamson import view
from lamson.routing import Router
from lamson.server import Relay
from app.model import state
import jinja2
import logging
import logging.config
import os

logging.config.fileConfig("config/test_logging.conf")

# the relay host to actually send the final message to (set debug=1 to see what
# the relay is saying to the log server).
settings.relay = Relay(host=settings.relay_config['host'], 
                       port=settings.relay_config['port'], debug=0)


settings.receiver = None

Router.defaults(**settings.router_defaults)
Router.load(settings.handlers)
Router.RELOAD=True
Router.LOG_EXCEPTIONS=False
Router.STATE_STORE=state.UserStateStorage()

view.LOADER = jinja2.Environment(
    loader=jinja2.PackageLoader(settings.template_config['dir'], 
                                settings.template_config['module']))


