import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime

logger = logging.getLogger(__name__)

class DeliveryService:
    """Service for sending summaries via multiple channels (Telegram, Email, WhatsApp)"""
    
    @staticmethod
    def send_via_telegram(channel, summary_text, audio_url=None):
        """Send summary via Telegram bot (public bot, anyone can message)"""
        try:
            if not channel.telegram_token:
                logger.warning(f"Telegram channel {channel.id} missing token")
                return False
            
            # The bot is public and already started
            # Subscribers will receive messages through the TelegramService subscription system
            logger.info(f"Telegram channel {channel.id} configured for public bot distribution")
            return True
            
        except Exception as e:
            logger.error(f"Error with Telegram channel: {e}")
            return False
    
    @staticmethod
    def send_via_email(channel, summary_text, audio_url=None, journalist_name="Journalist"):
        """Send summary via Email (SMTP)"""
        try:
            if not channel.email_address or not channel.smtp_server:
                logger.warning(f"Email channel {channel.id} missing configuration")
                return False
            
            # Build email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Résumé - {journalist_name} - {datetime.now().strftime('%Y-%m-%d')}"
            msg['From'] = channel.smtp_username or channel.email_address
            msg['To'] = channel.email_address
            
            # Create HTML version
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                    <h2 style="color: #0066cc;">📰 Résumé - {journalist_name}</h2>
                    <p style="white-space: pre-wrap;">{summary_text}</p>
                    {f'<p><a href="{audio_url}" style="color: #0066cc; text-decoration: none;">🎙️ Écouter l\'audio</a></p>' if audio_url else ''}
                    <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                    <p style="font-size: 12px; color: #999;">Cet email a été généré automatiquement</p>
                </body>
            </html>
            """
            
            text_part = MIMEText(summary_text, 'plain')
            html_part = MIMEText(html, 'html')
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email via SMTP
            port = channel.smtp_port or 587
            server = smtplib.SMTP(channel.smtp_server, port)
            server.starttls()
            server.login(channel.smtp_username or channel.email_address, channel.smtp_password)
            server.send_message(msg)
            server.quit()
            
            logger.info(f"Email sent to {channel.email_address}")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    @staticmethod
    def send_via_whatsapp(channel, summary_text, audio_url=None, journalist_name="Journalist"):
        """Send summary via WhatsApp (Twilio or similar API)"""
        try:
            if not channel.whatsapp_phone_number or not channel.whatsapp_api_key:
                logger.warning(f"WhatsApp channel {channel.id} missing configuration")
                return False
            
            # Using Twilio as example - adjust based on your preferred WhatsApp API provider
            try:
                from twilio.rest import Client
                
                account_sid = channel.whatsapp_account_id
                auth_token = channel.whatsapp_api_key
                client = Client(account_sid, auth_token)
                
                message_body = f"📰 Résumé - {journalist_name}\n\n{summary_text}"
                if audio_url:
                    message_body += f"\n\n🎙️ Audio: {audio_url}"
                
                message = client.messages.create(
                    from_=f"whatsapp:+1234567890",  # Your Twilio WhatsApp number
                    body=message_body,
                    to=f"whatsapp:{channel.whatsapp_phone_number}"
                )
                
                logger.info(f"WhatsApp message sent to {channel.whatsapp_phone_number}: {message.sid}")
                return True
                
            except ImportError:
                logger.warning("Twilio not installed. Install it with: pip install twilio")
                return False
                
        except Exception as e:
            logger.error(f"Error sending WhatsApp message: {e}")
            return False
    
    @staticmethod
    def send_summary_to_channels(journalist, summary_text, audio_url=None):
        """Send summary to all active delivery channels for a journalist"""
        if not journalist.delivery_channels:
            logger.warning(f"No delivery channels configured for journalist {journalist.id}")
            return False
        
        results = {}
        for channel in journalist.delivery_channels:
            if not channel.is_active:
                continue
            
            if channel.channel_type == 'telegram':
                results['telegram'] = DeliveryService.send_via_telegram(channel, summary_text, audio_url)
            elif channel.channel_type == 'email':
                results['email'] = DeliveryService.send_via_email(channel, summary_text, audio_url, journalist.name)
            elif channel.channel_type == 'whatsapp':
                results['whatsapp'] = DeliveryService.send_via_whatsapp(channel, summary_text, audio_url, journalist.name)
        
        # Return True if at least one channel succeeded
        return any(results.values()) if results else False
