from apscheduler.schedulers.background import BackgroundScheduler
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response
from requests import request
from statistics import mode
import bullcrawler
import time

BULLS = {}
LAST_REFRESH = None

templates = Jinja2Templates(directory="templates")

def get_bulls():
    global LAST_REFRESH
    LAST_REFRESH = time.time()
    global BULLS
    BULLS = bullcrawler.get_bulls()

async def home(request):
    return templates.TemplateResponse(request, "index.html", context={"good_bulls": BULLS, "ts": LAST_REFRESH})

get_bulls()
scheduler = BackgroundScheduler()
scheduler.add_job(get_bulls, "interval", hours=1)
scheduler.start()

routes = [
    Route("/", endpoint=home),
    Mount("/static", StaticFiles(directory='static'), name='static')
]

app = Starlette(routes=routes)