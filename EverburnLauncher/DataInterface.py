from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from EverburnLauncher.__main__ import Everburn


def Create_Player(E:Everburn, Data):
	E.DesmondCursor.execute("INSERT OR IGNORE INTO Players (ID, Name) VALUES (?,?)", (int(Data[0]), Data[1]))
	E.DesmondDB.commit()
	return None


def Get_Player(E:Everburn, Data):
	E.DesmondCursor.execute("SELECT * FROM Players WHERE ID=?", (int(Data[0]),))
	Row = E.DesmondCursor.fetchone()
	return ",".join([str(Item) for Item in Row])


def Update_Player():...



DataInterfaceMapping = {
	"NEW_PLAYER": Create_Player,
	"GET_PLAYER": Get_Player,
	"UPDATE_PLAYER": Update_Player,
}