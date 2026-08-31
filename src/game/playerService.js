const db = require("../db/database");
const { calculateLevel } = require("./levelEngine");
const { CORE_STATS } = require("./stats");

function getPlayer() {
  return db
    .prepare("SELECT * FROM player WHERE id = 1")
    .get();
}

function addXP(amount) {
  const player = getPlayer();

  const totalXP = player.total_xp + amount;
  const level = calculateLevel(totalXP);

  db.prepare(`
    UPDATE player
    SET total_xp = ?, level = ?
    WHERE id = 1
  `).run(totalXP, level);

  return getPlayer();
}

function addStatProgress(stat, amount) {
  if (!CORE_STATS.includes(stat)) {
    throw new Error(`Invalid stat: ${stat}`);
  }

  db.prepare(`
    UPDATE player
    SET ${stat} = ${stat} + ?
    WHERE id = 1
  `).run(amount);

  return getPlayer();
}

module.exports = {
  getPlayer,
  addXP,
  addStatProgress
};