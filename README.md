# Atelier — Voice Measurement Assistant

A hands-free garment measurement tool for tailors and dressmakers. Keep your hands on the cloth while recording measurements by voice.

## Features

- Voice-driven measurement recording — speak a number to record it
- Multiple garment templates: Men's Suit, Women's Dress, Men's Dress Shirt, Cheongsam/Qipao, Trousers
- Relative adjustments (e.g. "+5" or "minus 3" from the standard)
- Standard acceptance ("okay", "standard", "good", etc.)
- Named POM targeting ("shoulder 46", "waist 72")
- Navigation commands ("next", "previous", "go to chest")
- Session summary with custom vs. standard breakdown

## Voice Commands

| Command | Example |
|---|---|
| Record a value | `"42"` or `"forty two"` |
| Record relative to standard | `"+5"` / `"minus 3"` |
| Accept standard measurement | `"standard"` / `"okay"` / `"good"` |
| Skip current | `"skip"` / `"next"` |
| Go back | `"previous"` / `"back"` |
| Go to a specific POM | `"go to waist"` / `"go to 5"` |
| Fill a specific POM | `"waist 72"` / `"chest plus 4"` |

## Usage

Open `index.html` in Chrome (desktop or Android). The app requires microphone access and uses the Web Speech API — Chrome is the only reliably supported browser.

1. Select a garment template
2. Grant microphone access when prompted
3. Speak measurements as you work
4. Tap **Done** to review the session summary

## Tech

Single-file HTML/CSS/JS app. No build step, no dependencies.
