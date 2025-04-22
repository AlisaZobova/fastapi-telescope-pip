import os

from .router import router
from .middleware import TelescopeMiddleware

# create constant with full path to components
TELESCOPE_COMPONENTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "", "app/dashboard/templates/components")

__all__ = ['router', 'TELESCOPE_COMPONENTS_DIR', 'TelescopeMiddleware']