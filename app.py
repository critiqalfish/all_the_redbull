from apscheduler.schedulers.background import BackgroundScheduler
from starlette.templating import Jinja2Templates
from starlette.staticfiles import StaticFiles
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import Response
from requests import request
from statistics import mode
import time

BULLS = {}
LAST_REFRESH = None

templates = Jinja2Templates(directory="templates")

def get_bulls(billa=True, spar=True, lidl=True):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/125.0"}
    good_bulls = {"billa": [], "spar": [], "lidl": []}

    if billa:
        billa = "https://shop.billa.at/api/product-discovery/products/search/red-bull?pageSize=50&sortBy=relevance&countriesOfOriginList=Österreich&categoryNavigation=categories.0:Getränke"
        res = request("GET", billa, headers=headers)
        bulls = res.json()["results"]
        print("billa: " + str(res.status_code))

        for bull in bulls:
            if bull["name"].lower().find("pack") == -1:
                if bull["inPromotion"]:
                    good_bulls["billa"].append({
                        "name": bull["name"].removeprefix("Red Bull "),
                        "newPrice": bull["price"]["regular"]["value"],
                        "oldPrice": bull["price"]["regular"]["promotionValue"],
                        "condition": bull["price"]["regular"]["promotionText"]
                    })
    
    if spar:
        spar = "https://bfs-geo.spar-ics.com/fact-finder/rest/v5/search/products_at?query=red-bull&hitsPerPage=10&useAsn=false&marketId=NATIONAL&page="
        page = 1
        pages = 1
        while page <= pages:
            res = request("GET", spar + str(page), headers=headers)
            bulls = res.json()
            print("spar: " + str(res.status_code))

            if page == 1:
                pages = int(bulls["paging"]["pageCount"])

            bulls = bulls["hits"]
            for bull in bulls:
                mv = bull["masterValues"]
                gv = mv["geoInformation"][0]["geoValues"]

                if gv["inAngebot"]:
                    good_bulls["spar"].append({
                        "name": mv["name2"] if "name2" in mv else "",
                        "newPrice": gv["calculatedPrice"],
                        "oldPrice": gv["stattPrice"],
                        "condition": gv["promotionBadgeText"]
                    })

            page += 1

    if lidl:
        lidl = "https://www.lidl.at/q/api/search?q=red-bull&category=Essen+%26+Trinken%2FGetr%C3%A4nke&fetchsize=48&locale=de_AT&assortment=AT&offset=0&version=2.1.0"
        res = request("GET", lidl, headers=headers)
        bulls = res.json()["items"]
        print("lidl: " + str(res.status_code))

        for bull in bulls:
            if "price" not in bull["gridbox"]["data"]["price"]:
                #lidlplus aktion
                good_bulls["lidl"].append({
                    "name": bull["gridbox"]["data"]["fullTitle"],
                    "newPrice": int(bull["gridbox"]["data"]["lidlPlus"][0]["price"]["price"] * 100),
                    "oldPrice": int(bull["gridbox"]["data"]["lidlPlus"][0]["price"]["oldPrice"] * 100),
                    "condition": bull["gridbox"]["data"]["lidlPlus"][0]["lidlPlusText"]
                })
            elif "oldprice" in bull["gridbox"]["data"]["price"]:
                #normale aktion
                good_bulls["lidl"].append({
                    "name": bull["gridbox"]["data"]["fullTitle"],
                    "newPrice": int(bull["gridbox"]["data"]["price"]["price"] * 100),
                    "oldPrice": int(bull["gridbox"]["data"]["price"]["oldPrice"] * 100),
                    "condition": None
                })

    real_good_bulls = {}
    for shop, bulls in good_bulls.items():
        if not bulls:
            real_good_bulls[shop] = []
            continue

        data = {"nP": [], "oP": [], "cond": []}
        for bull in bulls:
            data["nP"].append(bull["newPrice"])
            data["oP"].append(bull["oldPrice"])
            data["cond"].append(bull["condition"])

        modes = {"nP": mode(data["nP"]), "oP": mode(data["oP"]), "cond": mode(data["cond"])}

        uni_bulls = []
        for bull in bulls:
            if bull["newPrice"] == modes["nP"] and bull["oldPrice"] == modes["oP"] and bull["condition"].split(" ")[:-1] == modes["cond"].split(" ")[:-1]:
                u_bull = bull.copy()
                u_bull["name"] = "Red Bull Editions"
                u_bull["condition"] = modes["cond"]
                uni_bulls.append(u_bull)
            else:
                uni_bulls.append(bull)

        real_good_bulls[shop] = [dict(t) for t in {tuple(d.items()) for d in uni_bulls}]

    print("done")
    global LAST_REFRESH
    LAST_REFRESH = time.time()
    global BULLS
    BULLS = real_good_bulls

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