#!/usr/bin/env node
"use strict";
/**
 * PMP-Agent CLI Main Entry
 * Usage: pmp-agent <command> [args...]
 */
const commands = {
    'calc-evm': './calc-evm',
    'evm': './calc-evm',
    'score-risks': './score-risks',
    'risk': './score-risks',
    'calc-velocity': './calc-velocity',
    'velocity': './calc-velocity',
    'health-check': './health-check',
    'health': './health-check',
};
function showHelp() {
    console.log(`
PMP-Agent — PMBOK Project Management CLI

Usage: pmp-agent <command> [options]

Commands:
  calc-evm <BAC> <PV> <EV> <AC>     Calculate earned value metrics
  score-risks <P> <I>             Score a risk (probability × impact)
  calc-velocity <points...>       Calculate sprint velocity
  health-check [<dir>]            Run project health check

Options:
  --json                          Output as JSON (default)
  --markdown                      Output as Markdown
  --file <path>                  Read from file (for batch operations)
  --forecast <points>            Forecast remaining work (velocity only)

Examples:
  pmp-agent calc-evm 10000 5000 4500 4800 --markdown
  pmp-agent score-risks 3 4
  pmp-agent calc-velocity 34 28 42 --forecast 200
  pmp-agent health-check ./my-project
`);
}
function main() {
    const [cmd, ...args] = process.argv.slice(2);
    if (!cmd || cmd === '--help' || cmd === '-h') {
        showHelp();
        process.exit(0);
    }
    const script = commands[cmd];
    if (!script) {
        console.error(`Unknown command: ${cmd}`);
        showHelp();
        process.exit(1);
    }
    // Re-execute with the specific script
    // In actual compiled code, this would require the specific module
    console.log(`Run: npx ${script.replace('./', 'pm-')} ${args.join(' ')}`);
}
main();
//# sourceMappingURL=index.js.map