This repository implements a ROS 2 text-to-speech module used to enable spoken interaction on robots from the Bio-Robotics Lab.

## Overview

The node exposes a ROS 2 service that receives a text string and synthesizes speech locally (offline).  
The module is designed for robotics competitions, where network connectivity can be unreliable and low-latency, stable behavior is required.

**Key goals**
- **Offline-first**: no cloud dependency.
- **Low-latency**: fast enough for interactive robot dialogue.
- **Lightweight**: runs on CPU and avoids GPU memory usage unless explicitly enabled.
- **ROS 2-friendly**: simple service API for integration with planners, dialogue managers, and state machines.

---

## Text-to-Speech Engine

This module uses **Mycroft Mimic3** as the TTS engine.

**Why Mimic3**
- **Runs fully offline** once the voice is downloaded.
- **CPU-friendly** and stable for long runs (competition-friendly).
- Uses **ONNX Runtime** under the hood for efficient inference.
- Simple CLI (`mimic3`) makes integration easy via `subprocess`.

---

## Voice Model Used

We use the Mimic3 voice:

### `en_US/ljspeech_low`

**Characteristics**
- **Language:** English (US)
- **Style:** clear, neutral, professional (assistant-like)
- **Quality tier:** `low` (optimized footprint + speed)
- **Best for:** robotics competitions and embedded-ish setups where reliability matters more than heavy emotional modeling

**Why this voice**
- It sounds natural enough for spoken interaction and demos, while being computationally lightweight and consistent.
- The `low` tier is typically faster and less resource-intensive than larger variants, which helps avoid performance issues during competitions.

> Note: Mimic3 voices do not provide advanced “emotion control” comparable to large transformer TTS models.  
> However, prosody can be improved using punctuation and tuning parameters (see below).

---

## Installation

Run the provided installer:

```bash
chmod +x install.sh
./install.sh
