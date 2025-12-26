from flask import Blueprint, request, jsonify
import logging
from models import db, Subscriber, Journalist, DeliveryChannel
from services.whatsapp_service import WhatsAppService

logger = logging.getLogger(__name__)
whatsapp_bp = Blueprint('whatsapp', __name__, url_prefix='/whatsapp')

@whatsapp_bp.route('/webhook/<int:journalist_id>', methods=['GET', 'POST'])
def webhook(journalist_id):
    """WhatsApp webhook handler for message reception and processing
    
    GET: Webhook verification
    POST: Incoming message handling
    """
    
    # Webhook verification
    if request.method == 'GET':
        token = request.args.get('hub.verify_token')
        challenge = request.args.get('hub.challenge')
        mode = request.args.get('hub.mode')
        
        # Simple verification - in production use environment variable
        VERIFY_TOKEN = "whatsapp_verify_token"
        
        if mode == "subscribe" and token == VERIFY_TOKEN:
            logger.info(f"✓ WhatsApp webhook verified for journalist {journalist_id}")
            return challenge, 200
        else:
            logger.warning(f"❌ WhatsApp webhook verification failed for journalist {journalist_id}")
            return "Forbidden", 403
    
    # Handle incoming messages
    if request.method == 'POST':
        data = request.get_json()
        
        try:
            journalist = Journalist.query.get(journalist_id)
            if not journalist:
                logger.error(f"❌ Journalist {journalist_id} not found")
                return jsonify({"status": "error"}), 404
            
            # Extract message from webhook payload
            messages = data.get('entry', [{}])[0].get('changes', [{}])[0].get('value', {}).get('messages', [])
            
            if not messages:
                logger.info(f"⚠️  No messages in WhatsApp webhook payload")
                return jsonify({"status": "success"}), 200
            
            for message in messages:
                phone = message.get('from')
                message_text = message.get('text', {}).get('body')
                message_id = message.get('id')
                
                if not message_text or not phone:
                    continue
                
                logger.info(f"📨 WhatsApp message received: {phone} - {message_text[:50]}")
                
                # Find or create subscriber
                subscriber = Subscriber.query.filter_by(
                    journalist_id=journalist_id,
                    whatsapp_phone=phone,
                    channel_type='whatsapp'
                ).first()
                
                if not subscriber:
                    # New subscriber
                    subscriber = Subscriber(
                        journalist_id=journalist_id,
                        whatsapp_phone=phone,
                        channel_type='whatsapp',
                        is_approved=False,
                        is_active=True
                    )
                    db.session.add(subscriber)
                    db.session.commit()
                    logger.info(f"✓ New WhatsApp subscriber created: {phone}")
                
                # Check subscription status
                is_approved, status_message = WhatsAppService.is_subscriber_approved(subscriber)
                
                if not is_approved:
                    # Send validation message
                    send_whatsapp_message(journalist_id, phone, status_message)
                    logger.info(f"⚠️  Subscriber {phone} not approved")
                    continue
                
                # Handle message commands (similar to Telegram)
                if message_text.lower().startswith('/latest'):
                    response = WhatsAppService.get_latest_summary(journalist_id)
                elif message_text.lower().startswith('/articles'):
                    # Extract date if provided
                    parts = message_text.split()
                    if len(parts) > 1:
                        date_str = parts[1]
                        response = WhatsAppService.search_articles_by_date(journalist_id, date_str)
                    else:
                        response = "📅 Format: /articles DD/MM/YYYY ou /articles YYYY-MM-DD"
                else:
                    # Natural language query
                    response = WhatsAppService.handle_message(journalist, subscriber, message_text)
                
                # Send response
                if response:
                    send_whatsapp_message(journalist_id, phone, response)
                    logger.info(f"✓ Response sent to {phone}")
            
            return jsonify({"status": "success"}), 200
            
        except Exception as e:
            logger.error(f"❌ WhatsApp webhook error: {str(e)[:100]}")
            return jsonify({"status": "error", "message": str(e)}), 500

def send_whatsapp_message(journalist_id: int, phone: str, message: str):
    """Send WhatsApp message via Twilio
    
    Args:
        journalist_id: Journalist ID
        phone: Recipient phone number
        message: Message text
    """
    try:
        channel = DeliveryChannel.query.filter_by(
            journalist_id=journalist_id,
            channel_type='whatsapp'
        ).first()
        
        if not channel or not channel.whatsapp_api_key:
            logger.warning(f"❌ WhatsApp channel not configured for journalist {journalist_id}")
            return False
        
        from twilio.rest import Client
        
        client = Client(channel.whatsapp_account_id, channel.whatsapp_api_key)
        
        msg = client.messages.create(
            body=message,
            from_=f"whatsapp:{channel.whatsapp_account_id}",
            to=f"whatsapp:{phone}"
        )
        
        logger.info(f"✓ WhatsApp message sent: {msg.sid}")
        return True
        
    except ImportError:
        logger.warning("❌ Twilio not installed")
        return False
    except Exception as e:
        logger.error(f"❌ Error sending WhatsApp message: {str(e)[:100]}")
        return False
