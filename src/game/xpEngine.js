const XP_REWARDS = {
  easy: 10,
  medium: 30,
  hard: 60,
  epic: 100
};

function calculateQuestXP(difficulty) {
  if (!XP_REWARDS[difficulty]) {
    throw new Error(`Invalid difficulty: ${difficulty}`);
  }

  return XP_REWARDS[difficulty];
}

module.exports = {
  calculateQuestXP,
  XP_REWARDS
};