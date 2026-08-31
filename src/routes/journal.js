const express = require("express");

const { createJournalEntry, getJournalEntries } = require("../services/journalService");

const router = express.Router();
const RAG_SERVICE_URL = process.env.RAG_SERVICE_URL;

router.post("/", async (req , res) => {
    const { content } = req.body;

    if (!content || typeof content != "string") {
        return res.status(400).json({
            error: "Journal content is required."
        });
    }

    const entry = createJournalEntry(content.trim());

    try {
        const response = await fetch(`${RAG_SERVICE_URL}/index`,{
            method: "POST",
            headers:{"Content-Type": "application/json"},
            body: JSON.stringify({
                journal_id: entry.id,
                content: entry.content,
                created_at:entry.created_at
            })
        });

        if (!response.ok){
            console.error(`[RAG] Indexing failed for journal_id=${entry.id}: ${response.status} ${await response.text()}`)
        }
    } catch (error) {
        console.error(`[RAG] Could not reach RAG service for journal_id=${entry.id}:`, error.message)
    }

    res.status(200).json({
        message: "[SYSTEM]: Memory successfully recorded.",
        entry
    })
});

router.get("/", (req, res) => {
    const entries = getJournalEntries();

    res.json({
        count: entries.length,
        entries
    });
});

module.exports = router;