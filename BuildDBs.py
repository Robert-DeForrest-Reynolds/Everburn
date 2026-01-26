from os import mkdir
from os.path import exists, join

from sqlite3 import connect

... if exists("Data") else mkdir("Data")




DesmondDB = connect(join("Data", "Desmond.db"))
DesmondCursor = DesmondDB.cursor()
DesmondCursor.execute('PRAGMA journal_mode=WAL;')
DesmondCursor.execute("PRAGMA foreign_keys=ON;")
DesmondCursor.execute("PRAGMA busy_timeout=3000;")
DesmondCursor.execute("""
CREATE TABLE IF NOT EXISTS Players (
	ID   				INTEGER PRIMARY KEY,
	Name        		TEXT NOT NULL,
	Wallet				REAL DEFAULT 500.0,
	Level				INTEGER NOT NULL DEFAULT 1,
	Experience			INTEGER NOT NULL DEFAULT 0,
	TimeOfLastClaim 	TEXT NOT NULL DEFAULT 'NEVER',
	CreatedAt   		TEXT NOT NULL DEFAULT (datetime('now'))
);
""")

DesmondCursor.execute("""
CREATE TABLE IF NOT EXISTS Reports (
	ReportID   			INTEGER PRIMARY KEY AUTOINCREMENT,
	ReporterID        	INTEGER NOT NULL,
	TargetID			INTEGER NOT NULL,
	Category 			TEXT NOT NULL,
	Statement			TEXT NOT NULL,
	Status				TEXT NOT NULL DEFAULT 'OPEN',
	CreatedAt   		TEXT NOT NULL DEFAULT (datetime('now')),
	UpdatedAt   		TEXT NOT NULL DEFAULT (datetime('now'))
);
""")

DesmondCursor.execute("""
CREATE TABLE IF NOT EXISTS ReportEvidence (
	EvidenceID  	INTEGER PRIMARY KEY AUTOINCREMENT,
	ReportID    	INTEGER NOT NULL,
	Note        	TEXT NOT NULL,
	Value       	TEXT NOT NULL,
	AddedAt     	TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

	FOREIGN KEY (ReportID)
		REFERENCES Reports(ReportID)
		ON DELETE CASCADE
)
""")

DesmondCursor.execute("""
CREATE TABLE IF NOT EXISTS ReportEvents (
	EventID     	INTEGER PRIMARY KEY AUTOINCREMENT,
	ReportID    	INTEGER NOT NULL,
	ActorUserID 	INTEGER NOT NULL,
	Type        	TEXT NOT NULL,
	Data        	TEXT NOT NULL,
	CreatedAt   	TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,

	FOREIGN KEY (ReportID)
		REFERENCES Reports(ReportID)
		ON DELETE CASCADE
)
""")

DesmondCursor.execute("""
CREATE TRIGGER IF NOT EXISTS Reports_UpdatedAt
AFTER UPDATE ON Reports
FOR EACH ROW
BEGIN
	UPDATE Reports
	SET UpdatedAt = CURRENT_TIMESTAMP
	WHERE ReportId = OLD.ReportId;
END;
""")
DesmondDB.commit()




CrucibleDB = connect(join("Data", "Crucible.db"))

CrucibleDBCursor = CrucibleDB.cursor()

CrucibleDBCursor.execute('PRAGMA journal_mode=WAL;')
CrucibleDBCursor.execute("PRAGMA busy_timeout=3000;")

CrucibleDBCursor.execute("""
CREATE TABLE IF NOT EXISTS Fighters (
	ID   INTEGER PRIMARY KEY AUTOINCREMENT,
	OwnerID     	TEXT NOT NULL,
	Name        	TEXT NOT NULL UNIQUE,
	Level       	INTEGER DEFAULT 1,
	Experience  	INTEGER DEFAULT 0,
	Health			INTEGER NOT NULL DEFAULT 50,
	Power			INTEGER NOT NULL DEFAULT 50,
	Defense			INTEGER NOT NULL DEFAULT 50,
	Wins			INTEGER NOT NULL DEFAULT 0,
	Losses			INTEGER NOT NULL DEFAULT 0,
	CreatedAt   	TEXT NOT NULL DEFAULT (datetime('now'))
);
""")

CrucibleDBCursor.execute("""
CREATE TABLE IF NOT EXISTS Challenges (
	ID   				TEXT PRIMARY KEY,
	ChallengerID    	INTEGER NOT NULL,
	ChallengeeID  		INTEGER NOT NULL,
	ChallengerFighter	TEXT NOT NULL,
	ChallengeeFighter	TEXT NOT NULL,
	Wager				REAL NOT NULL,
	CreatedAt   		TEXT NOT NULL DEFAULT (datetime('now'))
);
""")
CrucibleDB.commit()