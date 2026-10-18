CREATE TABLE IF NOT EXISTS messages (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	dtime TEXT(32) NOT NULL,
	tstamp INTEGER NOT NULL,
	message TEXT(2000) NOT NULL,
	lvl TEXT(16) DEFAULT ('info') NOT NULL
);

CREATE TABLE IF NOT EXISTS trends (
	id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	dtime TEXT(32) NOT NULL,
	tstamp REAL NOT NULL,
	channel_name TEXT(128) NOT NULL,
	value REAL
);

DROP INDEX IF EXISTS idx_trends_channel_name;

CREATE INDEX IF NOT EXISTS idx_trends_channel_tstamp ON trends (channel_name, tstamp);
