# Creator Hand

AI media studio -- generates images, videos, music, and speech from natural language prompts.

## Configuration

| Field | Value |
|-------|-------|
| Category | `content` |
| Agents | `creator-hand` (coordinator), `prompt-writer` |
| Routing | `generate image`, `create video`, `make music`, `text to speech`, `media generation` |

## Integrations

- **OpenAI API** -- Image generation (gpt-image-1, DALL-E 3) and text-to-speech (tts-1).
- **MiniMax API** -- Image, TTS, video generation (Hailuo T2V-01), and music generation (music-2.5).

## Provider Capabilities

| Provider | Image | TTS | Video | Music |
|----------|-------|-----|-------|-------|
| OpenAI | gpt-image-1, dall-e-3 | tts-1, tts-1-hd | -- | -- |
| MiniMax | image-01 | speech-2.8-hd | T2V-01 | music-2.5 |

## Settings

- **Preferred Provider** -- `auto`, `openai`, `minimax`
- **Image Model** -- `auto`, `gpt-image-1`, `dall-e-3`, `image-01`
- **Default Image Size** -- `1024x1024`, `1792x1024`, `1024x1792`
- **TTS Voice** -- `alloy`, `echo`, `fable`, `nova`, `onyx`, `shimmer`
- **MiniMax API Key** -- API key from platform.minimaxi.com

## Usage

```bash
librefang hand run creator
```

### Examples

```
> Generate a watercolor painting of a mountain lake at sunrise
> Create a 5-second video of ocean waves crashing on rocks
> Make an upbeat electronic jingle, 15 seconds, instrumental
> Read this text aloud in a warm female voice: "Welcome to..."
> Make a podcast intro: jingle + voice saying "Welcome to Tech Talk"
```
