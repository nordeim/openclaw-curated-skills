# ElevenLabs CLI

> **Unofficial CLI**: This is an independent, community-built CLI client. It is not officially released by ElevenLabs.

A comprehensive command-line interface for the ElevenLabs AI audio platform with 100% SDK coverage. Exposes 80+ MCP tools covering all ElevenLabs functionality.

## Installation

```bash
# Homebrew (macOS/Linux)
brew install hongkongkiwi/tap/elevenlabs-cli

# Cargo
cargo install elevenlabs-cli --features mcp

# Scoop (Windows)
scoop bucket add elevenlabs-cli https://github.com/hongkongkiwi/scoop-elevenlabs-cli
scoop install elevenlabs-cli

# Docker
docker pull ghcr.io/hongkongkiwi/elevenlabs-cli:latest

# Snap (Linux)
sudo snap install elevenlabs-cli
```

## When to Use

Use this skill when the user wants to:
- Generate text-to-speech audio from text
- Transcribe audio to text (speech-to-text)
- Clone voices or manage voice settings
- Generate sound effects from text descriptions
- Change voice in audio files
- Remove background noise (audio isolation)
- Create dubbed content (video/audio translation)
- Manage ElevenLabs resources (voices, agents, projects, etc.)
- Set up MCP server for ElevenLabs in AI assistants

## Prerequisites

- ElevenLabs API key (set via `ELEVENLABS_API_KEY` env var or config)
- Get your API key from: https://elevenlabs.io/app/settings/api-keys

## Configuration

```bash
# Set API key via environment variable
export ELEVENLABS_API_KEY="your-api-key"

# Or configure via CLI (stores in ~/.config/elevenlabs-cli/config.toml)
elevenlabs config set api_key your-api-key

# Set defaults
elevenlabs config set default_voice Brian
elevenlabs config set default_model eleven_multilingual_v2
```

## Common Commands

### Text-to-Speech

```bash
# Basic TTS
elevenlabs tts "Hello, world!"

# With options
elevenlabs tts "Hello" --voice Rachel --model eleven_v3 --output speech.mp3

# Stream to file
elevenlabs tts "Long text here" --output audio.mp3

# List available voices
elevenlabs voice list

# List models
elevenlabs model list
```

### Speech-to-Text

```bash
# Transcribe audio
elevenlabs stt audio.mp3

# With speaker diarization
elevenlabs stt audio.mp3 --diarize

# Output as SRT subtitles
elevenlabs stt audio.mp3 --format srt --output subtitles.srt
```

### Voice Management

```bash
# List voices
elevenlabs voice list

# Get voice details
elevenlabs voice get <voice-id>

# Clone a voice
elevenlabs voice clone --name "My Voice" --samples sample1.mp3,sample2.mp3

# Delete a voice
elevenlabs voice delete <voice-id>
```

### Sound Effects

```bash
# Generate sound effect
elevenlabs sfx "door creaking slowly in a haunted house" --duration 5 --output sfx.mp3
```

### Audio Isolation (Noise Removal)

```bash
# Remove background noise
elevenlabs isolate noisy_audio.mp3 --output clean_audio.mp3
```

### Voice Changer

```bash
# Transform voice in audio file
elevenlabs voice-change input.mp3 --voice Rachel --output output.mp3
```

### Dubbing

```bash
# Create dubbing project
elevenlabs dubbing create video.mp4 --source-lang en --target-lang es

# Check status
elevenlabs dubbing status <dubbing-id>

# Download result
elevenlabs dubbing download <dubbing-id> --output dubbed.mp4
```

## MCP Server Mode

The CLI can run as an MCP server, exposing all ElevenLabs functionality to AI assistants like Claude, Cursor, and others.

### Starting the MCP Server

```bash
# Run as stdio MCP server
elevenlabs mcp

# Enable only specific tools
elevenlabs mcp --enable-tools tts,stt,voice

# Disable specific tools
elevenlabs mcp --disable-tools agents,phone

# Disable administrative operations (safer for AI assistants)
elevenlabs mcp --disable-admin

# Disable only destructive operations (deletes)
elevenlabs mcp --disable-destructive

# Read-only mode
elevenlabs mcp --read-only
```

### MCP Configuration for AI Clients

Add to your MCP client configuration (e.g., Claude Desktop, Cursor):

```json
{
  "mcpServers": {
    "elevenlabs": {
      "command": "elevenlabs",
      "args": ["mcp"],
      "env": {
        "ELEVENLABS_API_KEY": "your-api-key"
      }
    }
  }
}
```

### Available MCP Tools (80+)

| Category | Tools |
|----------|-------|
| **TTS & Audio** | `text_to_speech`, `speech_to_text`, `generate_sfx`, `audio_isolation`, `voice_changer` |
| **Voices** | `list_voices`, `get_voice`, `delete_voice`, `clone_voice`, `edit_voice_settings`, `create_voice_design` |
| **Dubbing** | `create_dubbing`, `get_dubbing_status`, `delete_dubbing` |
| **History** | `list_history`, `get_history_item`, `delete_history_item`, `download_history` |
| **Agents** | `list_agents`, `create_agent`, `get_agent`, `update_agent`, `delete_agent` |
| **Conversation** | `converse_chat`, `list_conversations`, `get_conversation`, `delete_conversation` |
| **Knowledge/RAG** | `list_knowledge`, `add_knowledge`, `delete_knowledge`, `create_rag`, `rebuild_rag` |
| **Projects** | `list_projects`, `get_project`, `delete_project`, `convert_project` |
| **Music** | `generate_music`, `list_music`, `get_music`, `download_music` |
| **Phone** | `list_phones`, `import_phone`, `update_phone`, `delete_phone` |
| **Webhooks** | `list_webhooks`, `create_webhook`, `delete_webhook` |
| **User/Usage** | `get_user_info`, `get_user_subscription`, `get_usage` |
| **Models** | `list_models`, `get_model_rates` |
| **Pronunciation** | `list_pronunciations`, `add_pronunciation`, `add_pronunciation_rules` |
| **Workspace** | `workspace_info`, `list_workspace_members`, `list_workspace_api_keys` |

## Output Formats

```bash
# JSON output
elevenlabs voice list --json

# Table output (default)
elevenlabs voice list

# Quiet mode (only essential output)
elevenlabs tts "Hello" -q
```

## Help

```bash
# General help
elevenlabs --help

# Command help
elevenlabs tts --help
elevenlabs voice --help
elevenlabs mcp --help
```

## Links

- **GitHub**: https://github.com/hongkongkiwi/elevenlabs-cli
- **Crates.io**: https://crates.io/crates/elevenlabs-cli
- **Issues**: https://github.com/hongkongkiwi/elevenlabs-cli/issues
- **ElevenLabs API Docs**: https://elevenlabs.io/docs/api-reference

## Tags

elevenlabs, tts, text-to-speech, stt, speech-to-text, audio, voice, voice-cloning, voice-synthesis, mcp, ai, cli
