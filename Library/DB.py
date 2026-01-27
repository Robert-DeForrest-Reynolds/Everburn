from __future__ import annotations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
	from Bots.Crucible import Crucible as C


from asyncio import Queue, get_running_loop, Future, create_task
from sqlite3 import connect


class DB:
	def __init__(Self, DBPath:str, Crucible:C):
		Self.Crucible = Crucible
		Self.DB = connect(DBPath, check_same_thread=False)
		Self.Queue:Queue = Queue()
		Self.Alive = True
		create_task(Self.Run())


	async def Run(Self):
		while Self.Alive:
			Item = await Self.Queue.get()
			if Item is None:
				return

			Statement:str
			Values:tuple
			F:Future
			Statement, Values, F = Item

			try:
				Cursor = Self.DB.cursor()
				Cursor.execute(Statement, Values)

				if Statement.lstrip().upper().startswith("SELECT"):
					Result = Cursor.fetchall()
					Self.Crucible.EverburnBot.Send(f"DB Result: {Result}")
				else:
					Self.DB.commit()
					Result = Cursor.rowcount

				F.set_result(Result)

			except Exception as E:
				F.set_exception(E)
				Self.Crucible.EverburnBot.Send(E)
			finally:
				Cursor.close()


	async def Request(Self, Statement:str, Values:tuple=()):
		Loop = get_running_loop()
		F:Future = Loop.create_future()
		await Self.Queue.put((Statement, Values, F))
		return await F