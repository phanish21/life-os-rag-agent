const GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions";
const GROQ_MODEL = "openai/gpt-oss-120b";

const SYSTEM_PROMPT = `You are "The System" from a leveling-up life RPG. You observe the
    player's journal memories and issue a single quest that helps them grow in one
    specific attribute. Your tone is terse, formal, and slightly ominous - like a
    game system addressing a player, not a friendly assistant.
    
    Respond with ONLY a JSON object, no markdown fences, no extra text:
    {
    "title": "short quest title, 5-8 words",
    "description": "1-2 sentences, in System voice, referencing what it observed",
    "difficulty": "easy" | "medium" | "hard" | "epic"
}`;

function buildUserPrompt(attribute, chunks) {
    const memoryList = chunks.map((c, i) => `${i+1}. ${c.created_at} ${c.content}`).join("\n");

    return `Attribute to target: ${attribute}

    Relevant journal memories:
    ${memoryList}
    
    Generate one quest that targets the "${attribute}" attribute, grounded in
    what these memories actually show about the player's recent patterns.`
}

function fallBackQuest(attribute) {
    return {
        title: `Attend to your ${attribute}`,
        description: `[SYSTEM]: Insufficient data synthesis. Focus your next action on ${attribute}.`,
        difficulty: "medium"
    };
}

async function darftQuest(attribute, chunks) {
    const apiKey = process.env.GROQ_API_KEY;
    
    if (!apiKey) {
        console.error("[QuestGen] GROQ_API_KEY not set - using fallback quest.");
        return fallBackQuest(attribute);
    }

    try {
        const response = await fetch(GROQ_API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${apiKey}`
            },
            body: JSON.stringify({
                model: GROQ_MODEL,
                messages: [
                    { role: "system", content: SYSTEM_PROMPT },
                    { role: "user", content: buildUserPrompt(attribute, chunks) } 
                ],
                temperature: 0.7,
                max_tokens: 300
            })
        });

        if (!response.ok) {
            console.error(`[QuestGen] Groq API error: ${response.status} ${await response.text()}`);
            return fallBackQuest(attribute);
        }

        const data = await response.json();
        console.log("Inside draftQuest", data);

        const raw = data.choices?.[0]?.message?.content?.trim();

        if (!raw) {
            return fallBackQuest(attribute);
        }

        const cleaned = raw.replace(/```json|```/g, "").trim();
        const parsed = JSON.parse(cleaned);

        if (!parsed.title || !parsed.description || !parsed.difficulty) {
            console.error("[QuestGen] Malformed quest JSON from LLM:", parsed);
            return fallBackQuest(attribute);
        }

        return parsed;
    } catch (error) {
        console.error("[QuestGen] Failed to draft quest:", error.message);
        return fallBackQuest(attribute);
    }
}

module.exports = { darftQuest };