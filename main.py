from datetime import date
from io import BytesIO
from PyPDF2 import PdfReader

from requests import request

def get_bulls(billa=True, spar=True, lidl=True, adeg=False):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
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
                    "newPrice": bull["gridbox"]["data"]["lidlPlus"][0]["price"]["price"] * 100,
                    "oldPrice": bull["gridbox"]["data"]["lidlPlus"][0]["price"]["oldPrice"] * 100,
                    "condition": bull["gridbox"]["data"]["lidlPlus"][0]["lidlPlusText"]
                })
            elif "oldprice" in bull["gridbox"]["data"]["price"]:
                #normale aktion
                good_bulls["lidl"].append({
                    "name": bull["gridbox"]["data"]["fullTitle"],
                    "newPrice": bull["gridbox"]["data"]["price"]["price"] * 100,
                    "oldPrice": bull["gridbox"]["data"]["price"]["oldPrice"] * 100,
                    "condition": None
                })

# NOT FINISHED YET
    if adeg:
        # Fakker see und WINKLER sind aktiv
        # ARRIACH LIM is NV
        currKW = date.today().isocalendar()[1]
        locations = ["Aktiv", "NV", ]


        for location in locations:
            adeg = f"https://www.adeg.at/fileadmin/user_upload/{location}_Stamm_ADEG_FB_KW{currKW}.pdf"
            res = request("GET", adeg.replace("{location}", location), headers=headers)
            print(f"adeg {location}: " + str(res.status_code))
            if res.status_code != 200:
                print(f"Keine PDF für {location} gefunden, überspringe...")
                break
            
            pdf = res.content
            text = get_pdf_text(pdf)
            print(text)



    return good_bulls


def get_pdf_text(pdf):
    reader = PdfReader(BytesIO(pdf))
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    return text

def print_bulls(bulls):
    for key in bulls.keys():
        print(key.upper() + ":")
        for bull in bulls[key]:
            print(f"\t- {bull["name"]} {" " * (45 - len(bull["name"]))}| {int(bull["newPrice"]) / 100} < {int(bull["oldPrice"]) / 100} ? {bull["condition"]}")

if __name__ == "__main__":
    print_bulls(get_bulls())