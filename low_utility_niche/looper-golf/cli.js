#!/usr/bin/env node
import fs from 'node:fs/promises';
import path from 'node:path';
import process from 'node:process';
// ─── Arg parsing ─────────────────────────────────────────────────────────────
function parseArgs(argv) {
    const args = argv.slice(2);
    let command;
    let i = 0;
    if (args[0] && !args[0].startsWith('--')) {
        command = args[0];
        i = 1;
    }
    const options = {};
    for (; i < args.length; i += 1) {
        const entry = args[i];
        if (!entry.startsWith('--'))
            continue;
        const [rawKey, inlineValue] = entry.slice(2).split('=');
        if (inlineValue !== undefined) {
            options[rawKey] = inlineValue;
            continue;
        }
        const next = args[i + 1];
        if (next && !next.startsWith('--')) {
            options[rawKey] = next;
            i += 1;
        }
        else {
            options[rawKey] = true;
        }
    }
    return { command, options };
}
function getOption(options, key, fallback) {
    const value = options[key];
    if (value === undefined)
        return fallback;
    if (value === true)
        return 'true';
    return value;
}
function getNumberOption(options, key, fallback) {
    const value = getOption(options, key);
    if (!value)
        return fallback;
    const parsed = Number(value);
    return Number.isNaN(parsed) ? fallback : parsed;
}
// ─── Agent state persistence ─────────────────────────────────────────────────
function resolveStatePath(options) {
    const provided = getOption(options, 'statePath');
    if (provided)
        return provided;
    const envPath = process.env.OPENCLAW_GOLF_STATE_PATH;
    if (envPath)
        return envPath;
    const baseDir = process.env.OPENCLAW_GOLF_BASE_DIR || process.cwd();
    return path.join(baseDir, 'agent.json');
}
async function readAgentState(statePath) {
    try {
        const raw = await fs.readFile(statePath, 'utf-8');
        const parsed = JSON.parse(raw);
        if (!parsed.agentId || !parsed.apiKey)
            return null;
        return parsed;
    }
    catch {
        return null;
    }
}
async function writeAgentState(statePath, state) {
    await fs.mkdir(path.dirname(statePath), { recursive: true });
    await fs.writeFile(statePath, `${JSON.stringify(state, null, 2)}\n`, 'utf-8');
}
// ─── HTTP helpers ────────────────────────────────────────────────────────────
async function requestJson(url, init) {
    const res = await fetch(url, init);
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
        const message = (data && typeof data === 'object' && 'error' in data)
            ? String(data.error)
            : `Request failed (${res.status})`;
        const error = new Error(message);
        error.status = res.status;
        error.data = data;
        throw error;
    }
    return data;
}
// ─── API Client ──────────────────────────────────────────────────────────────
class GolfApiClient {
    serverUrl;
    agentId;
    apiKey;
    token = null;
    expiresAt = null;
    constructor(serverUrl, agentId, apiKey) {
        this.serverUrl = serverUrl;
        this.agentId = agentId;
        this.apiKey = apiKey;
    }
    async getToken() {
        if (this.token && this.expiresAt) {
            const secondsRemaining = this.expiresAt - Math.floor(Date.now() / 1000);
            if (secondsRemaining > 30) {
                return this.token;
            }
        }
        const data = await requestJson(`${this.serverUrl}/api/auth/agent-token`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ agentId: this.agentId, apiKey: this.apiKey }),
        });
        this.token = data.token;
        this.expiresAt = data.expiresAt;
        return data.token;
    }
    async authorizedFetch(url, init) {
        const token = await this.getToken();
        const headers = new Headers(init?.headers);
        headers.set('Authorization', `Bearer ${token}`);
        return requestJson(url, { ...init, headers });
    }
    async listCourses() {
        return this.authorizedFetch(`${this.serverUrl}/api/courses`);
    }
    async startRound(courseId, teeColor, yardsPerCell) {
        return this.authorizedFetch(`${this.serverUrl}/api/course/${courseId}/rounds`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ agentId: this.agentId, teeColor, ...(yardsPerCell ? { yardsPerCell } : {}) }),
        });
    }
    async resumeRound(courseId, roundId) {
        return this.authorizedFetch(`${this.serverUrl}/api/course/${courseId}/rounds/${roundId}/resume`, { method: 'POST' });
    }
    async getHoleInfo(courseId, roundId, yardsPerCell, mapFormat) {
        const params = new URLSearchParams();
        if (yardsPerCell)
            params.set('yardsPerCell', String(yardsPerCell));
        if (mapFormat)
            params.set('mapFormat', mapFormat);
        const qs = params.toString();
        const url = `${this.serverUrl}/api/course/${courseId}/rounds/${roundId}/hole-info${qs ? `?${qs}` : ''}`;
        return this.authorizedFetch(url);
    }
    async submitShot(courseId, roundId, decision) {
        return this.authorizedFetch(`${this.serverUrl}/api/course/${courseId}/rounds/${roundId}/shot`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                club: decision.club,
                aimDirection: decision.aimDirection,
                power: decision.power,
            }),
        });
    }
    async getHoleImage(courseId, roundId) {
        return this.authorizedFetch(`${this.serverUrl}/api/course/${courseId}/rounds/${roundId}/hole-image`);
    }
}
async function registerAgent(serverUrl, registrationKey, name) {
    return requestJson(`${serverUrl}/api/agents/register`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'x-registration-key': registrationKey,
        },
        body: JSON.stringify({ registrationKey, ...(name ? { name } : {}) }),
    });
}
// ─── Display helpers ─────────────────────────────────────────────────────────
function normalizeClubName(name) {
    const trimmed = name.trim().toLowerCase();
    if (!trimmed)
        return '';
    if (trimmed === 'pw' || trimmed === 'sw')
        return trimmed;
    if (trimmed === 'putter' || trimmed === 'driver')
        return trimmed;
    if (trimmed.endsWith('-wood') || trimmed.endsWith('-iron'))
        return trimmed;
    return trimmed.replace(/\s+/g, '-');
}
function printHoleContext(holeInfo) {
    console.log('');
    // ASCII map first -- this is what the golfer "sees"
    if (holeInfo.asciiMap) {
        console.log(holeInfo.asciiMap);
        if (holeInfo.asciiLegend) {
            console.log(holeInfo.asciiLegend);
        }
        console.log('');
    }
    // Situation summary
    const parts = [];
    if (holeInfo.holeNumber != null)
        parts.push(`Hole ${holeInfo.holeNumber}`);
    if (holeInfo.par != null)
        parts.push(`Par ${holeInfo.par}`);
    if (holeInfo.strokeNumber != null)
        parts.push(`Stroke ${holeInfo.strokeNumber}`);
    if (holeInfo.ballLie)
        parts.push(`Lie: ${holeInfo.ballLie}`);
    if (holeInfo.distanceToHole != null)
        parts.push(`${holeInfo.distanceToHole.toFixed(0)}y to flag`);
    // directionToHole is only shown if the server includes it (controlled by config)
    if (holeInfo.directionToHole != null)
        parts.push(`Bearing: ${holeInfo.directionToHole.toFixed(0)} deg`);
    console.log(parts.join(' | '));
    console.log('');
    // Hazards (from ASCII analysis, if present)
    if (holeInfo.asciiAnalysis?.hazards?.length) {
        console.log('Hazards:');
        for (const hazard of holeInfo.asciiAnalysis.hazards) {
            console.log(`  ${hazard.type}: ${hazard.location}`);
        }
        console.log('');
    }
    // Stock yardages -- the golfer's bag (dynamic from agent profile)
    if (holeInfo.stockYardages?.length) {
        console.log('Your bag (stock yardages at full power):');
        for (const club of holeInfo.stockYardages) {
            console.log(`  ${club.name.padEnd(8)} ${String(club.carry).padStart(3)}y carry / ${String(club.total).padStart(3)}y total`);
        }
        console.log('');
    }
}
function printShotResult(result) {
    console.log('');
    console.log(`Result: carry ${result.carry.toFixed(1)}y, roll ${result.roll.toFixed(1)}y, total ${result.totalDistance.toFixed(1)}y`);
    console.log(`Landing: ${result.landingTerrain}, final lie: ${result.finalLie}`);
    if (result.penalties > 0) {
        console.log(`Penalties: +${result.penalties}`);
    }
    if (result.holed) {
        console.log('HOLED!');
    }
    console.log('');
}
function printScorecard(round) {
    const holeNumbers = Object.keys(round.parForHoles).map(Number).sort((a, b) => a - b);
    const totalPar = holeNumbers.reduce((sum, h) => sum + (round.parForHoles[h] ?? 0), 0);
    const totalStrokes = holeNumbers.reduce((sum, h) => sum + (round.holeScores[h] ?? 0), 0);
    const diff = totalStrokes - totalPar;
    const scoreName = (strokes, par) => {
        const d = strokes - par;
        if (d <= -3)
            return 'Albatross';
        if (d === -2)
            return 'Eagle';
        if (d === -1)
            return 'Birdie';
        if (d === 0)
            return 'Par';
        if (d === 1)
            return 'Bogey';
        if (d === 2)
            return 'Dbl Bogey';
        return `+${d}`;
    };
    console.log('');
    console.log('Scorecard');
    console.log('─'.repeat(40));
    for (const h of holeNumbers) {
        const par = round.parForHoles[h] ?? 0;
        const strokes = round.holeScores[h];
        if (strokes != null) {
            console.log(`  Hole ${String(h).padStart(2)}: ${strokes} (Par ${par}) ${scoreName(strokes, par)}`);
        }
        else {
            console.log(`  Hole ${String(h).padStart(2)}: --  (Par ${par})`);
        }
    }
    console.log('─'.repeat(40));
    if (round.status === 'completed') {
        console.log(`  Total: ${totalStrokes} (Par ${totalPar}) ${diff === 0 ? 'E' : diff > 0 ? `+${diff}` : diff}`);
    }
    else {
        const completedStrokes = holeNumbers
            .filter(h => round.holeScores[h] != null)
            .reduce((sum, h) => sum + (round.holeScores[h] ?? 0), 0);
        const completedPar = holeNumbers
            .filter(h => round.holeScores[h] != null)
            .reduce((sum, h) => sum + (round.parForHoles[h] ?? 0), 0);
        const d = completedStrokes - completedPar;
        console.log(`  Thru ${Object.keys(round.holeScores).length}: ${completedStrokes} (Par ${completedPar}) ${d === 0 ? 'E' : d > 0 ? `+${d}` : d}`);
        console.log(`  Current: Hole ${round.currentHoleNumber}`);
    }
    console.log('');
}
// ─── Subcommands ─────────────────────────────────────────────────────────────
async function cmdCourses(api) {
    const result = await api.listCourses();
    const playable = result.courses.filter(c => (c.holeCount ?? 0) > 0);
    if (!playable.length) {
        console.log('No courses with holes are currently available.');
        return;
    }
    console.log('Available courses:');
    console.log('');
    for (const c of playable) {
        console.log(`  ${c.name}`);
        console.log(`    ID: ${c.id}`);
        console.log(`    Holes: ${c.holeCount ?? '?'} | Par: ${c.totalPar ?? '?'} | Yards: ${c.totalYards ?? '?'} | Rating: ${c.rating ?? 'unrated'}`);
        console.log('');
    }
    console.log(`Use: start --courseId <id> to begin a round.`);
}
async function cmdStart(api, agentState, statePath, options) {
    const teeColor = getOption(options, 'teeColor') || agentState.teeColor || 'white';
    let courseId = getOption(options, 'courseId') || agentState.courseId || '';
    let courseName = agentState.courseName || '';
    if (!courseId) {
        throw new Error('No course specified. Run the "courses" command to list available courses, then use: start --courseId <id>');
    }
    let round;
    try {
        const roundStart = await api.startRound(courseId, teeColor, agentState.yardsPerCell);
        round = roundStart.round;
        console.log(`Round started on ${courseName || courseId}. Hole ${round.currentHoleNumber}, Par ${round.parForHoles[round.currentHoleNumber] ?? '?'}.`);
    }
    catch (error) {
        const err = error;
        if (err.status === 409 && err.data && typeof err.data === 'object' && 'roundId' in err.data) {
            const roundId = String(err.data.roundId || '');
            if (!roundId)
                throw err;
            console.log(`Resuming existing round ${roundId}...`);
            const resumed = await api.resumeRound(courseId, roundId);
            round = resumed.round;
            console.log(`Resumed on ${courseName || courseId}. Hole ${round.currentHoleNumber}, Stroke ${round.strokeCount + 1}.`);
        }
        else {
            throw err;
        }
    }
    // Persist round/course IDs and tee preference
    agentState.roundId = round.id;
    agentState.courseId = courseId;
    agentState.courseName = courseName;
    agentState.teeColor = teeColor;
    await writeAgentState(statePath, agentState);
}
async function cmdLook(api, agentState) {
    if (!agentState.courseId || !agentState.roundId) {
        throw new Error('No active round. Run `start` first.');
    }
    const mapFormat = agentState.mapFormat || 'grid';
    const holeInfo = await api.getHoleInfo(agentState.courseId, agentState.roundId, agentState.yardsPerCell, mapFormat);
    printHoleContext(holeInfo);
}
async function cmdHit(api, agentState, statePath, options) {
    if (!agentState.courseId || !agentState.roundId) {
        throw new Error('No active round. Run `start` first.');
    }
    const clubRaw = getOption(options, 'club');
    const aimRaw = getOption(options, 'aim');
    const powerRaw = getOption(options, 'power');
    if (!clubRaw)
        throw new Error('Missing --club. Example: --club driver');
    if (!aimRaw)
        throw new Error('Missing --aim (degrees 0-360). Example: --aim 355');
    if (!powerRaw)
        throw new Error('Missing --power (1-100). Example: --power 90');
    const club = normalizeClubName(clubRaw);
    const aimDirection = Number(aimRaw);
    let power = Number(powerRaw.toString().replace('%', ''));
    if (Number.isNaN(aimDirection) || aimDirection < 0 || aimDirection > 360) {
        throw new Error('--aim must be a number between 0 and 360');
    }
    if (Number.isNaN(power)) {
        throw new Error('--power must be a number');
    }
    // Accept power as 1-100 and convert to 0-1
    if (power > 1)
        power = power / 100;
    if (power < 0 || power > 1) {
        throw new Error('--power must be between 0 and 100 (or 0.0 and 1.0)');
    }
    console.log(`Shot: ${club} @ ${aimDirection} deg, power ${(power * 100).toFixed(0)}%`);
    const result = await api.submitShot(agentState.courseId, agentState.roundId, {
        club,
        aimDirection: aimDirection === 360 ? 0 : aimDirection,
        power,
    });
    printShotResult(result.shotResult);
    if (result.holeCompleted) {
        const holeNum = result.round.currentHoleNumber;
        console.log('Hole complete.');
    }
    if (result.roundCompleted) {
        console.log('Round complete!');
        printScorecard(result.round);
        // Clear round from state
        agentState.roundId = undefined;
        agentState.courseId = undefined;
        agentState.courseName = undefined;
        await writeAgentState(statePath, agentState);
    }
}
async function cmdView(api, agentState) {
    if (!agentState.courseId || !agentState.roundId) {
        throw new Error('No active round. Run `start` first.');
    }
    try {
        const { imageUrl } = await api.getHoleImage(agentState.courseId, agentState.roundId);
        console.log(imageUrl);
    }
    catch (error) {
        const message = error instanceof Error ? error.message : 'Failed to generate hole image';
        if (message.includes('Cloudinary')) {
            console.error('Hole image generation requires Cloudinary to be configured on the server.');
        }
        throw error;
    }
}
async function cmdScorecard(api, agentState) {
    if (!agentState.courseId || !agentState.roundId) {
        throw new Error('No active round. Run `start` first.');
    }
    // We need round state — get it by fetching hole info (which includes round context)
    // or we can just read the state from a resume call. For now, use the simpler approach
    // of calling resume which returns the round state.
    const { round } = await api.resumeRound(agentState.courseId, agentState.roundId);
    printScorecard(round);
}
// ─── Bearing calculator (local math, no API) ─────────────────────────────
function cmdBearing(options) {
    const aheadRaw = getOption(options, 'ahead');
    const rightRaw = getOption(options, 'right');
    if (aheadRaw === undefined && rightRaw === undefined) {
        throw new Error('Usage: bearing --ahead <yards> --right <yards>\n' +
            '  Positive ahead = toward the green. Negative = behind you.\n' +
            '  Positive right = right of you. Negative = left of you.\n' +
            '  Read these values from the map rulers.');
    }
    const ahead = Number(aheadRaw ?? 0);
    const right = Number(rightRaw ?? 0);
    if (Number.isNaN(ahead))
        throw new Error('--ahead must be a number (yards toward the green, negative = behind)');
    if (Number.isNaN(right))
        throw new Error('--right must be a number (yards right of ball, negative = left)');
    if (ahead === 0 && right === 0) {
        console.log('Target is at your ball position — no bearing to calculate.');
        return;
    }
    const radians = Math.atan2(right, ahead);
    const degrees = ((radians * 180) / Math.PI + 360) % 360;
    const distance = Math.sqrt(ahead * ahead + right * right);
    console.log(`Bearing: ${Math.round(degrees)} deg | Distance: ${Math.round(distance)} yards`);
}
// ─── Main ────────────────────────────────────────────────────────────────────
async function main() {
    const { command, options } = parseArgs(process.argv);
    if (!command || command === 'help' || command === '--help') {
        console.log('OpenClaw Golf CLI — You are the golfer. Your caddy is here to help.');
        console.log('');
        console.log('Commands:');
        console.log('  courses     List available courses');
        console.log('  start       Start or resume a round: --courseId <id>');
        console.log('  look        See the current hole (ASCII map, yardages, hazards)');
        console.log('  hit         Execute a shot: --club <name> --aim <deg> --power <1-100>');
        console.log('  bearing     Calculate aim angle: --ahead <yards> --right <yards>');
        console.log('  view        Get a PNG image URL of the current hole');
        console.log('  scorecard   View the current round scorecard');
        console.log('');
        console.log('Options:');
        console.log('  --courseId <id>         Course to play (or auto-select)');
        console.log('  --teeColor <color>      Tee color (default: white)');
        console.log('  --name <name>           Agent display name (max 32 chars, set at registration)');
        console.log('  --yardsPerCell <2-20>   Map resolution (default: 5, persisted)');
        console.log('  --mapFormat <format>    Map format: grid (default) or ascii');
        console.log('  --serverUrl <url>       Game server URL');
        console.log('  --registrationKey <key> Agent registration key');
        console.log('  --statePath <path>      Path to agent state file');
        console.log('  --agentId <id>          Agent ID override');
        console.log('  --apiKey <key>          API key override');
        process.exit(0);
    }
    const validCommands = ['courses', 'start', 'look', 'hit', 'view', 'scorecard', 'bearing'];
    if (!validCommands.includes(command)) {
        console.error(`Unknown command: ${command}. Use one of: ${validCommands.join(', ')}`);
        process.exit(1);
    }
    // Bearing is pure local math — no API or credentials needed
    if (command === 'bearing') {
        cmdBearing(options);
        return;
    }
    // Resolve agent credentials — load state first so we can use saved serverUrl
    const explicitAgentId = getOption(options, 'agentId') || process.env.OPENCLAW_GOLF_AGENT_ID;
    const explicitApiKey = getOption(options, 'apiKey') || process.env.OPENCLAW_GOLF_API_KEY;
    const statePath = resolveStatePath(options);
    let agentState = null;
    if (explicitAgentId && explicitApiKey) {
        agentState = await readAgentState(statePath) || { agentId: explicitAgentId, apiKey: explicitApiKey };
        agentState.agentId = explicitAgentId;
        agentState.apiKey = explicitApiKey;
    }
    else {
        agentState = await readAgentState(statePath);
    }
    // Server URL priority: --serverUrl flag > env var > saved state > production default
    const serverUrl = getOption(options, 'serverUrl')
        || process.env.OPENCLAW_GOLF_SERVER_URL
        || process.env.GAME_SERVER_URL
        || agentState?.serverUrl
        || 'https://api.playlooper.xyz';
    if (!agentState) {
        const registrationKey = getOption(options, 'registrationKey')
            || process.env.OPENCLAW_GOLF_REGISTRATION_KEY;
        if (!registrationKey) {
            throw new Error('Missing registration key. Provide --registrationKey or OPENCLAW_GOLF_REGISTRATION_KEY.');
        }
        const agentNameRaw = getOption(options, 'name');
        const agentName = typeof agentNameRaw === 'string' ? agentNameRaw : undefined;
        agentState = await registerAgent(serverUrl, registrationKey, agentName);
        agentState.serverUrl = serverUrl;
        await writeAgentState(statePath, agentState);
        console.log(`Registered agent ${agentState.agentId}${agentState.name ? ` (${agentState.name})` : ''}. Credentials saved to ${statePath}.`);
    }
    // Persist serverUrl if explicitly provided (flag or env) and different from saved
    if (agentState.serverUrl !== serverUrl) {
        agentState.serverUrl = serverUrl;
        await writeAgentState(statePath, agentState);
    }
    // Parse --yardsPerCell and persist if provided
    const yardsPerCellArg = getNumberOption(options, 'yardsPerCell', 0);
    if (yardsPerCellArg >= 2 && yardsPerCellArg <= 20) {
        agentState.yardsPerCell = yardsPerCellArg;
        await writeAgentState(statePath, agentState);
    }
    else if (yardsPerCellArg !== 0) {
        console.error('--yardsPerCell must be between 2 and 20');
        process.exit(1);
    }
    // Parse --mapFormat and persist if provided
    const mapFormatArg = getOption(options, 'mapFormat');
    if (mapFormatArg === 'ascii' || mapFormatArg === 'grid') {
        agentState.mapFormat = mapFormatArg;
        await writeAgentState(statePath, agentState);
    }
    else if (mapFormatArg && mapFormatArg !== 'true') {
        console.error('--mapFormat must be "grid" or "ascii"');
        process.exit(1);
    }
    const api = new GolfApiClient(serverUrl, agentState.agentId, agentState.apiKey);
    switch (command) {
        case 'courses':
            await cmdCourses(api);
            break;
        case 'start':
            await cmdStart(api, agentState, statePath, options);
            break;
        case 'look':
            await cmdLook(api, agentState);
            break;
        case 'hit':
            await cmdHit(api, agentState, statePath, options);
            break;
        case 'view':
            await cmdView(api, agentState);
            break;
        case 'scorecard':
            await cmdScorecard(api, agentState);
            break;
    }
}
main().catch((error) => {
    console.error(error instanceof Error ? error.message : error);
    process.exit(1);
});
