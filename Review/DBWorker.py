from asyncio import Queue, get_running_loop
from sqlite3 import connect


# Startup
# create_task(Self.DBWorker.Run())


# Shutdown
# await Self.DBWorker.Queue.put(None)
# Self.DBWorker.Alive = False

class DBWorker:
	def __init__(Self, DBPath:str):
		Self.DB = connect(DBPath, check_same_thread=False)
		Self.Queue:Queue = Queue()
		Self.Alive = True

	async def Run(Self):
		while Self.Alive:
			Item = await Self.Queue.get()
			if Item is None:
				return

			Sql, Params, Future = Item

			try:
				Cursor = Self.DB.cursor()
				Cursor.execute(Sql, Params)

				if Sql.lstrip().upper().startswith("SELECT"):
					Result = Cursor.fetchall()
				else:
					Self.DB.commit()
					Result = Cursor.rowcount

				Future.set_result(Result)

			except Exception as E:
				Future.set_exception(E)

			finally:
				Cursor.close()

	async def Request(Self, Sql:str, Params:tuple=()):
		Loop = get_running_loop()
		Future = Loop.create_future()
		await Self.Queue.put((Sql, Params, Future))
		return await Future