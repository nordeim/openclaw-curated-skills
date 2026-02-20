---
name: my-fitness-claw
description: Your personal nutrition sidekick. Log meals in plain natural language, track macros (P/C/F) automatically, and visualize your progress on a beautiful real-time dashboard. Includes AI-driven health insights, common food memory, and daily progress tracking—all controlled via chat.
requires:
  tools: [canvas, read, write, edit]
  paths: [nutrition/, canvas/, memory/]
---

# MyFitnessClaw

This skill manages your nutritional data and provides a visual dashboard for tracking macros using OpenClaw's native tools.

## Core Files

- `nutrition/daily_macros.json`: The structured log of daily intake.
- `nutrition/targets.json`: Daily nutritional goals (calories, protein, carbs, fats).
- `nutrition/insights.json`: AI-generated tips based on current progress.
- `nutrition/foods/common.md`: A reference list of frequently eaten foods and their macros.
- `canvas/index.html`: The visual dashboard for the OpenClaw Canvas.

## Workflow: Logging Food

When the user mentions eating something:
1. **Estimate Macros**: If the user doesn't provide them, estimate calories, protein, carbs, and fats. Check `nutrition/foods/common.md` first.
2. **Update Daily Log**: Add values to `nutrition/daily_macros.json`.
3. **Update Memory**: Log the meal in the agent's current daily memory file (e.g., `memory/YYYY-MM-DD.md`) using the `write` or `edit` tool.
4. **Update Dashboard**: 
   - Read the latest data from `nutrition/daily_macros.json`, `nutrition/targets.json`, and `nutrition/insights.json`.
   - Use the `edit` tool to update the following variables in `canvas/index.html`:
     - `const fallbackData`: Update with the full array from `daily_macros.json`.
     - `const fallbackGoals`: Update with the full JSON object from `targets.json`.
     - `const fallbackInsights`: Update with the full JSON object from `insights.json`.
   - Use `canvas(action=present, url='canvas/index.html')` to show the updated dashboard.
5. **Generate Insights**: Analyze progress against goals in `nutrition/targets.json` and update `nutrition/insights.json`.

## Dashboard Maintenance

The dashboard (`canvas/index.html`) reads from the JSON files but uses `fallbackData` for immediate persistence. Always keep the HTML fallbacks in sync with `daily_macros.json`.
