const express = require("express");
const { getPlayer } = require("../game/playerService");

const router = express.Router();

router.get("/", (req, res) => {
  const player = getPlayer();

  res.json({
    message: "[SYSTEM]: Player status retrieved.",
    player: {
      level: player.level,
      totalXP: player.total_xp,

      attributes: {
        vitality: player.vitality,
        focus: player.focus,
        intellect: player.intellect,
        balance: player.balance,
        connection: player.connection,
        progress: player.progress
      }
    }
  });
});

module.exports = router;