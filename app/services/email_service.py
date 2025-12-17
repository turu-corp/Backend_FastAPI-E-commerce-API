from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from app.config import settings
from typing import List
import logging

logger = logging.getLogger(__name__)

# Email configuration
conf = ConnectionConfig(
    MAIL_USERNAME=settings.MAIL_USERNAME,
    MAIL_PASSWORD=settings.MAIL_PASSWORD,
    MAIL_FROM=settings.MAIL_FROM,
    MAIL_PORT=settings.MAIL_PORT,
    MAIL_SERVER=settings.MAIL_SERVER,
    MAIL_STARTTLS=settings.MAIL_STARTTLS,
    MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True
)


class EmailService:
    """Service for sending emails(workflow automation)"""
    
    @staticmethod
    async def send_welcome_email(email: str, name: str):
        """
        Send welcome email after registration (workflow automation)
        """
        try:
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; border-radius: 8px; padding: 30px;">
                        <h1 style="color: #2563eb;">Welcome to {settings.APP_NAME}! 🎉</h1>
                        <p>Hi <strong>{name}</strong>,</p>
                        <p>Thank you for registering with us! We're excited to have you on board.</p>
                        <p>You can now:</p>
                        <ul>
                            <li>Browse our amazing products</li>
                            <li>Add items to your cart</li>
                            <li>Place orders and track shipments</li>
                            <li>Write reviews for products</li>
                        </ul>
                        <p style="margin-top: 30px;">Happy shopping!</p>
                        <p style="color: #666; font-size: 12px; margin-top: 40px;">
                            This is an automated email. Please do not reply to this message.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            message = MessageSchema(
                subject=f"Welcome to {settings.APP_NAME}!",
                recipients=[email],
                body=html,
                subtype="html"
            )
            
            fm = FastMail(conf)
            await fm.send_message(message)
            logger.info(f"Welcome email sent to {email}")
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {email}: {str(e)}")
            # Don't raise exception - email failure shouldn't break registration
    
    @staticmethod
    async def send_order_confirmation(email: str, name: str, order_id: str, total_price: int):
        """
        Send confirmation email for order (workflow automation)
        """
        try:
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; border-radius: 8px; padding: 30px;">
                        <h1 style="color: #2563eb;">Order Confirmed! ✅</h1>
                        <p>Hi <strong>{name}</strong>,</p>
                        <p>Thank you for your order! We've received your payment and are processing your order.</p>
                        
                        <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                            <h3 style="margin-top: 0;">Order Details</h3>
                            <p><strong>Order ID:</strong> {order_id}</p>
                            <p><strong>Total Amount:</strong> Rp {total_price:,}</p>
                        </div>
                        
                        <p>You will receive another email once your order has been shipped.</p>
                        <p style="margin-top: 30px;">Thank you for shopping with us!</p>
                        
                        <p style="color: #666; font-size: 12px; margin-top: 40px;">
                            This is an automated email. Please do not reply to this message.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            message = MessageSchema(
                subject=f"Order Confirmation - {order_id}",
                recipients=[email],
                body=html,
                subtype="html"
            )
            
            fm = FastMail(conf)
            await fm.send_message(message)
            logger.info(f"Order confirmation email sent to {email}")
            
        except Exception as e:
            logger.error(f"Failed to send order confirmation to {email}: {str(e)}")
    
    @staticmethod
    async def send_password_reset(email: str, name: str, reset_token: str):
        """
        Send reset password email (workflow automation)
        """
        try:
            reset_link = f"https://yourwebsite.com/reset-password?token={reset_token}"
            
            html = f"""
            <html>
                <body style="font-family: Arial, sans-serif; padding: 20px;">
                    <div style="max-width: 600px; margin: 0 auto; border: 1px solid #ddd; border-radius: 8px; padding: 30px;">
                        <h1 style="color: #2563eb;">Password Reset Request 🔐</h1>
                        <p>Hi <strong>{name}</strong>,</p>
                        <p>We received a request to reset your password. Click the button below to create a new password:</p>
                        
                        <div style="text-align: center; margin: 30px 0;">
                            <a href="{reset_link}" 
                               style="background-color: #2563eb; color: white; padding: 12px 30px; 
                                      text-decoration: none; border-radius: 5px; display: inline-block;">
                                Reset Password
                            </a>
                        </div>
                        
                        <p>If you didn't request this, please ignore this email.</p>
                        <p style="color: #999; font-size: 12px;">This link will expire in 1 hour.</p>
                        
                        <p style="color: #666; font-size: 12px; margin-top: 40px;">
                            This is an automated email. Please do not reply to this message.
                        </p>
                    </div>
                </body>
            </html>
            """
            
            message = MessageSchema(
                subject="Password Reset Request",
                recipients=[email],
                body=html,
                subtype="html"
            )
            
            fm = FastMail(conf)
            await fm.send_message(message)
            logger.info(f"Password reset email sent to {email}")
            
        except Exception as e:
            logger.error(f"Failed to send password reset email to {email}: {str(e)}")