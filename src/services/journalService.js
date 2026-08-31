const db = require("../db/database");

function createJournalEntry(content){
    const createdAt = new Date().toISOString();

    const result = db.prepare(`Insert INTO journal_entries (content, created_at)
        VALUES (?, ?)`).run(content, createdAt);

    return db.prepare("SELECT * FROM journal_entries WHERE id = ?").get(result.lastInsertRowid);
}

function getJournalEntries() {
    return db.prepare(`SELECT * FROM journal_entries ORDER BY created_at DESC`).all();
}

function getJournalEntriesById(id) {
    return db.prepare(`SELECT * FROM journal_entries WHERE id = ?`).get(id);
}

module.exports = {
    createJournalEntry, getJournalEntries, getJournalEntriesById
}