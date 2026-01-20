INFO = "INFO"
ERROR = "ERROR"
GET = "GET"
SET = "SET"

def EverLog(Message:str, Type:str=INFO):
	"""Everburn's log function. Prints to console"""
	print(f"Everburn:{Type}:{Message}", flush=True)