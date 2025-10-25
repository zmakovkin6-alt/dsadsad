# Telegram Influence Bot

## Overview
This is a Telegram bot that analyzes Instagram account influence metrics. It helps users track and compare multiple Instagram accounts based on various engagement metrics.

## Features
- Add and track multiple Instagram accounts
- Calculate engagement metrics (ER, IS, IA, VS)
- Compare accounts and rank by influence score
- Export data to CSV format
- Store data persistently per chat

## Current State
- Python 3.11 project
- Dependencies installed: python-telegram-bot v20.7, requests
- Workflow configured to run the bot
- Security: Bot token moved to environment variable (TELEGRAM_BOT_TOKEN)

## Setup Required
The bot requires a Telegram Bot API token to run. This should be set as a secret named `TELEGRAM_BOT_TOKEN`.

## Project Architecture
- `influence_bot.py` - Main bot implementation with all commands and metrics calculations
- `bot_data/` - Directory for storing user data (per chat JSON files)
- `requirements.txt` - Python dependencies
- `runtime.txt` - Python version specification

## Bot Commands
- `/start` - Show welcome message and available commands
- `/add` - Add a new Instagram account (interactive flow)
- `/list` - Show all saved accounts
- `/compare` - Compare accounts and show rankings
- `/export` - Export data to CSV
- `/clear` - Clear all chat data
- `/formulas` - Show metric calculation formulas
- `/help` - Show help message

## Metrics Calculated
1. **ER (Engagement Rate)**: `(avg_likes + avg_comments) / followers * 100%`
2. **IS (Account Activity)**: `weeks_active / total_weeks * 100%`
3. **VS (Visual Style)**: User rating 1-5 normalized to percentage
4. **IA (Interaction Index)**: User-provided percentage
5. **I (Influence Index)**: `0.4*ER + 0.3*IS + 0.2*IA + 0.1*VS`

## Recent Changes
- 2025-10-25: Imported from GitHub and set up for Replit
  - Installed Python 3.11
  - Updated python-telegram-bot to v20.7
  - Moved hardcoded bot token to environment variable for security
  - Added .gitignore for Python projects
  - Configured workflow to run the bot
  - Added token validation with helpful error messages
