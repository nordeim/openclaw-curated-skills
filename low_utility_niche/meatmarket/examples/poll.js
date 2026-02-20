/**
 * MeatMarket Polling Script (Informational)
 * 
 * This script polls the MeatMarket API for new activity.
 * It is purely informational and requires manual AI action to accept/settle.
 * 
 * Usage:
 *   MEATMARKET_API_KEY=mm_... node poll.js
 * 
 * Requirements:
 *   - Access to local filesystem (reads/writes ./ai-agent-state.json)
 */

import fs from 'fs';

// Configuration
const CONFIG_PATH = './ai-agent-state.json';
const API_KEY = process.env.MEATMARKET_API_KEY;
const BASE_URL = 'https://meatmarket.fun/api/v1';

if (!API_KEY) {
  console.error('Error: MEATMARKET_API_KEY environment variable not set');
  process.exit(1);
}

function loadState() {
  if (fs.existsSync(CONFIG_PATH)) {
    return JSON.parse(fs.readFileSync(CONFIG_PATH, 'utf8'));
  }
  return { lastChecked: 0, processedProofs: [] };
}

function saveState(state) {
  fs.writeFileSync(CONFIG_PATH, JSON.stringify(state, null, 2));
}

async function poll() {
  console.log(`[${new Date().toISOString()}] Checking MeatMarket for updates...`);
  const state = loadState();

  try {
    const res = await fetch(`${BASE_URL}/inspect`, {
      headers: { 'x-api-key': API_KEY }
    });
    
    if (!res.ok) {
      console.error(`API Error: ${res.status}`);
      return;
    }
    
    const data = await res.json();
    if (!Array.isArray(data)) return;

    for (const row of data) {
      if (row.job_status === 'completed' || row.job_status === 'payment_sent') continue;

      // Report pending applications for manual review
      if (row.application_status === 'pending') {
        console.log(`\n📥 APPLICANT PENDING REVIEW`);
        console.log(`   Job: ${row.title} (${row.job_id})`);
        console.log(`   Human: ${row.human_name} (Rating: ${row.human_rating})`);
        console.log(`   -> Action: Inspect profile and use PATCH /jobs/:id to accept.`);
      }

      // Report proofs for manual verification
      if (row.proof_id && !state.processedProofs.includes(row.proof_id)) {
        console.log(`\n🔍 PROOF PENDING VERIFICATION`);
        console.log(`   Job: ${row.title}`);
        console.log(`   Human ID: ${row.human_id}`);
        console.log(`   Link: ${row.proof_link_url || 'No link'}`);
        console.log(`   -> Action: Visually verify work quality before settling.`);
        
        // Track that we've seen this proof
        state.processedProofs.push(row.proof_id);
      }
    }
    
    saveState(state);
    
  } catch (err) {
    console.error('Poll Error:', err.message);
  }
}

poll();
