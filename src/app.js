const express = require("express");

const statsRouter = require("./routes/stats");
const journalRouter = require("./routes/journal");
const questsRouter = require("./routes/quests");

const app = express();

app.use(express.json());

app.get("/", (req , res) => {
    res.json({
        message:"[SYSTEM]: Life OS Agent is online.",
        status:"active"
    });
});

app.use("/stats", statsRouter);
app.use("/journal", journalRouter);
app.use("/quests", questsRouter);

module.exports = app;