const router = require("express").Router();

const Agent = require("../model/Agent")

function normalizeArchitecture(arch) {
    if (!arch) return "unknown";
    arch = arch.toLowerCase();
    if (arch.includes("amd64") || arch.includes("x64")) return "x64";
    if (arch.includes("x86")) return "x86";
    if (arch.includes("arm")) return "arm";
    return "unknown";
}

router.post("/create-agent", async (req, res) => {
    const { ipAddress, hostname, username, operatingSystem, architecture, cpu, memory, disk } = req.body;

    // Simple validation
    if (!ipAddress || !hostname || !username)
        return res.status(400).json({
            errors: true,
            message: ["ipAddress, hostname and username are required."]
        });

    try {
        const newAgent = new Agent({
            ipAddress,
            hostname,
            username,
            operatingSystem: operatingSystem || "unknown",
            architecture: normalizeArchitecture(architecture) || "unknown",
            cpu: cpu || { model: "unknown", cores: 0 },
            memory: memory || { total: 0, free: 0 },
            disk: disk || { total: 0, free: 0 },
            status: "online",
            lastActivity: new Date(),
            lastSeen: new Date(),
            lastCode: Date.now(),
            returned: "",
            commandQueue: [],
            logs: []
        });
        await newAgent.save(); // Salva no MongoDB

        res.status(201).json({
            errors: false,
            message: ["Agent registered successfully."],
            agentId: newAgent._id
        });
    } catch (error) {
        console.error("Error creating Agent:", error);
        res.status(500).json({
            errors: true,
            message: ["Failed to register Agent", error.message],
        });
    }
});

router.get("/check-agent/:pc", async (req, res) => {
    const { pc } = req.params; // parâmetro da URL

    try {
        const agent = await Agent.findOne({ hostname: pc });

        if (agent) {
            res.status(200).json({
                errors: false,
                exists: true,
                agentId: agent._id,
                hostname: agent.hostname,
                status: agent.status,
                message: ["success"]
            });
        } else {
            res.status(404).json({
                exists: false,
                errors: true,
                message: [`Agent with hostname "${pc}" not found.`]
            });
        }
    } catch (error) {
        console.error("Error checking Agent:", error);
        res.status(500).json({
            errors: true,
            message: ["Internal error while checking Agent", error.message],
        });
    }
});

router.get("/check-status/:pc", async (req, res) => {
    const { pc } = req.params;

    try {
        const agent = await Agent.findOne({ hostname: pc });

        if (!agent) {
            return res.status(404).json({
                errors: true,
                message: [`Agent with hostname "${pc}" not found.`]
            });
        }

        const lastUpdate = agent.lastActivity || agent.lastSeen;
        const currentTime = new Date();
        const diff = currentTime - new Date(lastUpdate);

        // Se o Agent não atualizou há mais de 10 dias, deletar
        if (diff >= 10 * 24 * 60 * 60 * 1000) {
            await Agent.deleteOne({ _id: agent._id });
            return res.json({ errors: false, status: "offline", message: ["Agent removed due to inactivity."] });
        }

        // Se o Agent não atualizou há mais de 1 minuto, marcar offline
        if (diff >= 1 * 60 * 1000) {
            agent.status = "offline";
            await agent.save();
            return res.json({ errors: false, status: "offline", currentTime, lastUpdate, message: ["success"] });
        }

        // Caso contrário, marcar online
        agent.status = "online";
        await agent.save();
        res.json({ errors: false, status: "online", currentTime, lastUpdate, message: ["success"] });

    } catch (error) {
        console.error("Error checking Agent status:", error);
        res.status(500).json({
            message: ["Internal error checking Agent status", error.message],
            errors: true
        });
    }
});

router.get("/connections", async (req, res) => {
    try {
        const tenDaysAgo = new Date(Date.now() - 10 * 24 * 60 * 60 * 1000);

        // Deleta Agents que não atualizam há mais de 10 dias
        await Agent.deleteMany({ lastActivity: { $lt: tenDaysAgo } });

        // Busca todos os Agents restantes
        const agents = await Agent.find({});

        res.status(200).json({
            message: ["success"],
            errors: false,
            agents
        });
    } catch (error) {
        console.error("Error fetching connections:", error);
        res.status(500).json({
            message: ["Internal error fetching Agents", error.message],
            errors: true
        });
    }
});

