INFO = "INFO"
ERROR = "ERROR"
DATA = "DATA"

def EverLog(Message:str, Type:str=INFO):
	"""Everburn's log function. Prints to console"""
	print(f"Everburn:{Type}:{Message}", flush=True)