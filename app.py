from starlette.applications import Starlette
from starlette.routing import Route
from starlette.templating import Jinja2Templates
from starlette.responses import Response
import requests

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/125.0"}

session = requests.Session()
session.headers = HEADERS

templates = Jinja2Templates(directory="templates")

async def home(request):
    return templates.TemplateResponse(request, "index.html")

routes = [
    Route("/", endpoint=home)
]

app = Starlette(routes=routes)