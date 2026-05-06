from statistics import mode
bulls = [{'name': 'Summer Edition Sudachi-Lime', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Dosen'}, {'name': '8 pack', 'newPrice': 559, 'oldPrice': 649, 'condition': 'ab 2 Packungen'}, {'name': 'Spring Edition Kirsche-Sakura Sugarfree', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Dosen'}, {'name': 'Summer Edition Sudachi-Lime Sugarfree', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Dosen'}, {'name': 'Spring Edition Kirsche-Sakura', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Dosen'}, {'name': 'Energy Drink Lime Green Edition', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Dosen'}, {'name': 'Energy Drink White Peach', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Dosen'}, {'name': 'Energy Drink ICE Edition Iced Gummy Bear', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Dosen'}, {'name': 'Energy Drink Pink Edition Waldbeere Sugarfree', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Liter'}, {'name': 'Energy Drink Green Edition Kaktusfrucht', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Dosen'}, {'name': 'Energy Drink Sea Blue Edition Juneberry', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Dosen'}, {'name': 'Energy Drink Lilac Edition Sugarfree', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Dosen'}]

data = {"nP": [], "oP": [], "cond": []}
for bull in bulls:
    data["nP"].append(bull["newPrice"])
    data["oP"].append(bull["oldPrice"])
    data["cond"].append(bull["condition"])

modes = {"nP": mode(data["nP"]), "oP": mode(data["oP"]), "cond": mode(data["cond"])}
print(modes)

uni_bulls = []
for bull in bulls:
    if bull["newPrice"] == modes["nP"] and bull["oldPrice"] == modes["oP"] and bull["condition"].split(" ")[:-1] == modes["cond"].split(" ")[:-1]:
        u_bull = bull
        u_bull["name"] = "Red Bull Editions"
        u_bull["condition"] = modes["cond"]
        uni_bulls.append(u_bull)
    else:
        uni_bulls.append(bull)

uni_bulls = [dict(t) for t in {tuple(d.items()) for d in uni_bulls}]

