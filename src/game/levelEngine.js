function calculateLevel(totalXP) {
  return Math.floor(totalXP / 100) + 1;
}

module.exports = {
  calculateLevel
};