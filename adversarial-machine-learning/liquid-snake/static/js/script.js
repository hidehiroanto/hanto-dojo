var modelSocket;

function addInteractionCard(interaction) {
    const card = document.createElement("div");
    card.className = "card";

    const tabs = document.createElement("ul");
    tabs.className = "tabs";
    card.appendChild(tabs);

    const contentContainer = document.createElement("div");
    card.appendChild(contentContainer);

    const icons = {
        "message": "fa-comment",
        "thoughts": "fa-brain",
        "terminal": "fa-terminal",
        "file": "fa-file",
        "unknown": "fa-question-circle"
    }

    Object.entries(interaction.content).forEach(([contentType, content], index) => {
        const icon = icons[contentType] || icons.unknown;
        const tab = document.createElement("li");
        const link = document.createElement("a");
        link.className = "tablink" + (index === 0 ? " active" : "");
        link.title = contentType;
        link.innerHTML = `<i class="fas ${icon}"></i>`;
        link.onclick = (event) => openTab(event, contentType);
        tab.appendChild(link);
        tabs.appendChild(tab);

        const contentDiv = document.createElement("div");
        contentDiv.id = contentType;
        contentDiv.className = "tabcontent";
        contentDiv.hidden = index !== 0;
        if (["message", "thoughts"].includes(contentType)) {
            contentDiv.innerHTML = DOMPurify.sanitize(marked.parse(content));
        } else {
            const pre = document.createElement("pre");
            const code = document.createElement("code");
            code.textContent = content;
            pre.appendChild(code);
            contentDiv.appendChild(pre);
        }
        contentContainer.appendChild(contentDiv);
    });

    if (interaction.type === "assistant") {
        const ratings = document.createElement("ul");
        ratings.className = "tabs secondary";
        card.appendChild(ratings);

        [+1, -1].forEach(value => {
            const icon = value === +1 ? "fa-thumbs-up" : "fa-thumbs-down";
            const tab = document.createElement("li");
            const link = document.createElement("a");
            link.className = "tablink";
            link.innerHTML = `<i class="fas ${icon}"></i>`;
            link.onclick = (event) => {
                const index = Array.from(card.parentElement.children).indexOf(card);
                const rating = link.classList.contains("active") ? 0 : value;
                link.classList.toggle("active");
                ratings.querySelectorAll(".tablink").forEach(otherLink => { if (otherLink !== link) otherLink.classList.remove("active"); });
                modelSocket.emit("rate_interaction", {index: index, rating: rating});
            }
            tab.appendChild(link);
            ratings.appendChild(tab);
        });
    }

    document.querySelector(".background").hidden = true;

    document.querySelector(".card-container").appendChild(card);
    window.scrollTo({
        top: document.body.scrollHeight,
        behavior: "smooth",
    });
}

function setLoadingState(isLoading) {
    const status = document.querySelector("#status");
    status.innerHTML = "";

    if (isLoading) {
        for (let delay = 0; delay <= 0.9; delay += 0.1) {
            let dot = document.createElement("div");
            dot.className = "dot";
            dot.style.setProperty("--delay", `${delay}s`);
            status.appendChild(dot);
        }
        status.hidden = false;
    } else {
        status.hidden = true;
    }
}

function openTab(event, tabName) {
    const card = event.currentTarget.closest(".card");
    const tabs = event.currentTarget.closest(".tabs");

    const tabcontent = Array.from(card.getElementsByClassName("tabcontent"));
    tabcontent.forEach(tab => tab.hidden = true);

    const tablinks = Array.from(tabs.getElementsByClassName("tablink"));
    tablinks.forEach(tablink => tablink.classList.remove("active"));

    card.querySelector(`#${tabName}`).hidden = false;
    event.currentTarget.classList.add("active");
}

function rateLimit(rateLimits) {
    const formatDuration = (duration) => {
        let days = Math.floor(duration / 86400);
        duration %= 86400;
        let hours = Math.floor(duration / 3600);
        duration %= 3600;
        let minutes = Math.floor(duration / 60);
        let seconds = Math.floor(duration % 60);

        let parts = [];
        if (days > 0) parts.push(`${days} day${days === 1 ? "" : "s"}`);
        if (hours > 0) parts.push(`${hours} hour${hours === 1 ? "" : "s"}`);
        if (minutes > 0) parts.push(`${minutes} minute${minutes === 1 ? "" : "s"}`);
        if (seconds >= 0) parts.push(`${seconds} second${seconds === 1 ? "" : "s"}`);
        return parts.join(", ");
    };

    let maxRemainingRate = rateLimits.reduce((max, rate) => (max.remaining < rate.remaining) ? rate : max, {remaining: -Infinity});
    let endTime = Date.now() + maxRemainingRate.remaining * 1000;

    const promptStatus = document.querySelector("#prompt-status");
    const promptTextArea = document.querySelector("#prompt-message > textarea");

    promptStatus.innerHTML = `You must wait for <b>${formatDuration(maxRemainingRate.remaining)}</b> before you can continue.`;
    promptTextArea.hidden = true;
    promptStatus.hidden = false;

    let interval = setInterval(() => {
        let now = Date.now();
        if (now >= endTime) {
            clearInterval(interval);
            promptStatus.hidden = true;
            promptStatus.innerHTML = "";
            let cards = document.querySelectorAll(".card-container > .card");
            let lastCard = cards[cards.length - 1];
            promptTextArea.value = lastCard.querySelector("#message").textContent.trimEnd();
            lastCard.remove();
            promptTextArea.hidden = false;
            promptTextArea.readOnly = false;
        } else {
            let remaining = Math.floor((endTime - now) / 1000);
            promptStatus.innerHTML = `You must wait for <b>${formatDuration(remaining)}</b> before you can continue.`;
        }
    }, 1000);
}

