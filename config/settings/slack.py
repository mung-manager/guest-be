from config.env import env

SLACK_API_TOKEN = env.str("SLACK_API_TOKEN")
SLACK_ERROR_PARTNER_CHANNEL_ID = env.str("SLACK_ERROR_PARTNER_CHANNEL_ID")
SLACK_ERROR_GUEST_CHANNEL_ID = env.str("SLACK_ERROR_GUEST_CHANNEL_ID")
