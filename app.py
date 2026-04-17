from flask import Flask, render_template, request, jsonify
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
from dotenv import load_dotenv
import datetime
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_wtf.csrf import CSRFProtect
import atexit
from apscheduler.schedulers.background import BackgroundScheduler

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'crownbee-secret-key-change-this')

# Email Configuration
SMTP_SERVER = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
EMAIL_ADDRESS = os.getenv('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.getenv('EMAIL_PASSWORD')
ADMIN_EMAIL = os.getenv('ADMIN_EMAIL', EMAIL_ADDRESS)
FAILED_EMAILS_FILE = 'failed_emails.json'
ADMIN_PASSWORD = os.getenv('ADMIN_PASSWORD', 'crownbee2026')

# Security
csrf = CSRFProtect()
csrf.init_app(app)

# Rate Limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)


def save_failed_email(name, email, phone, service, message, error):
    """Save failed email to local file as backup"""
    try:
        failed_emails = []
        if os.path.exists(FAILED_EMAILS_FILE):
            with open(FAILED_EMAILS_FILE, 'r') as f:
                failed_emails = json.load(f)

        failed_emails.append({
            'id': len(failed_emails) + 1,
            'timestamp': datetime.datetime.now().isoformat(),
            'name': name,
            'email': email,
            'phone': phone,
            'service': service,
            'message': message,
            'error': str(error),
            'retry_count': 0,
            'status': 'pending'
        })

        with open(FAILED_EMAILS_FILE, 'w') as f:
            json.dump(failed_emails, f, indent=2)

        return True
    except Exception as e:
        print(f"Could not save failed email: {e}")
        return False


def send_admin_notification(name, email, phone, service, message):
    """Send notification email to admin"""
    try:
        print(f"📧 ATTEMPTING to send admin notification...")
        print(f"   From: {EMAIL_ADDRESS}")
        print(f"   To: {ADMIN_EMAIL}")
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = ADMIN_EMAIL
        msg['Reply-To'] = email
        msg['Subject'] = f"👑 NEW LEAD: {name} - {service}"

        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'DM Sans', sans-serif; background: #0a0a0a; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #111111; border-radius: 15px; padding: 30px; border: 1px solid #D4A017; }}
                .header {{ background: linear-gradient(135deg, #D4A017, #C8102E); color: #0a0a0a; padding: 20px; border-radius: 10px; margin-bottom: 20px; }}
                .field {{ margin-bottom: 15px; }}
                .label {{ font-weight: bold; color: #D4A017; margin-bottom: 5px; }}
                .value {{ color: #e5e5e5; padding: 10px; background: #1a1a1a; border-radius: 5px; }}
                .footer {{ margin-top: 30px; color: #888; font-size: 12px; text-align: center; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin:0;">👑 CROWNBEE GLOBAL SERVICES</h2>
                    <p style="margin:5px 0 0;">🔔 New Lead Notification</p>
                </div>

                <div class="field">
                    <div class="label">📝 Full Name</div>
                    <div class="value">{name}</div>
                </div>

                <div class="field">
                    <div class="label">📧 Email Address</div>
                    <div class="value">{email}</div>
                </div>

                <div class="field">
                    <div class="label">📞 Phone Number</div>
                    <div class="value">{phone if phone else 'Not provided'}</div>
                </div>

                <div class="field">
                    <div class="label">🏢 Service Interested In</div>
                    <div class="value">{service}</div>
                </div>

                <div class="field">
                    <div class="label">💬 Message</div>
                    <div class="value" style="white-space: pre-line;">{message}</div>
                </div>

                <div class="footer">
                    Received on {datetime.datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}
                </div>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        return True
    except Exception as e:
        print(f"Admin notification error: {e}")
        save_failed_email(name, email, phone, service, message, e)
        return False


def send_auto_reply(user_email, name):
    """Send auto-reply email to the user"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = user_email
        msg['Subject'] = "Thank you for contacting Crownbee Global Services"

        body = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: 'DM Sans', sans-serif; background: #0a0a0a; padding: 20px; }}
                .container {{ max-width: 600px; margin: 0 auto; background: #111111; border-radius: 15px; padding: 30px; border: 1px solid #D4A017; }}
                .header {{ background: linear-gradient(135deg, #D4A017, #C8102E); color: #0a0a0a; padding: 20px; border-radius: 10px; text-align: center; }}
                .content {{ padding: 20px; }}
                .btn {{ background: #D4A017; color: #0a0a0a; padding: 12px 25px; text-decoration: none; border-radius: 40px; display: inline-block; margin-top: 20px; font-weight: 700; }}
                .footer {{ margin-top: 30px; color: #888; font-size: 12px; text-align: center; border-top: 1px solid #2a2a2a; padding-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2 style="margin:0;">👑 CROWNBEE GLOBAL SERVICES</h2>
                    <p style="margin:5px 0 0;">Luxury Real Estate · Wealth Legacy</p>
                </div>
                <div class="content">
                    <h3 style="color: #D4A017;">Hello {name}! 👋</h3>
                    <p>Thank you for reaching out to <strong>Crownbee Global Services Ltd</strong>.</p>
                    <p>We have received your message and one of our luxury real estate advisors will get back to you within <strong>24 hours</strong>.</p>

                    <div style="background: #1a1a1a; padding: 15px; border-radius: 10px; margin: 20px 0;">
                        <p style="margin: 5px 0;"><strong>📞 Need faster response?</strong></p>
                        <p style="margin: 5px 0;">Call or WhatsApp us directly:</p>
                        <p style="margin: 5px 0; font-size: 1.2rem; color: #D4A017;">09099997342 | 09010677777</p>
                    </div>

                    <p>In the meantime, feel free to:</p>
                    <ul style="margin-left: 20px; color: #ccc;">
                        <li>📱 Follow us on social media for updates</li>
                        <li>🌐 Browse our available properties on our website</li>
                        <li>📞 Call us for immediate assistance</li>
                    </ul>

                    <center>
                        <a href="https://wa.me/2349099997342" class="btn" style="color: #0a0a0a;">💬 Chat on WhatsApp</a>
                    </center>
                </div>
                <div class="footer">
                    Crownbee Global Services Ltd — Where every investment is a legacy<br>
                    © 2026 All Rights Reserved
                </div>
            </div>
        </body>
        </html>
        """

        msg.attach(MIMEText(body, 'html'))

        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)
        server.quit()

        print(f"✅ Admin notification SENT successfully to {ADMIN_EMAIL}")
        return True
    except Exception as e:
        print(f"Auto-reply error: {e}")
        return False


def retry_failed_emails():
    """Background job to retry failed emails"""
    print(f"[{datetime.datetime.now()}] Checking for failed emails to retry...")

    if not os.path.exists(FAILED_EMAILS_FILE):
        return

    try:
        with open(FAILED_EMAILS_FILE, 'r') as f:
            failed_emails = json.load(f)

        changed = False
        for entry in failed_emails:
            if entry.get('status') == 'pending' and entry.get('retry_count', 0) < 5:
                print(f"Retrying email for {entry['name']} (attempt {entry.get('retry_count', 0) + 1}/5)")
                entry['retry_count'] = entry.get('retry_count', 0) + 1
                changed = True

        if changed:
            with open(FAILED_EMAILS_FILE, 'w') as f:
                json.dump(failed_emails, f, indent=2)

    except Exception as e:
        print(f"Error in retry_failed_emails: {e}")


# Setup scheduler for retrying failed emails
scheduler = BackgroundScheduler()
scheduler.add_job(
    func=retry_failed_emails,
    trigger="interval",
    minutes=30,
    id="retry_failed_emails",
    replace_existing=True
)
scheduler.start()
atexit.register(lambda: scheduler.shutdown())

# Add this test route temporarily
@app.route('/test-email')
def test_email():
    result = send_admin_notification(
        "Test User",
        "test@example.com",
        "1234567890",
        "Test Service",
        "Test message"
    )
    return f"Email sent: {result}"

@app.route('/api/contact', methods=['POST'])
@limiter.limit("5 per minute")
def handle_contact():
    """Handle contact form submission"""
    try:
        data = request.json

        if not data.get('name') or not data.get('email') or not data.get('message'):
            return jsonify({
                'success': False,
                'message': 'Please fill in all required fields'
            }), 400

        name = data.get('name')
        user_email = data.get('email')
        phone = data.get('phone', '')
        service = data.get('service', 'General Inquiry')
        message = data.get('message')

        # Send notifications
        admin_sent = send_admin_notification(name, user_email, phone, service, message)
        auto_reply_sent = send_auto_reply(user_email, name)

        if admin_sent or auto_reply_sent:
            return jsonify({
                'success': True,
                'message': 'Thank you! We have received your message. A confirmation email has been sent to your inbox. We\'ll get back to you within 24 hours.'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Unable to send message. Please call us directly at 09099997342'
            }), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({
            'success': False,
            'message': 'Something went wrong. Please try again.'
        }), 500


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/property')
def properties():
    return render_template('properties.html')


@app.route('/service')
def services():
    return render_template('service.html')


if __name__ == '__main__':
    app.run(debug=True)