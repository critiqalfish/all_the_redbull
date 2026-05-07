from requests import request
from PyPDF2 import PdfReader
from statistics import mode
from datetime import date
from io import BytesIO
import re

def get_bulls(billa=True, spar=True, lidl=True, adeg=False):
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101 Firefox/125.0"}
    good_bulls = {"billa": [], "spar": [], "lidl": [], "adeg": []}

    try:
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
    except Exception as e:
        print(e)
    
    try:
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
    except Exception as e:
        print(e)

    try:
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
    except Exception as e:
        print(e)

    try:
        ADEG_UVP = 159
        if adeg:
            currKW = date.today().isocalendar()[1]
            print(f"adeg KW{currKW}:")
            locations = ["Aktiv", "NV"]

            for location in locations:
                pdf = None
                found_kw = None
                for kw_offset in range(-1, 1):
                    kw = currKW - kw_offset
                    url = f"https://www.adeg.at/fileadmin/user_upload/{location}_Stamm_ADEG_FB_KW{kw}.pdf"
                    res = request("GET", url, headers=headers)
                    if res.status_code == 200:
                        pdf = res.content
                        found_kw = kw
                        break

                if pdf is None:
                    print(f"  {location}: keine PDF gefunden (KW{currKW}-KW{currKW - 2})")
                    continue

                text = get_pdf_text(pdf)
                bulls = parse_adeg_text(text, location, found_kw)

                if not bulls:
                    bulls.append(
                        {
                            "name": "Red Bull",
                            "newPrice": ADEG_UVP,
                            "oldPrice": ADEG_UVP,
                            "condition": f"ADEG {location} KW{found_kw} (UVP)",
                        }
                    )

                print(f"  {location} KW{found_kw}: 200")
                good_bulls["adeg"].extend(bulls)
    except Exception as e:
        print(e)

    real_good_bulls = {}
    try:
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
                if bull["newPrice"] == modes["nP"] and bull["oldPrice"] == modes["oP"]:
                    if shop in ["billa", "lidl"] and bull["condition"].split(" ")[:-1] == modes["cond"].split(" ")[:-1]:
                        u_bull = bull.copy()
                        u_bull["name"] = "Red Bull Editions"
                        u_bull["condition"] = modes["cond"]
                        uni_bulls.append(u_bull)
                    elif shop in ["spar", "adeg"]:
                        u_bull = bull.copy()
                        u_bull["name"] = "Red Bull Editions"
                        u_bull["condition"] = modes["cond"]
                        uni_bulls.append(u_bull)
                    
                    else:
                        uni_bulls.append(bull)
                else:
                    uni_bulls.append(bull)

            real_good_bulls[shop] = [dict(t) for t in {tuple(d.items()) for d in uni_bulls}]
    except Exception as e:
        print(e)

    print("done")
    return real_good_bulls

def get_pdf_text(pdf):
    reader = PdfReader(BytesIO(pdf))
    text = ""
    for page in reader.pages:
        text += page.extract_text()

    return text


def parse_adeg_text(text, location, kw):
    bulls = []
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    for i, line in enumerate(lines):
        if "red bull" not in line.lower():
            continue

        first_line = re.sub(r"^.*?(?=Red Bull)", "", line, flags=re.IGNORECASE)
        name_parts = [first_line]
        desc_end = i
        for j in range(i + 1, min(len(lines), i + 8)):
            next_line = lines[j]
            if re.match(r"^(ab\s+\d+\s+Stück|1\s*(Liter|kg))", next_line):
                break
            name_parts.append(next_line)
            desc_end = j

        name = " ".join(name_parts).strip()
        name = re.sub(r"([a-zA-Z])(\d)", r"\1 \2", name)
        new_price = None
        old_price = None
        condition = f"KW{kw}"

        context = lines[desc_end + 1 : min(len(lines), i + 15)]

        for idx, ctx in enumerate(context):
            if condition == f"ADEG {location}":
                cond_match = re.match(r"^ab\s+(\d+\s+Stück)\s*(je)?.*", ctx)
                if cond_match:
                    condition = cond_match.group(1)

            if old_price is None and "statt" in ctx.lower():
                statt_match = re.search(
                    r"(\d+[.,]\d{2})\s*Statt\s*(\d+[.,]\d{2})", ctx, re.IGNORECASE
                )
                if statt_match:
                    old_price = int(float(statt_match.group(2).replace(",", ".")) * 100)

            if ctx.startswith("ADEG UVP*"):
                if condition == f"ADEG {location}":
                    mult_match = re.search(r"ab\s+(\d+)\s+Stück", ctx)
                    if mult_match:
                        condition = f"ab {mult_match.group(1)} Stück"
                for m in re.findall(r"(\d+[.,]\d{2})", ctx):
                    old_price = int(float(m.replace(",", ".")) * 100)
                if old_price is None and idx + 1 < len(context):
                    next_ctx = context[idx + 1]
                    for m in re.findall(r"(\d+[.,]\d{2})", next_ctx):
                        old_price = int(float(m.replace(",", ".")) * 100)
                        break

            if (
                new_price is None
                and "Liter" not in ctx
                and "kg" not in ctx
                and not ctx.startswith("ADEG UVP")
            ):
                price_match = re.match(r"^(\d+[.,]\d{2})", ctx)
                if price_match:
                    new_price = int(float(price_match.group(1).replace(",", ".")) * 100)

        if new_price is not None:
            bulls.append(
                {
                    "name": name,
                    "newPrice": new_price,
                    "oldPrice": old_price,
                    "condition": condition,
                }
            )

    return bulls

def print_bulls(bulls):
    for key in bulls.keys():
        print(key.upper() + ":")
        for bull in bulls[key]:
            print(f"\t- {bull['name']} {' ' * (45 - len(bull['name']))}| {int(bull['newPrice']) / 100} < {int(bull['oldPrice']) / 100} ? {bull['condition']}")

if __name__ == "__main__":
    print_bulls(get_bulls())