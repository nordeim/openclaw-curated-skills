#!/usr/bin/env node

/**
 * Generates or retrieves a persistent device ID (UUID v4-style).
 * The ID is saved to .device_id in the same directory so the same
 * device ID is reused across sessions (important for auth flow).
 *
 * Usage: node generate-device-id.js
 * Output: the device UUID string
 */

const fs = require("fs")
const path = require("path")
const crypto = require("crypto")

const DEVICE_ID_FILE = path.join(__dirname, ".device_id")

function generateDeviceId() {
	return crypto.randomUUID()
}

function getOrCreateDeviceId() {
	if (fs.existsSync(DEVICE_ID_FILE)) {
		const existing = fs.readFileSync(DEVICE_ID_FILE, "utf-8").trim()
		if (existing) return existing
	}
	const id = generateDeviceId()
	fs.writeFileSync(DEVICE_ID_FILE, id, "utf-8")
	return id
}

const deviceId = getOrCreateDeviceId()
process.stdout.write(deviceId)
