# 🎬 18+ Video Streaming Website

A secure video streaming platform with YouTube-style UI and Telegram bot authentication.

## ✨ Features

### 🎨 Frontend
- **YouTube-inspired UI** - Dark theme (#0f0f0f) with modern design
- **Responsive Design** - Works on all devices
- **Video Categories** - Entertainment, Education, Music, Sports, News, Technology
- **16:9 Thumbnails** - Professional video presentation
- **Modal Video Player** - Clean, distraction-free viewing

### 🔐 Security
- **Telegram Bot Authentication** - Keys generated only via Telegram
- **No Traditional Login** - No username/password vulnerability
- **Authorized Access Only** - Single Chat ID authorization
- **Auto-Key Invalidation** - Old keys destroyed on new key creation
- **Hidden Admin Panel** - Not linked publicly, secret URL only
- **32-Character Keys** - Cryptographically secure

### 🤖 Telegram Bot (@pluseight_bot)
- `/start` - Welcome and instructions
- `/help` - Detailed usage guide
- `/createkey` - Generate new access key
- `/currentkey` - View active key
- **24/7 Online** - Always available for key generation

## 🚀 Quick Start (Local Development)

### Prerequisites
- Python 3.11+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd VideoStreamingSite
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Initialize storage**
   ```bash
   python init_storage.py
   ```

4. **Run the application**
   ```bash
   # Start both services
   ./start_all.ps1

   # Or start individually:
   # Terminal 1: python web_server.py
   # Terminal 2: python telegram_bot.py
   ```

5. **Access the website**
   - Home: http://localhost:8000
   - Admin: http://localhost:8000/parking55009hvSweJimbs5hhinbd56y

## 🌐 Deployment on Render.com

### Complete deployment guide: [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md)

**Quick Deploy:**
1. Push code to GitHub
2. Create Web Service on Render.com
3. Create Background Worker for Telegram bot
4. Set environment variables
5. Deploy! 🚀

## 📁 Project Structure

```
VideoStreamingSite/
├── index.html                          # Home page
├── parking55009hvSweJimbs5hhinbd56y.html  # Admin login (key-only)
├── admin/
│   └── dashboard.html                  # Admin dashboard
├── css/
│   └── style.css                       # YouTube-style CSS
├── js/
│   ├── main.js                         # Frontend logic
│   └── admin.js                        # Admin panel logic
├── web_server.py                       # Production web server
├── telegram_bot.py                     # Telegram bot (24/7)
├── init_storage.py                     # Storage initialization
├── key_storage.json                    # Shared key storage
├── requirements.txt                    # Python dependencies
├── runtime.txt                         # Python version
├── Procfile                            # Process definitions
├── render.yaml                         # Render.com config
├── .env.example                        # Environment template
├── .gitignore                          # Git ignore rules
├── RENDER_DEPLOYMENT_GUIDE.md          # Deployment guide
└── README.md                           # This file
```

## 🔧 Configuration

### Environment Variables

**Web Service:**
```env
PYTHON_VERSION=3.11.0
PORT=10000
```

**Telegram Bot:**
```env
BOT_TOKEN=your_bot_token_here
AUTHORIZED_CHAT_ID=your_chat_id_here
PYTHON_VERSION=3.11.0
```

### Bot Configuration
- **Bot:** @pluseight_bot
- **Token:** Set in environment variables
- **Authorized Chat ID:** 2103408372 (set in env vars)

## 🎯 How It Works

### Authentication Flow
1. Admin sends `/createkey` to Telegram bot
2. Bot generates 32-character secure key
3. Bot saves key to `key_storage.json`
4. Admin copies key from Telegram
5. Admin visits secret URL and pastes key
6. Website validates key from `key_storage.json`
7. Access granted! ✅

### Key Features
- **Single Active Key** - Only one valid key at a time
- **Instant Invalidation** - New key destroys old one
- **No Reset Option** - Keys only via Telegram
- **Authorized Only** - One Chat ID can generate keys

## 🛡️ Security Measures

1. **Hidden Admin URL** - Not linked anywhere publicly
2. **Telegram-Only Key Generation** - No web interface
3. **Single Authorization** - Only your Chat ID works
4. **Secure Key Generation** - Cryptographically random
5. **No Session Persistence** - Keys required each time
6. **Auto-Invalidation** - Old keys become useless

## 📱 Using the Telegram Bot

### First Time Setup
```
You: /start
Bot: Welcome! Here's how to use me...

You: /createkey
Bot: ✅ New Access Key Generated!
     🔑 [32-character-key-here]
     
     Copy this key and use it to login!
```

### Checking Current Key
```
You: /currentkey
Bot: 🔑 Current Active Key
     [your-active-key]
     
     🕒 Created: 2026-01-19 22:00:00
```

## 🎨 Customization

### Change Theme Colors
Edit `css/style.css`:
```css
body {
    background-color: #0f0f0f; /* Change background */
    color: #ffffff; /* Change text color */
}
```

### Add Video Categories
Edit `admin/dashboard.html`:
```html
<option value="your-category">Your Category</option>
```

### Modify 18+ Logo
Edit `index.html` and other pages:
```html
<h1><span class="age-badge">18+</span> 18+ only</h1>
```

## 🐛 Troubleshooting

### Bot Not Responding?
1. Check if bot token is correct
2. Verify bot is running (check logs)
3. Restart the bot service

### Can't Login?
1. Generate new key: `/createkey`
2. Check `key_storage.json` exists
3. Verify you're using the secret URL

### Videos Not Showing?
1. Upload videos via admin panel
2. Check localStorage in browser
3. Clear browser cache and retry

## 📊 Tech Stack

- **Frontend:** HTML5, CSS3, JavaScript (Vanilla)
- **Backend:** Python 3.11+
- **Web Server:** Python http.server (production-ready)
- **Bot Framework:** python-telegram-bot
- **Storage:** JSON file (localStorage + file system)
- **Hosting:** Render.com (optimized)

## 🔄 Updates & Maintenance

### Update Bot Token
1. Edit environment variables in Render dashboard
2. Restart the background worker
3. Test with `/start` command

### Add New Features
1. Modify code locally
2. Test thoroughly
3. Commit and push to GitHub
4. Render auto-deploys changes

## 📄 License

Private project - All rights reserved

## 👤 Admin Access

- **Admin URL:** `https://your-site.onrender.com/parking55009hvSweJimbs5hhinbd56y`
- **Key Generation:** Via @pluseight_bot on Telegram
- **Authorized User:** Chat ID 2103408372

## 🎉 Credits

- **YouTube-inspired Design**
- **Secure Telegram Integration**
- **Production-Ready Deployment**

---

**Status:** ✅ Production Ready  
**Deployment:** Render.com Optimized  
**Bot:** @pluseight_bot (24/7 Online)  
**Last Updated:** January 2026

---

## 📞 Support

For issues or questions:
1. Check [RENDER_DEPLOYMENT_GUIDE.md](RENDER_DEPLOYMENT_GUIDE.md)
2. Review Render.com logs
3. Test Telegram bot connectivity
4. Verify environment variables

**Happy Streaming! 🎬**
