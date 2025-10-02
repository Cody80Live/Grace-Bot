# GraceBot - AI Girlfriend Companion

## Overview

GraceBot is a personal AI assistant designed as a caring girlfriend companion. The application monitors various aspects of the user's life (email, calendar, home security, weather) and provides proactive, personalized notifications and assistance. Built with Python and Flask, it uses AI to make intelligent decisions about what information is important and when to notify the user.

The system features a warm, casual communication style with emoji-enhanced messages, treating the user as a romantic partner while providing practical life management features like schedule tracking, home monitoring, and smart device control.

## User Preferences

Preferred communication style: Simple, everyday language.

Communication tone: Warm, caring girlfriend persona using casual language, emojis, and terms of endearment ("babe", "love"). All responses should be concise, sweet, and supportive.

## System Architecture

### Core Architecture Pattern
- **Modular service-based architecture** - Each feature (Gmail, Calendar, Wyze, etc.) is encapsulated in its own manager module
- **Centralized memory system** - SQLite database with encryption for storing conversations, preferences, and learned behaviors
- **AI-driven decision making** - Uses OpenAI/Grok API to analyze incoming data and determine urgency/relevance
- **Background scheduler** - APScheduler runs periodic tasks (email checks, calendar monitoring) alongside the Flask web server

### Frontend Architecture
- **Simple web dashboard** - HTML/CSS interface for status monitoring and manual triggers
- **Real-time status updates** - AJAX polling to `/status` endpoint for live system information
- **Responsive design** - Mobile-friendly gradient UI with glassmorphism effects

### Backend Architecture
- **Flask web framework** - Main application server handling routes and API endpoints
- **Modular manager classes** - Each integration (Gmail, Calendar, Spotify, Weather, Wyze, Alexa) has dedicated manager
- **Memory Manager** - Handles encrypted storage/retrieval of conversations and user preferences
- **AI Brain** - Centralizes AI API calls with personality configuration and context management
- **Notification Manager** - Unified interface for sending alerts via Twilio SMS or console logging

### Data Storage
- **SQLite database** - Primary storage for conversations and memories
- **Fernet encryption** - All sensitive data encrypted at rest using cryptography library
- **File-based key management** - Encryption key stored in `.encryption_key` file
- **Schema design**: 
  - `memories` table: key-value pairs with categories and timestamps
  - `conversations` table: user/bot message history for context

### Authentication & Authorization
- **OAuth 2.0 flow** - Google Calendar and Gmail access via OAuth tokens
- **Replit Connectors integration** - Centralized credential management through Replit's connector API
- **Token-based access** - Uses `REPL_IDENTITY` or `WEB_REPL_RENEWAL` for Replit API authentication
- **Environment variable secrets** - API keys stored securely in Replit environment

### AI Integration
- **Flexible AI provider** - Supports both OpenAI (GPT-3.5) and xAI (Grok-2)
- **Context-aware conversations** - Includes recent conversation history in prompts
- **Personality system** - System prompts define Grace's caring girlfriend persona
- **Decision-making prompts** - AI determines urgency of emails/events and appropriate responses

### Background Processing
- **APScheduler** - Background scheduler for periodic monitoring tasks
- **Interval triggers** - Configurable check frequencies (default: 10 minutes for email)
- **Graceful shutdown** - `atexit` handler ensures scheduler cleanup
- **Threading model** - Scheduler runs in background thread alongside Flask server

## External Dependencies

### Third-Party APIs & Services

**Google Services**
- **Gmail API** - Email monitoring for unread messages
- **Google Calendar API** - Event tracking and reminder management
- OAuth 2.0 authentication via `google-auth-oauthlib` and `google-api-python-client`

**AI Services**
- **OpenAI API** - GPT-3.5-turbo for conversational AI (fallback)
- **xAI API (Grok)** - Grok-2-1212 model for enhanced AI responses (preferred)
- Unified via OpenAI SDK with custom base URL for xAI

**Communication**
- **Twilio API** - SMS notifications to user's phone
- API key-based authentication with account SID

**Smart Home**
- **Wyze SDK** - Camera event monitoring and motion detection
- Credentials: email/password or access token
- **Alexa Control** - Device control via custom API endpoint (AWS Lambda Smart Home Skill or local APIs)

**Entertainment & Lifestyle**
- **Spotify API** - Playlist creation and music management via `spotipy`
- **OpenWeather API** - Weather data and outfit/activity suggestions

**Replit Platform**
- **Replit Connectors API** - Centralized OAuth token management
- Hostname-based credential retrieval for connected services

### Python Libraries

**Web Framework**
- `Flask` - Web application framework
- `APScheduler` - Background task scheduling

**AI & ML**
- `openai` - OpenAI and xAI API client

**Google APIs**
- `google-auth-oauthlib` - OAuth authentication
- `google-api-python-client` - Gmail and Calendar API access

**External Services**
- `twilio` - SMS notifications
- `spotipy` - Spotify integration
- `requests` - HTTP client for API calls

**Security**
- `cryptography` (Fernet) - Data encryption at rest

**Planned/Optional**
- Wyze SDK (camera integration)
- AlexaPy (Alexa device control)
- Plaid (budget/banking)
- NLTK (sentiment analysis)
- Fitbit/Apple Health APIs (health tracking)

### Database
- **SQLite** - Embedded relational database for memory and conversation storage
- No external database server required
- Encrypted blob storage for sensitive data

### Environment Configuration
Required environment variables:
- `OPENAI_API_KEY` or `XAI_API_KEY` - AI service
- `USER_PHONE_NUMBER` - Notification destination
- `REPLIT_CONNECTORS_HOSTNAME` - Replit connector endpoint
- `REPL_IDENTITY` or `WEB_REPL_RENEWAL` - Replit authentication
- Optional: `WYZE_EMAIL`, `WYZE_PASSWORD`, `OPENWEATHER_API_KEY`, `WEATHER_CITY`, `ALEXA_API_ENDPOINT`

## Recent Changes

### October 2, 2025 - Removed ResMed MyAir Integration
- Removed non-functional MyAir sleep monitoring integration due to authentication issues
- Cleaned up all MyAir-related code from modules, routes, dashboard, and scheduler
- Future health monitoring features (Apple Watch, Fitbit) remain in planning phase