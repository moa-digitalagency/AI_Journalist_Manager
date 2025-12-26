# WhatsApp Bot Documentation

## Overview

The WhatsApp bot provides multi-channel conversation handling similar to the Telegram bot, with natural language query support, subscription validation, and article history search.

## Features

### 1. Conversation Handling
- Natural language message processing
- Automatic subscriber registration
- Subscription validation with admin approval

### 2. Subscription Validation
- New subscribers automatically marked as pending
- Admin must approve before access
- Unapproved users receive notification message
- Expiration date support

### 3. Article Search
- Search articles by date (DD/MM/YYYY or YYYY-MM-DD format)
- Natural language keyword search
- Returns matching articles with source and time

### 4. Commands
- `/latest` - Get the latest summary
- `/articles DD/MM/YYYY` - Search articles by date
- Any natural language query - AI-powered response using article context

## Configuration

### Setup

1. **Twilio Account**: Create WhatsApp Business Account
2. **Delivery Channel**: Configure in journalist form
   - Phone number: `+1234567890` format
   - Account ID: Twilio Account SID
   - API Key: Twilio Auth Token

3. **Webhook**: Configure Twilio webhook to:
   ```
   https://yourapp.com/whatsapp/webhook/<journalist_id>
   ```

4. **Webhook Token**: Update `VERIFY_TOKEN` in `routes/whatsapp.py` (use environment variable in production)

### Database

Subscribers table now supports:
- `channel_type` - 'telegram' or 'whatsapp'
- `whatsapp_phone` - Phone number in +1234567890 format
- `is_approved` - Admin approval status
- `is_active` - Subscription active status

## Message Flow

```
WhatsApp Message
       ↓
Webhook Handler (/whatsapp/webhook/<journalist_id>)
       ↓
Find/Create Subscriber
       ↓
Check Approval Status
       ├─ Not Approved → Send Validation Message
       └─ Approved → Process Message
           ├─ /latest → Get Latest Summary
           ├─ /articles <date> → Search by Date
           └─ Natural Language → AI Response
                    ↓
              Search Articles
                    ↓
              AI Service Answer
                    ↓
          Send Response via Twilio
```

## WhatsAppService Methods

### `is_subscriber_approved(subscriber) -> (bool, str)`
Check if subscriber is approved and active.

### `handle_message(journalist, subscriber, message: str) -> str`
Process natural language message with article context.

### `search_articles_by_date(journalist_id: int, target_date: str) -> str`
Search articles by date and return formatted list.

### `get_latest_summary(journalist_id: int) -> str`
Get most recent summary text.

## Error Handling

- Missing subscriber - auto-register and notify
- Unapproved account - send validation message
- Expired subscription - notify user
- Invalid date format - return format hint
- Twilio errors - log and return error message

## Security

- Webhook verification with token
- Subscription validation before access
- Message from authorized phone only
- Admin approval required for new users

## Environment Variables

```
WHATSAPP_VERIFY_TOKEN=<your-token>  # Webhook verification
```

## Testing

Create test subscriber:
```python
from models import Subscriber
sub = Subscriber(
    journalist_id=1,
    whatsapp_phone="+1234567890",
    channel_type='whatsapp',
    is_approved=True,
    is_active=True
)
db.session.add(sub)
db.session.commit()
```

Send test via Twilio API or webhook simulator.
