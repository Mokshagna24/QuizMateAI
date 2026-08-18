from .core.app import app

# Initialize the database exactly once when the backend package starts.
from .db.database import init_db
init_db()

# Import route modules so their decorators register the endpoints.
from .routes import auth  # noqa: F401,E402
from .routes import documents  # noqa: F401,E402
from .routes import health  # noqa: F401,E402
from .routes import quiz  # noqa: F401,E402
from .routes import results  # noqa: F401,E402
from .routes import summary  # noqa: F401,E402
from .routes import topics  # noqa: F401,E402
from .routes import youtube  # noqa: F401,E402
