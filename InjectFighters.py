from os.path import join
from sqlite3 import connect

FighterDB = connect(join("Data", "MainEvent.db"))
Cursor = FighterDB.cursor()

with open("AI_Fighters.txt") as FightersFile:
	FightersData = [[1254877546986733668, Name.strip(), 50, 50, 50] for Name in FightersFile.readlines()]
	Cursor.executemany("INSERT OR IGNORE INTO Fighters (OwnerID, Name, Health, Power, Defense) VALUES (?,?,?,?,?)", FightersData)

FighterDB.commit()