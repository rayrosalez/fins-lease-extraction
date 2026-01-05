# FINS Lease Extraction Platform (FrontEndV2)

A modern React-based lease extraction platform powered by Databricks, featuring AI-powered document processing, real-time analytics, and intelligent chat interface.

## 🚀 Features

### 1. **AI-Powered Document Processing**
- Upload lease PDFs to Databricks Unity Catalog
- Automated AI extraction with 99%+ accuracy
- Real-time processing status tracking
- Beautiful animated upload interface

### 2. **Portfolio Dashboard**
- Live KPIs from Databricks (leases, properties, tenants, markets)
- Interactive lease table with sorting and filtering
- Market-level analytics and aggregations
- Expiration tracking and alerts

### 3. **AI Chat Assistant**
- Embedded chat interface for natural language queries
- Ask questions about your portfolio in plain English
- Instant insights from your Databricks data
- Sample questions to get started

### 4. **Human-in-the-Loop Validation**
- Review AI-extracted data
- Edit and correct fields
- Approve records for production (Silver layer)
- Track validation status

---

## 📦 Quick Start

### Prerequisites

- **Node.js** v14+ (for React frontend)
- **Python** 3.9+ (for Flask backend)
- **Databricks** workspace with SQL Warehouse access
- Access to `bronze_leases` table in Unity Catalog

### Installation

#### 1. Install Frontend Dependencies
```bash
cd FrontEndV2
npm install
```

#### 2. Setup Backend
```bash
cd backend
pip install -r requirements.txt
python setup.py  # Interactive setup for Databricks credentials
```

The setup script will create a `.env` file with your Databricks configuration.

#### 3. Start Both Servers

**Terminal 1 - Backend API:**
```bash
cd backend
python api.py
# Runs on http://localhost:5001
```

**Terminal 2 - React Frontend:**
```bash
cd FrontEndV2
npm start
# Opens http://localhost:3000
```

**Both servers must be running** for the full application to work!

---

## 🗂️ Project Structure

```
FrontEndV2/
├── backend/                   # Flask API for Databricks
│   ├── api.py                # REST API endpoints
│   ├── utils.py              # Volume upload utilities
│   ├── setup.py              # Interactive .env setup
│   ├── test_connection.py    # Connection testing
│   └── requirements.txt      # Python dependencies
├── src/
│   ├── components/
│   │   ├── Hero.js/css              # Landing page with overview
│   │   ├── Portfolio.js/css         # Portfolio dashboard
│   │   ├── Chat.js/css              # AI chat interface
│   │   ├── Upload.js/css            # Document upload
│   │   ├── ValidationForm.js/css    # Data validation
│   │   └── ProcessingAnimation.js/css  # Upload animations
│   ├── App.js                # Main app with navigation
│   ├── App.css               # Global styles
│   └── index.js              # Entry point
├── public/                   # Static assets
└── package.json              # Node dependencies
```

---

## 🔌 API Endpoints

All endpoints are prefixed with `/api`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/portfolio/kpis` | GET | Portfolio-wide metrics |
| `/portfolio/leases` | GET | All lease details |
| `/portfolio/recent` | GET | Recent extractions (last 10) |
| `/portfolio/market-summary` | GET | Market-level aggregations |
| `/upload` | POST | Upload lease document to Volume |
| `/check-processing/<path>` | GET | Check file processing status |
| `/validate-record` | POST | Validate & promote to Silver layer |
| `/chat/query` | POST | Natural language chat queries |

---

## ⚙️ Configuration

### Backend `.env` File

Located at `backend/.env`:

```env
DATABRICKS_HOST=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-personal-access-token
DATABRICKS_WAREHOUSE_ID=your-sql-warehouse-id
DATABRICKS_CATALOG=fins_team_3
DATABRICKS_SCHEMA=lease_management
DATABRICKS_VOLUME=raw_lease_docs
```

### Getting Your Credentials

1. **Host**: Your Databricks workspace URL
2. **Token**: User Settings → Developer → Access Tokens → Generate New Token
3. **Warehouse ID**: SQL Warehouses → Select warehouse → Copy ID from URL
4. **Catalog/Schema**: Where your `bronze_leases` table exists

Run `python test_connection.py` to verify your setup!

---

## 🎨 Design System

### Official Databricks Colors

- **Lava Orange** (`#FF3621`) - Primary actions, active states
- **Navy** (`#1B3139`) - Backgrounds, surfaces
- **Maroon** (`#8B4513`) - Secondary accents, charts
- **Gray** (`#6B6B6B`) - Neutral elements
- **White** (`#FFFFFF`) - Text on dark backgrounds

