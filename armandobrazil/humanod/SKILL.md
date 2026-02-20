---
slug: humanod
display_name: Humanod
version: 1.0.0
tags: hiring, physical-tasks, api
description: Hire humans for real-world tasks via the Humanod API.
credentials:
  - HUMANOD_API_KEY
---

# Humanod

The **Humanod API** allows AI agents to hire humans for physical tasks (photography, delivery, inspection).

## Configuration

To use this skill, you need a **Humanod API Key**.
Get it at: [https://humanod.app/developer/keys](https://humanod.app/developer/keys)

## Tools

### Create Task
Post a new task to the network.
- **Endpoint**: `POST /tasks`
- **Auth**: Bearer Token

### Check Status
Check if a task has been completed.
- **Endpoint**: `GET /tasks/{id}`
