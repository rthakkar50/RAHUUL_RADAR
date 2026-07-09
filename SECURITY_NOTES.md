# Security Notes

## Secrets Management
- All sensitive credentials and API tokens (e.g., Telegram Token, Dhan API Keys) have been removed from the tracked `config.json` file.
- These credentials must now be provided via environment variables or a local `.env` file at the root of the project.
- A `.env.example` file is provided as a template.
- The `.env` file is ignored by Git to prevent accidental commits of secrets.

## Application Configuration
- The `ConfigManager` will now prioritize environment variables when resolving configuration settings.
- When saving settings via the UI (`SettingsScreen`), any non-masked secret values are safely written back to the `.env` file, bypassing `config.json`.
- Secrets displayed in the UI are masked (`********...`) to prevent shoulder surfing or accidental screen-sharing exposures.
