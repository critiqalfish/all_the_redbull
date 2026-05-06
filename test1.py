from functools import reduce
guh = [{'name': 'Summer Edition Sudachi-Lime', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Dosen'}, {'name': 'Spring Edition Kirsche-Sakura Sugarfree', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Dosen'}, {'name': 'Summer Edition Sudachi-Lime Sugarfree', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Dosen'}, {'name': 'Spring Edition Kirsche-Sakura', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Dosen'}, {'name': 'Energy Drink Lime Green Edition', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Dosen'}, {'name': 'Energy Drink White Peach', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Dosen'}, {'name': 'Energy Drink ICE Edition Iced Gummy Bear', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Dosen'}, {'name': 'Energy Drink Pink Edition Waldbeere Sugarfree', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Liter'}, {'name': 'Energy Drink Green Edition Kaktusfrucht', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Dosen'}, {'name': 'Energy Drink Sea Blue Edition Juneberry', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Dosen'}, {'name': 'Energy Drink Lilac Edition Sugarfree', 'newPrice': 139, 'oldPrice': 159, 'condition': 'ab 2 Dosen'}]

def red(x, y):
    if type(x) is type({}):
        return [x, y]
    elif type(x) is type([]):
        return x + [y]

print(reduce(red, guh))