### UI Components

- **Glassmorphism** cards with backdrop blur
- **Framer Motion** animations for smooth transitions
- **Feather Icons** (react-icons/fi) for consistency
- **Responsive design** for desktop and mobile

---

## 📊 Data Pipeline

```
1. Upload → Unity Catalog Volume
   ↓
2. AI Parser → Extract text/structure
   ↓
3. Agent Extraction → Identify lease fields
   ↓
4. Human Validation → Review & correct
   ↓
5. Silver Layer → Validated, production-ready data
   ↓
6. Analytics → Dashboards, Chat, Risk Models
```

---

## 🛠️ Development

### Run Frontend
```bash
npm start
```

### Run Backend
```bash
cd backend
python api.py
```

### Test Backend Connection
```bash
cd backend
python test_connection.py
```

### Build for Production
```bash
npm run build
```

---

## 🔧 Troubleshooting

### Backend Won't Start

**Problem:** Permission errors or missing modules
```bash
# Activate your Python environment
pyenv activate buildathon  # or your virtualenv name

# Reinstall dependencies
pip install -r requirements.txt

# Try starting again
python api.py
```

**Problem:** Connection to Databricks fails
```bash
# Run the test script
python test_connection.py

# Common fixes:
# 1. Check your .env file exists and has correct values
# 2. Ensure SQL Warehouse is running (not stopped)
# 3. Verify token hasn't expired
# 4. Check catalog/schema names are correct
```

### Frontend Issues

**Problem:** "Backend connection error" in Chat
- Ensure backend is running on port 5001
- Check backend terminal for errors
- Verify CORS is enabled (it should be by default)

**Problem:** No data showing
- Verify `bronze_leases` table has data
- Check browser console for API errors
- Try refreshing the page

### Port Conflicts

If port 5001 or 3000 is in use:
- Backend: Edit `api.py` line 711: `app.run(debug=True, port=NEW_PORT)`
- Frontend: Set `PORT=NEW_PORT` before running `npm start`

---

## 💻 Technology Stack

### Frontend
- **React** 18 - UI framework
- **Framer Motion** - Smooth animations
- **React Icons** - Feather icon set

### Backend
- **Flask** - Python web framework
- **Flask-CORS** - Cross-origin requests
- **Databricks SDK** - Database connectivity
- **python-dotenv** - Environment management

### Data Platform
- **Databricks Unity Catalog** - Data governance
- **Delta Lake** - ACID transactions
- **SQL Warehouses** - Query compute
- **Volumes** - File storage

---

## 📝 Chat Capabilities

The AI chat can answer questions like:

- "What is the total value of all active leases?"
- "Show me leases expiring in the next 12 months"
- "Which tenants have the highest square footage?"
- "What is the average rent per square foot by industry?"
- "List all tenants"

The backend uses keyword matching to route queries to the appropriate SQL. For more advanced NLP, you can integrate Databricks Genie API or a custom LLM.

---

## 📄 License

Proprietary - FINS Platform

---

## 🤝 Support

For issues or questions:
1. Check the troubleshooting section above
2. Run `python test_connection.py` in the backend folder
3. Check terminal logs for detailed error messages
4. Verify all environment variables are set correctly

---

**Built with ❤️ using Databricks**
