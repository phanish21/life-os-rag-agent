const db = require("../db/database");
const { getPlayer } = require("./playerService");
const { CORE_STATS } = require("./stats");

// TO DO:
// Tune these to shift how much "weak stat" vs "hasn't been touched in a while"
// matters when the System picks a quest attribute.
const LOW_STA_WEIGHT = 0.5
const NEGLECT_WEIGHT = 0.5

function getStatNeglect() {
    const rows = db.prepare(`
        SELECT primary_stat, MAX(created_at) as last_created
        FROM quests
        GROUP BY primary_stat`).all();

    const lastQuestByStat = {}
    for (const row of rows){
        lastQuestByStat[row.primary_stat] = new Date(row.last_created);
    }

    const now = new Date();
    const neglect = {};

    for (const stat of CORE_STATS) {
        const last = lastQuestByStat[stat]
        neglect[stat] = last ? (now - last) / (1000 * 60 * 60 * 24) : Infinity
    }

    return neglect;
}

function normalize(values) {
    const finite = values.filter(Number.isFinite);
    const maxFinite = finite.length ? Math.max(...finite) : 0;
    const sentinel = maxFinite + 1; 
    const max = Math.max(sentinel, 1);
    return values.map((v) => (Number.isFinite(v) ? v / max : sentinel / max));
}

function shuffle(array) {
    const arr = [...array];
    for (let i = arr.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [arr[i], arr[j]] = [arr[j], arr[i]];
    }
    return arr;
}

function selectAttributeForQUest() {
    const player = getPlayer();
    const neglect = getStatNeglect();

    const statValues = CORE_STATS.map((s) => player[s]);
    const maxStat = Math.max(...statValues, 1);
    const lowStatScore = statValues.map((v) => 1-v/maxStat);

    const neglectValues = CORE_STATS.map((s) => neglect[s]);
    const normalizedNeglect = normalize(neglectValues);

    const scored = CORE_STATS.map((stat, i) => ({
        stat,
        lowStatScore: lowStatScore[i],
        neglectScore: normalizedNeglect[i],
        score: LOW_STA_WEIGHT * lowStatScore[i] + NEGLECT_WEIGHT * normalizedNeglect[i]
    }));

    console.log("[AttributeSelector] scores:", scored);

    scored.sort((a, b) => b.score - a.score);
    const shuffled = shuffle(scored);
    shuffled.sort((a, b) => b.score - a.score);
    console.log("Inside selectAttributeForQUest", shuffled , shuffled[0].stat);
    return shuffled[0].stat;
}

module.exports = { selectAttributeForQUest, getStatNeglect};