router.post("/:pc", async (req, res) => {
    const { pc } = req.params;
    const { command } = req.body;

    if (!command)
        return res.status(400).json({
            errors: true,
            message: ["The command cannot be empty."]
        });

    try {
        const agent = await Agent.findOne({ hostname: pc });

        if (!agent)
            return res.status(404).json({
                errors: true,
                message: [`Agent with hostname "${pc}" not found.`]
            });


        agent.commandQueue.push({
            command: command,
            payload: {},
            createdAt: new Date(),
            executed: false
        });

        agent.lastCode = Date.now();
        await agent.save();

        res.status(200).json({
            message: ["Command sent successfully."],
            errors: false
        });
    } catch (error) {
        console.error("Erro ao enviar comando:", error);
        res.status(500).json({
            message: ["Erro interno ao enviar comando.", error.message],
            errors: true
        });
    }
});

router.post("/connect/:pc", async (req, res) => {
    const { pc } = req.params;

    try {
        const agent = await Agent.findOne({ hostname: pc });

        if (!agent)
            return res.status(404).json({
                errors: true,
                message: [`Agent "${pc}" not found.`]
            });

        // Retorna os dados completos do Agent
        res.status(200).json({
            erros: false,
            message: ["success"],
            agent
        });
    } catch (error) {
        console.error("Error connecting to Agent:", error);
        res.status(500).json({
            message: ["Internal error connecting to Agent", error.message],
            errors: true
        });
    }
});

router.get("/command/:pc", async (req, res) => {
    const { pc } = req.params;

    try {
        const agent = await Agent.findOne({ hostname: pc });

        if (!agent)
            return res.status(404).json({
                errors: true,
                message: [`Agent "${pc}" not found.`]
            });


        // Pega o último comando não executado
        const pendingCommand = agent.commandQueue.find(cmd => !cmd.executed);

        if (!pendingCommand)
            return res.status(200).json({
                errors: true,
                message: ["No pending commands."]
            });


        res.status(200).json({
            errors: false,
            message: ["success"],
            command: pendingCommand.command,
            payload: pendingCommand.payload,
            createdAt: pendingCommand.createdAt
        });
    } catch (error) {
        console.error("Error getting command from Agent:", error);
        res.status(500).json({
            message: ["Internal error getting command from Agent", error.message],
            errors: true
        });
    }
});

router.post("/returned/:pc", async (req, res) => {
    const { pc } = req.params;
    const { returned } = req.body;

    if (!returned)
        return res.status(400).json({
            errors: true,
            message: ["Returned is required."]
        });

    try {
        const agent = await Agent.findOne({ hostname: pc });

        if (!agent)
            return res.status(404).json({
                errors: true,
                message: [`Agent "${pc}" not found.`]
            });

        agent.returned = returned;
        await agent.save();

        res.status(200).json({
            erros: false,
            message: ["Return updated successfully."]
        });
    } catch (error) {
        console.error("Error updating Agent return:", error);
        res.status(500).json({
            message: ["Internal error updating Agent return", error.message],
            errors: true
        });
    }
});

router.get("/returned/:pc", async (req, res) => {
    const { pc } = req.params;

    try {
        const agent = await Agent.findOne({ hostname: pc });

        if (!agent)
            return res.status(404).json({
                errors: true,
                message: [`Agent "${pc}" not found.`]
            });

        res.status(200).json({
            erros: false,
            message: ["success"],
            returned: agent.returned
        });
    } catch (error) {
        console.error("Error getting return from Agent:", error);
        res.status(500).json({
            errors: true,
            message: ["Internal error getting return from Agent", error.message]
        });
    }
});

router.post("/activity/:pc", async (req, res) => {
    const { pc } = req.params;

    try {
        const agent = await Agent.findOne({ hostname: pc });

        if (!agent)
            return res.status(404).json({
                errors: true,
                message: [`Agent "${pc}" not found.`]
            });

        agent.lastActivity = new Date();
        await agent.save();

        res.status(200).json({
            errors: false,
            message: ["Last activity updated successfully."]
        });
    } catch (error) {
        console.error("Error updating Agent activity:", error);
        res.status(500).json({
            message: ["Internal error updating Agent activity", error.message],
            errors: true
        });
    }
});

router.get("/last-code/:pc", async (req, res) => {
    const { pc } = req.params;

    try {
        const agent = await Agent.findOne({ hostname: pc });

        if (!agent)
            return res.status(404).json({
                errors: true,
                message: [`Agent "${pc}" not found.`]
            });

        res.status(200).json({ 
            errors: false,
            message: ["success"],
            code: agent.lastCode 
        });
    } catch (error) {
        console.error("Erro ao obter último código do Agent:", error);
        res.status(500).json({
            message: ["Erro interno ao obter último código do Agent", error.message],
            errors: true
        });
    }
});

module.exports = router;