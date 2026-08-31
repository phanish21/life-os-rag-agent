const express = require("express");

const { getPlayer } = require("../game/playerService");
const { getActiveQuest, completeQuest, createQuest} = require("../services/questService")
const { calculateQuestXP } = require("../game/xpEngine");
const { selectAttributeForQUest } = require("../game/attributeSelector");
const { darftQuest } = require("../services/questGenerator");

const router = express.Router();

const RAG_SERVICE_URL = process.env.RAG_SERVICE_URL;

router.post("/generate", async ( req, res) => {
    try {
        const attribute = selectAttributeForQUest();

        const ragResponse = await fetch(`${RAG_SERVICE_URL}/search/attribute`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ attribute, final_limit: 8})
        });

        if (!ragResponse.ok) {
            return res.status(502).json({
                error: `RAG service returned ${ragResponse.status} while fetching memories for "${attribute}".`
            });
        }

        const { chunks } = await ragResponse.json();

        const draft = await darftQuest(attribute, chunks);
        const xpReward = calculateQuestXP(draft.difficulty);

        const sourceJournalIds = [...new Set(chunks.map((c) => c.journal_id))]

        const quest = createQuest({
            title: draft.title,
            description: draft.description,
            difficulty: draft.difficulty,
            xpReward,
            primaryStat: attribute,
            sourceJournalIds
        });

        res.status(201).json({
            message: "[SYSTEM]: New quest issued.",
            quest
        });

    } catch (error) {
        console.error("[Quests] Generation failed:", error);
        res.status(500).json({
            error: "Quest generation failed."
        });
    }
});

router.get("/", (req, res) => {
    const quests = getActiveQuest();

    res.json({
        count: quests.length,
        quests
    });
});

router.post("/:id/complete", (req, res) => {
    const { id } = req.params;

    try {
        const quest = completeQuest(Number(id));
        const player =  getPlayer();

        res.json({
            message: `[SYSTEM]: Quest "${quest.title}" complete. ${quest.xp_reward} XP awarded.`,
            quest,
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
    } catch (error) {
        res.status(400).json({error: error.message});
    }
});

module.exports = router;