const Database = require("better-sqlite3");

const db = new Database("life-os.db");

db.pragma("journal_mode = WAL");

db.exec(`
  CREATE TABLE IF NOT EXISTS player (
    id INTEGER PRIMARY KEY,
    total_xp INTEGER NOT NULL DEFAULT 0,
    level INTEGER NOT NULL DEFAULT 1,

    vitality INTEGER NOT NULL DEFAULT 0,
    focus INTEGER NOT NULL DEFAULT 0,
    intellect INTEGER NOT NULL DEFAULT 0,
    balance INTEGER NOT NULL DEFAULT 0,
    connection INTEGER NOT NULL DEFAULT 0,
    progress INTEGER NOT NULL DEFAULT 0
  );

  CREATE TABLE IF NOT EXISTS journal_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    content TEXT NOT NULL,
    created_at TEXT NOT NULL
  );

  CREATE TABLE IF NOT EXISTS quests (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,

    difficulty TEXT NOT NULL,
    xp_reward INTEGER NOT NULL,

    primary_stat TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',

    created_at TEXT NOT NULL,
    completed_at TEXT
  );

  CREATE TABLE IF NOT EXISTS quest_sources (
    quest_id INTEGER NOT NULL,
    journal_entry_id INTEGER NOT NULL,

    FOREIGN KEY (quest_id) REFERENCES quests(id),
    FOREIGN KEY (journal_entry_id) REFERENCES journal_entries(id)
  );
`);

const existingPlayer = db
  .prepare("SELECT id FROM player WHERE id = 1")
  .get();

if (!existingPlayer) {
  db.prepare(`
    INSERT INTO player (id)
    VALUES (1)
  `).run();
}

module.exports = db;