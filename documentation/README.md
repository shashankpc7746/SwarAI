<div align="center">

# 🤖 SwarAI

### Multi-Agent AI Task Automation Assistant

<p align="center">
  <img src="https://img.shields.io/badge/SwarAI-AI%20Assistant-6366f1?style=for-the-badge&logo=robot&logoColor=white" alt="SwarAI" />
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" /></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.115+-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI" /></a>
  <a href="https://nextjs.org/"><img src="https://img.shields.io/badge/Next.js-15.5-000000?style=for-the-badge&logo=next.js&logoColor=white" alt="Next.js" /></a>
  <a href="LICENSE"><img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License" /></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/CrewAI-0.86+-FF6B6B?style=flat-square&logo=ai&logoColor=white" alt="CrewAI" />
  <img src="https://img.shields.io/badge/LangChain-1.2+-1C3C3C?style=flat-square&logo=chainlink&logoColor=white" alt="LangChain" />
  <img src="https://img.shields.io/badge/Groq-LLM-F55036?style=flat-square&logo=ai&logoColor=white" alt="Groq" />
  <img src="https://img.shields.io/badge/MongoDB-Optional-47A248?style=flat-square&logo=mongodb&logoColor=white" alt="MongoDB" />
</p>

<h4>A sophisticated multi-agent AI system powered by CrewAI, LangChain, and Groq LLM</h4>

<p align="center">
  <a href="#-features">Features</a> •
  <a href="#-quick-start">Quick Start</a> •
  <a href="#-installation">Installation</a> •
  <a href="#-usage">Usage</a> •
  <a href="#-api-reference">API</a> •
  <a href="#-recent-improvements--new-features">What's New</a> •
  <a href="#-contributing">Contributing</a>
</p>

</div>

---

## 📖 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [AI Agents](#-ai-agents)
- [API Reference](#-api-reference)
- [Development](#-development)
- [Troubleshooting](#-troubleshooting)
- [Contributing](#-contributing)
- [Recent Improvements](#-recent-improvements--new-features)
- [Roadmap](#-roadmap)
- [License](#-license)

---

## 🌟 Overview

**SwarAI** is an advanced multi-agent AI task automation assistant that combines natural language processing, voice recognition, file management, and cross-platform communication into a unified, intelligent system.

### Key Highlights

- 🤖 **13 Specialized AI Agents** for different tasks
- 🚀 **65+ Application Launchers** including Windows apps, browsers, Office suite, and development tools
- 🌐 **15+ Website Quick Access** to popular platforms and services
- 🎤 **Voice Recognition** with multiple engines (Google Speech, Whisper AI)
- 🗣️ **Text-to-Speech** with intelligent speech filtering and context-aware output
- 📱 **WhatsApp Integration** with fuzzy contact matching and smart message handling
- 📁 **Intelligent File Search** with fuzzy matching, multi-location scanning, and latest file detection
- 📧 **AI-Powered Email** with automatic content generation and subject correction
- ⚙️ **System Control** (11 operations): Volume, brightness, battery, lock, power management
- 🧠 **Smart Intent Detection** with AI Enhancement Layer (auto-fixes typos and improves clarity)
- 🔄 **Multi-Agent Orchestration** using CrewAI for complex workflows
- 🌐 **Modern Web Interface** with dynamic animations, login system, and profile settings
- 🔐 **Authentication** with JWT tokens and protected routes
- 🚀 **FastAPI Backend** with WebSocket support and real-time processing
- 💾 **Conversation Memory** with MongoDB (optional)

---

## ✨ Features

### 🎯 Core Capabilities

#### 1. **Conversational AI**

- Natural language understanding with context awareness
- Personality-driven responses
- Multi-turn conversation support
- Intent classification and routing
- Emotional intelligence
- **AI Enhancement Layer**: Automatically improves command clarity and fixes typos using Groq LLM

#### 2. **Voice Recognition & TTS**

- **Speech-to-Text**: Google Speech Recognition, Whisper AI
- **Text-to-Speech**: Microsoft Edge TTS, Google TTS, Coqui TTS, pyttsx3
- Multi-language support (English variants)
- Noise reduction and ambient adjustment
- Real-time voice processing
- Context-aware speech filtering (removes URLs, paths, technical jargon)

#### 3. **WhatsApp Automation**

- Send messages via voice or text commands
- Contact management with fuzzy search
- WhatsApp URL generation (wa.me format)
- Natural language command parsing
- Multiple command pattern support

#### 4. **File Management**

- Cross-platform file search (Windows, macOS, Linux)
- Fuzzy matching algorithm
- Recursive directory searching
- File operations: search, open, share
- Performance-optimized scanning

#### 5. **System Control**

- Volume control (Windows with pycaw)
- Brightness adjustment
- Battery status monitoring
- System information retrieval
- Application launching

#### 6. **Multi-Agent Orchestration**

- CrewAI-powered agent coordination
- Complex workflow execution
- Task delegation and routing
- Error recovery and fallbacks
- Parallel task processing

---

<!-- trimmed for brevity in documentation copy; full content moved into file -->