document.addEventListener("DOMContentLoaded", () => {
    const url = new URL(document.URL);
    const sessionId = url.searchParams.get("session_id") || "";
    modelSocket = io(url.origin, {
        path: `${url.pathname}socket.io`,
        transports: ["websocket"],
        query: {session_id: sessionId},
        timeout: 60000
    });
    const promptStatus = document.querySelector("#prompt-status");
    const promptMessage = document.querySelector("#prompt-message");
    const promptTerminal = document.querySelector("#prompt-terminal");
    const promptFile = document.querySelector("#prompt-file");
    const promptTextArea = promptMessage.querySelector("#prompt-message > textarea");
    const toggleTerminalContext = document.querySelector("#terminal-btn");
    const toggleFileContext = document.querySelector("#file-btn");
    const betaNotify = document.querySelector("#beta-notify");
    const betaOptOut = document.querySelector("#beta-opt-out");

    modelSocket.on("running_experiment", () => {
        if (betaNotify) {
            betaNotify.hidden = false;
        }
    });

    modelSocket.on("connect_error", error => {
        promptStatus.innerHTML = error.message;
        promptTextArea.hidden = true;
        promptStatus.hidden = false;
    });

    modelSocket.on("user_rate_limit", rate_limits => {
        rateLimit(rate_limits);
        setLoadingState(false);
    });

    modelSocket.on("all_rate_limit", rate_limits => {
        rateLimit(rate_limits);
        setLoadingState(false);
    });

    modelSocket.on("session_end", reason => {
        promptStatus.innerHTML = reason.message;
        promptTextArea.hidden = true;
        promptStatus.hidden = false;
        setLoadingState(false);
    });

    modelSocket.on("new_interaction", interaction => {
        addInteractionCard(interaction);
        promptTextArea.readOnly = false;
        setLoadingState(false);
    });

    let localRender = false;
    modelSocket.on("update_terminal", data => {
        if (localRender) return;
        promptTerminal.querySelector("code").textContent = data.display;
    });

    const terminals = {};
    modelSocket.on("stream_terminal", streamData => {
        localRender = true;
        const { tty_id, stream: { data, rows, cols } } = streamData;
        if (!terminals[tty_id]) {
            terminals[tty_id] = new Terminal({
                cols: cols,
                rows: rows,
                convertEol: true,
                allowProposedApi: true,
                logLevel: "off",
            });
        }
        const terminal = terminals[tty_id];
        if (terminal.cols !== cols || terminal.rows !== rows) {
            terminal.resize(cols, rows);
        }
        terminal.write(data, () => {
            const activeBuffer = terminal.buffer.active;
            const terminalText = Array.from({ length: activeBuffer.length }, (_, i) => {
                const line = activeBuffer.getLine(i);
                return line ? line.translateToString(true)?.trimEnd() : "";
            }).filter(Boolean).join("\n");
            promptTerminal.querySelector("code").textContent = terminalText;
        });
    });

    modelSocket.on("update_file", data => {
        promptFile.querySelector("code").textContent = data.data;
    });

    promptTextArea.addEventListener("input", event => {
        promptTextArea.style.height = "1.5em";
        const lines = Math.min(promptTextArea.scrollHeight / parseInt(window.getComputedStyle(promptTextArea).lineHeight), 8);
        promptTextArea.style.height = `${lines * 1.5}em`;
    });

    toggleTerminalContext.addEventListener("click", function () {
        const isActive = this.getAttribute("data-active") === "true";
        this.setAttribute("data-active", !isActive);
    });

    toggleFileContext.addEventListener("click", function () {
        const isActive = this.getAttribute("data-active") === "true";
        this.setAttribute("data-active", !isActive);
    });

    betaOptOut.addEventListener('click', (e) => {
        e.preventDefault();
        if (confirm('Are you sure you want to opt-out of this beta? Doing so will reset your current session.')) {
            modelSocket.emit('beta_opt_out');
            setTimeout(() => {
                window.location.reload();
            }, 100);
        }
    });

    promptTextArea.addEventListener("keydown", (event) => {
        const { key, shiftKey } = event;
        if (key === "Enter" && !shiftKey) {
            event.preventDefault();

            if (promptTextArea.readOnly) return;

            const message = promptTextArea.value;
            if (!message) return;

            let terminal = promptTerminal.querySelector("code").textContent;
            let file = promptFile.querySelector("code").textContent;

            if (toggleTerminalContext.getAttribute("data-active") === "false") {
                terminal = "...";
            }
            if (toggleFileContext.getAttribute("data-active") === "false") {
                file = "...";
            }

            const content = {message: message, terminal: terminal, file: file};
            const interaction = {type: "learner", content: content};
            addInteractionCard(interaction);

            promptTextArea.readOnly = true;
            promptTextArea.value = "";
            promptTextArea.style.height = "1.5em";

            modelSocket.emit("new_interaction", interaction);
            setLoadingState(true);
        }
    });
});
