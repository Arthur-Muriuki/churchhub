from django.db.utils import OperationalError, ProgrammingError
from .models import ChurchProfile


def church_config(request):
    """
    Injects the active ChurchProfile globally into all template contexts.
    """
    try:
        config = ChurchProfile.get_solo()
    except (OperationalError, ProgrammingError):
        config = None
    return {"church_config": config}