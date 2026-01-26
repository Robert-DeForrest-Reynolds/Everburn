from sqlite3 import Connection

class EverburnBot:
	# Self.DesmondDB: Connection

	def Get_Wallet(Self, MemberID:int) -> float:
		Cursor = Self.DesmondDB.cursor()
		try:
			Cursor.execute("SELECT Wallet FROM Players WHERE ID=?", (MemberID,))
			Row = Cursor.fetchone()
			if Row is None:
				raise ValueError(f"Player {MemberID} not found in Players table")
			return float(Row[0])
		finally:
			Cursor.close()


	def Add_To_Wallet(Self, MemberID:int, Amount:float) -> float:
		if Amount < 0:
			raise ValueError("Amount must be >= 0 for Add_To_Wallet")

		with Self.DesmondDB:  # atomic transaction
			Cursor = Self.DesmondDB.cursor()
			try:
				Cursor.execute(
					"UPDATE Players SET Wallet = Wallet + ? WHERE ID = ?",
					(float(Amount), int(MemberID)),
				)
				if Cursor.rowcount != 1:
					raise ValueError(f"Player {MemberID} not found (no row updated)")

				# Return the new wallet
				Cursor.execute("SELECT Wallet FROM Players WHERE ID=?", (int(MemberID),))
				return float(Cursor.fetchone()[0])
			finally:
				Cursor.close()


	def Subtract_From_Wallet(Self, MemberID:int, Amount:float) -> float:
		"""Subtracts only if the user has enough. Raises if insufficient."""
		if Amount < 0:
			raise ValueError("Amount must be >= 0 for Subtract_From_Wallet")

		with Self.DesmondDB:
			Cursor = Self.DesmondDB.cursor()
			try:
				Cursor.execute(
					"""
					UPDATE Players
					SET Wallet = Wallet - ?
					WHERE ID = ? AND Wallet >= ?
					""",
					(float(Amount), int(MemberID), float(Amount)),
				)

				if Cursor.rowcount != 1:
					# Could be missing player OR insufficient funds.
					# Disambiguate with one cheap select.
					Cursor.execute("SELECT Wallet FROM Players WHERE ID=?", (int(MemberID),))
					Row = Cursor.fetchone()
					if Row is None:
						raise ValueError(f"Player {MemberID} not found")
					raise ValueError(f"Insufficient funds: Wallet={float(Row[0]):.2f}, Need={float(Amount):.2f}")

				Cursor.execute("SELECT Wallet FROM Players WHERE ID=?", (int(MemberID),))
				return float(Cursor.fetchone()[0])
			finally:
				Cursor.close()


	def Apply_Wallet(Self, MemberID:int, NewAmount:float) -> float:
		"""Force-set wallet to a specific value (admin / corrections)."""
		with Self.DesmondDB:
			Cursor = Self.DesmondDB.cursor()
			try:
				Cursor.execute(
					"UPDATE Players SET Wallet = ? WHERE ID = ?",
					(float(NewAmount), int(MemberID)),
				)
				if Cursor.rowcount != 1:
					raise ValueError(f"Player {MemberID} not found")
				return float(NewAmount)
			finally:
				Cursor.close()


	def Transfer_Wallet(Self, FromMemberID:int, ToMemberID:int, Amount:float) -> tuple[float, float]:
		"""
		Atomic transfer: subtract from one (if enough), add to the other.
		Returns (FromNewWallet, ToNewWallet).
		"""
		if Amount <= 0:
			raise ValueError("Amount must be > 0 for Transfer_Wallet")

		with Self.DesmondDB:
			Cursor = Self.DesmondDB.cursor()
			try:
				# Withdraw guarded
				Cursor.execute(
					"""
					UPDATE Players
					SET Wallet = Wallet - ?
					WHERE ID = ? AND Wallet >= ?
					""",
					(float(Amount), int(FromMemberID), float(Amount)),
				)
				if Cursor.rowcount != 1:
					Cursor.execute("SELECT Wallet FROM Players WHERE ID=?", (int(FromMemberID),))
					Row = Cursor.fetchone()
					if Row is None:
						raise ValueError(f"From player {FromMemberID} not found")
					raise ValueError(f"Insufficient funds: Wallet={float(Row[0]):.2f}, Need={float(Amount):.2f}")

				# Deposit
				Cursor.execute(
					"UPDATE Players SET Wallet = Wallet + ? WHERE ID = ?",
					(float(Amount), int(ToMemberID)),
				)
				if Cursor.rowcount != 1:
					raise ValueError(f"To player {ToMemberID} not found")

				# Fetch both
				Cursor.execute("SELECT Wallet FROM Players WHERE ID=?", (int(FromMemberID),))
				FromNew = float(Cursor.fetchone()[0])
				Cursor.execute("SELECT Wallet FROM Players WHERE ID=?", (int(ToMemberID),))
				ToNew = float(Cursor.fetchone()[0])

				return (FromNew, ToNew)
			finally:
				Cursor.close()
