from bs4 import BeautifulSoup
from requests import request
import os

if __name__ == "__main__":
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
    res = request("GET", "https://www.billa.at/unsere-aktionen/flugblatt", headers=headers)
    html = res.text
    print(res.status_code)

    soup = BeautifulSoup(html, "html.parser")
    tags = soup.find_all("a", attrs={"aria-label": True})
    for tag in tags:
        if tag["aria-label"].lower().find("flugblatt") >= 0:
            url = tag["href"]
            print(url)

            os.makedirs("download", exist_ok=True)
            filename = url.split("/")[-1].lower()
            kw = [g for g in filename.split("_") if g.startswith("kw")][0].removeprefix("kw")
            plus = True if filename.find("plus") >= 0 else False
            
            print(filename, kw, plus)
            pdf = request("GET", url, headers=headers)
            with open("download/BILLA" + ("+_KW" if plus else "_KW") + kw + ".pdf", "wb") as file:
                file.write(pdf.content)
