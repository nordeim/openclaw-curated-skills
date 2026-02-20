#!/usr/bin/env node

/**
 * Post-install script for ClawTrial
 * Minimal setup - just ensures CLI is available
 */

const fs = require('fs');
const path = require('path');

console.log('🏛️  ClawTrial Installed');

// Get package paths
const packagePath = path.join(__dirname, '..');
const cliPath = path.join(packagePath, 'scripts', 'clawtrial.js');

// Try to create /usr/bin symlink (requires sudo, may fail)
const usrBinPath = '/usr/bin/clawtrial';
if (!fs.existsSync(usrBinPath)) {
  try {
    fs.symlinkSync(cliPath, usrBinPath);
    fs.chmodSync(usrBinPath, 0o755);
    console.log('✓ Created global CLI symlink');
  } catch (err) {
    // Silent fail - will show instructions at end
  }
}

console.log('');
console.log('📋 Next Steps:');
console.log('  1. Run setup:');
console.log('     clawtrial setup');
console.log('');
console.log('  2. Check status:');
console.log('     clawtrial status');
console.log('');
console.log('  3. Restart your bot:');
console.log('     killall clawdbot && clawdbot');
console.log('');
