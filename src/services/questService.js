const db = require("../db/database");
const {addXP, addStatProgress} = require("../game/playerService");

function createQuest({title, description, difficulty, xpReward, primaryStat, sourceJournalIds = []}) {
    const createdAt = new Date().toISOString();
    const result = db.prepare(`
        INSERT INTO quests (title, description, difficulty, xp_reward, primary_stat, status, created_at)
        VALUES (?, ?, ?, ?, ?, 'active', ?)`).run(title, description, difficulty, xpReward, primaryStat, createdAt)

    const questId = result.lastInsertRowid;

    const insertSource = db.prepare(`
        INSERT INTO quest_sources (quest_id, journal_entry_id)
        VALUES (?,?)`);

    for (const journalId of sourceJournalIds) {
        insertSource.run(questId, journalId);
    }

    return getQuestById(questId);
}

function getQuestById(id) {
    return db.prepare("SELECT * FROM quests WHERE id =?").get(id);
}

function getActiveQuest() {
    return db.prepare("SELECT * FROM quests WHERE status = 'active' ORDER BY created_at DESC").all();
}

function completeQuest(id){
    const quest = getQuestById(id);

    if (!quest) {
        throw new Error(`Quest not Found: ${id}`);
    }

    if (quest.status != "active") {
        throw new Error(`Quest ${id} is not active (status: ${quest.status})`);
    }

    const completedAt = new Date().toISOString();

    db.prepare(`UPDATE quests SET status = 'completed', completed_at = ? WHERE id = ?`).run(completedAt, id);

    addXP(quest.xp_reward);
    addStatProgress(quest.primary_stat, quest.xp_reward);

    return getQuestById(id);
}

module.exports = {
    createQuest, getQuestById, getActiveQuest, completeQuest
} 