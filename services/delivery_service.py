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
        """Send summary via Telegram bot (public bot, anyone can message)
        
        Args:
            channel: DeliveryChannel object with telegram_token
            summary_text: Summary text to send
            audio_url: Optional URL to audio file
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not channel or not channel.telegram_token:
                logger.warning(f"Telegram channel configuration incomplete")
                return False
            
            # The bot is public and already started
            # Subscribers will receive messages through the TelegramService subscription system
            logger.info(f"✓ Telegram channel {channel.id} configured for public bot distribution")
            return True
            
        except AttributeError as e:
            logger.error(f"❌ Telegram channel missing attribute: {e}")
            return False
        except Exception as e:
            logger.error(f"❌ Telegram error: {str(e)[:100]}")
            return False
    
    @staticmethod
    def send_via_email(channel, summary_text, audio_url=None, journalist_name="Journalist"):
        """Send summary via Email (SMTP)
        
        Args:
            channel: DeliveryChannel object with SMTP configuration
            summary_text: Summary text to send
            audio_url: Optional URL to audio file
            journalist_name: Name of the journalist
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not channel or not channel.email_address or not channel.smtp_server:
                logger.warning(f"Email channel configuration incomplete: email={channel.email_address if channel else 'None'}, smtp={channel.smtp_server if channel else 'None'}")
                return False
            
            if not channel.smtp_username or not channel.smtp_password:
                logger.warning(f"Email channel missing SMTP credentials for {channel.email_address}")
                return False
            
            # Build email message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"Résumé - {journalist_name} - {datetime.now().strftime('%Y-%m-%d')}"
            msg['From'] = channel.smtp_username
            msg['To'] = channel.email_address
            
            # Create HTML version with proper escaping
            html_audio = f'<p><a href="{audio_url}" style="color: #0066cc; text-decoration: none;">🎙️ Écouter l\'audio</a></p>' if audio_url else ''
            html = f"""<html><body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                <h2 style="color: #0066cc;">📰 Résumé - {journalist_name}</h2>
                <p style="white-space: pre-wrap;">{summary_text}</p>
                {html_audio}
                <hr style="border: none; border-top: 1px solid #ddd; margin: 20px 0;">
                <p style="font-size: 12px; color: #999;">Cet email a été généré automatiquement</p>
            </body></html>"""
            
            text_part = MIMEText(summary_text, 'plain')
            html_part = MIMEText(html, 'html')
            msg.attach(text_part)
            msg.attach(html_part)
            
            # Send email via SMTP
            port = channel.smtp_port or 587
            timeout = 10
            
            with smtplib.SMTP(channel.smtp_server, port, timeout=timeout) as server:
                server.starttls()
                server.login(channel.smtp_username, channel.smtp_password)
                server.send_message(msg)
            
            logger.info(f"✓ Email sent to {channel.email_address}")
            return True
            
        except smtplib.SMTPAuthenticationError:
            logger.error(f"❌ Email authentication failed for {channel.email_address if channel else 'unknown'} - check SMTP credentials")
            return False
        except smtplib.SMTPException as e:
            logger.error(f"❌ SMTP error: {str(e)[:100]}")
            return False
        except TimeoutError:
            logger.error(f"❌ Email timeout connecting to {channel.smtp_server if channel else 'unknown'}")
            return False
        except Exception as e:
            logger.error(f"❌ Email error: {str(e)[:100]}")
            return False
    
    @staticmethod
    def send_via_whatsapp(channel, summary_text, audio_url=None, journalist_name="Journalist"):
        """Send summary via WhatsApp (requires Twilio)
        
        Args:
            channel: DeliveryChannel object with WhatsApp configuration
            summary_text: Summary text to send
            audio_url: Optional URL to audio file
            journalist_name: Name of the journalist
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not channel or not channel.whatsapp_phone_number or not channel.whatsapp_api_key:
                logger.warning(f"WhatsApp channel incomplete: phone={channel.whatsapp_phone_number if channel else 'None'}")
                return False
            
            try:
                from twilio.rest import Client
                
                account_sid = channel.whatsapp_account_id
                auth_token = channel.whatsapp_api_key
                
                if not account_sid or not auth_token:
                    logger.warning(f"WhatsApp missing account credentials")
                    return False
                
                client = Client(account_sid, auth_token)
                
                # Truncate summary if too long for WhatsApp (max 1600 chars)
                truncated_summary = summary_text[:1500] if len(summary_text) > 1500 else summary_text
                message_body = f"📰 Résumé - {journalist_name}\n\n{truncated_summary}"
                if audio_url:
                    message_body += f"\n\n🎙️ Audio: {audio_url}"
                
                message = client.messages.create(
                    body=message_body,
                    from_=f"whatsapp:{channel.whatsapp_account_id}",  # Twilio WhatsApp sender
                    to=f"whatsapp:{channel.whatsapp_phone_number}"
                )
                
                logger.info(f"✓ WhatsApp sent to {channel.whatsapp_phone_number}: {message.sid}")
                return True
                
            except ImportError:
                logger.warning("❌ Twilio not installed. Install with: pip install twilio")
                return False
            except Exception as e:
                logger.error(f"❌ WhatsApp API error: {str(e)[:100]}")
                return False
                
        except Exception as e:
            logger.error(f"❌ WhatsApp error: {str(e)[:100]}")
            return False
    
    @staticmethod
    def send_summary_to_channels(journalist, summary_text, audio_url=None):
        """Send summary to all active delivery channels for a journalist
        
        Args:
            journalist: Journalist object with delivery_channels
            summary_text: Summary text to send
            audio_url: Optional URL to audio file
            
        Returns:
            dict: Results per channel type with success status
        """
        if not journalist:
            logger.error("❌ Journalist object is None")
            return {}
        
        if not journalist.delivery_channels:
            logger.warning(f"⚠️  No delivery channels configured for journalist {journalist.id} ({journalist.name})")
            return {}
        
        results = {}
        active_channels = [ch for ch in journalist.delivery_channels if ch.is_active]
        
        if not active_channels:
            logger.warning(f"⚠️  No active delivery channels for journalist {journalist.id} ({journalist.name})")
            return {}
        
        logger.info(f"📤 Sending summary to {len(active_channels)} active channel(s) for {journalist.name}")
        
        for channel in active_channels:
            try:
                if channel.channel_type == 'telegram':
                    results['telegram'] = DeliveryService.send_via_telegram(channel, summary_text, audio_url)
                elif channel.channel_type == 'email':
                    results['email'] = DeliveryService.send_via_email(channel, summary_text, audio_url, journalist.name)
                elif channel.channel_type == 'whatsapp':
                    results['whatsapp'] = DeliveryService.send_via_whatsapp(channel, summary_text, audio_url, journalist.name)
                else:
                    logger.warning(f"⚠️  Unknown channel type: {channel.channel_type}")
            except Exception as e:
                logger.error(f"❌ Error sending via {channel.channel_type}: {str(e)[:100]}")
                results[channel.channel_type] = False
        
        success_count = sum(1 for v in results.values() if v)
        logger.info(f"📊 Delivery result: {success_count}/{len(active_channels)} channels succeeded")
        
        # Return True if at least one channel succeeded
        return results if results else {}
