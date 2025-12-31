# FINS Lease Extraction Platform - Project Summary

## Overview

A complete lease document processing platform built with React and Databricks, featuring:
- AI-powered document extraction
- Real-time portfolio analytics
- Natural language chat interface
- Human-in-the-loop validation workflow

---

## Architecture

### Frontend (React)
- **Framework**: React 18
- **Styling**: Custom CSS with Databricks design system
- **Animations**: Framer Motion
- **Icons**: Feather Icons (react-icons/fi)
- **Port**: 3000

### Backend (Flask API)
- **Framework**: Flask + Flask-CORS
- **Database**: Databricks Unity Catalog via SDK
- **Port**: 5001

### Data Platform (Databricks)
- **Storage**: Unity Catalog Volumes
- **Tables**: Bronze (raw extractions), Silver (validated)
- **Compute**: SQL Warehouses
- **AI**: Agent framework for extraction

---

## File Structure

```
FrontEndV2/
├── src/
│   ├── components/
│   │   ├── Hero.js/css           # Landing page with KPIs
│   │   ├── Portfolio.js/css      # Full portfolio table view
│   │   ├── Chat.js/css           # AI chat interface
│   │   ├── Upload.js/css         # Document upload workflow
│   │   ├── ValidationForm.js/css # Data validation form
│   │   └── ProcessingAnimation.js/css # Upload progress animation
│   ├── App.js                    # Main app with navigation
│   ├── App.css                   # Global styles
│   └── index.js                  # React entry point
├── backend/
│   ├── api.py                    # REST API (9 endpoints)
│   ├── utils.py                  # Volume upload helper
│   ├── setup.py                  # Interactive config tool
│   ├── test_connection.py        # Connection testing
│   └── requirements.txt          # Python deps
├── public/                       # Static assets
├── package.json                  # Node deps
└── README.md                     # Main documentation
```

---

## Components

### 1. Hero (Landing Page)
- **Purpose**: Welcome screen and quick stats
- **Features**:
  - Portfolio KPIs (leases, properties, tenants, markets)
  - Recent extractions list
  - Quick navigation cards
  - Market summary table
- **API Calls**: 
  - `/api/portfolio/kpis`
  - `/api/portfolio/recent`
  - `/api/portfolio/market-summary`

### 2. Portfolio (Dashboard)
- **Purpose**: Complete portfolio view
- **Features**:
  - Searchable/sortable lease table
  - All lease details (tenant, dates, rent, etc.)
  - Real-time data from bronze_leases
- **API Calls**: `/api/portfolio/leases`

### 3. Chat (AI Assistant)
- **Purpose**: Natural language queries
- **Features**:
  - Message-based interface
  - Sample questions
  - Keyword-based query routing
  - Structured data responses
- **API Calls**: `/api/chat/query`
- **Capabilities**:
  - Total portfolio value
  - Expiring leases (6/12/24 months)
  - Largest tenants by sqft
  - Average rent by industry
  - Tenant listings

### 4. Upload (Document Processing)
- **Purpose**: Upload and extract PDFs
- **Features**:
  - Drag & drop file upload
  - Multi-stage processing animation
  - Real-time status polling
  - Timeout handling
- **API Calls**:
  - `/api/upload` (POST file)
  - `/api/check-processing` (poll status)

### 5. ValidationForm
- **Purpose**: Review and correct AI extractions
- **Features**:
  - 14 lease fields with icons
  - Required field validation
  - User-added field tracking
  - AI confidence display
- **API Calls**: `/api/validate-record` (promote to Silver)

### 6. ProcessingAnimation
- **Purpose**: Visual feedback during extraction
- **Features**:
  - 4-stage animation (Upload → Parse → Extract → Validate)
  - Smooth transitions
  - Stage-specific messaging

---

## API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/health` | GET | Health check |
| `/api/portfolio/kpis` | GET | Portfolio metrics |
| `/api/portfolio/leases` | GET | All leases |
| `/api/portfolio/recent` | GET | Recent extractions |
| `/api/portfolio/market-summary` | GET | Market aggregations |
| `/api/upload` | POST | Upload PDF to Volume |
| `/api/check-processing/<path>` | GET | Check extraction status |
| `/api/validate-record` | POST | Validate & promote to Silver |
| `/api/chat/query` | POST | Natural language queries |

---

## Data Flow

### Upload → Extraction → Validation

```
1. User uploads PDF
   ↓
2. API saves to Unity Catalog Volume
   ↓
3. Databricks job ingests to raw_leases table
   ↓
4. AI agent extracts fields to bronze_leases
   ↓
5. Frontend polls for completion
   ↓
6. User validates/corrects data
   ↓
7. API promotes to silver_leases
   ↓
8. Data available in all views
```

### Chat Queries

```
1. User types question
   ↓
2. Frontend sends to /api/chat/query
   ↓
3. Backend matches keywords
   ↓
4. SQL query executed on bronze_leases
   ↓
5. Results formatted as natural language
   ↓
6. Response + data returned to UI
```

---

## Design System

### Colors
- **Primary**: #FF3621 (Lava Orange)
- **Background**: #1B3139 (Navy)
- **Secondary**: #8B4513 (Maroon)
- **Neutral**: #6B6B6B (Gray)
- **Text**: #FFFFFF (White)

### Typography
- **Headings**: 700 weight, white
- **Body**: 400 weight, rgba(255,255,255,0.9)
- **Subtle**: rgba(255,255,255,0.6)

### Components
- **Cards**: Glassmorphism with `backdrop-filter: blur(20px)`
- **Borders**: `rgba(255,255,255,0.1)`
- **Hover**: Orange tint + transform
- **Focus**: Orange glow

---

## Environment Setup

### Required Variables

```env
DATABRICKS_HOST=https://workspace.cloud.databricks.com
DATABRICKS_TOKEN=dapi...
DATABRICKS_WAREHOUSE_ID=abc123...
DATABRICKS_CATALOG=fins_team_3
DATABRICKS_SCHEMA=lease_management
DATABRICKS_VOLUME=raw_lease_docs
```

### Database Schema

**bronze_leases** (AI extractions):
- extraction_id (primary key)
- landlord_name, tenant_name, industry_sector
- commencement_date, expiration_date, term_months
- rentable_square_feet, annual_base_rent, base_rent_psf
- annual_escalation_pct, renewal_notice_days, guarantor
- validation_status, extracted_at

**silver_leases** (validated):
- lease_id, property_id, tenant_name
- square_footage, lease_start_date, lease_end_date
- base_rent_psf, estimated_annual_rent
- validation_status, verified_by, verified_at

---

## Running the Application

### Development Mode

**Terminal 1 - Backend:**
```bash
cd FrontEndV2/backend
python api.py
```

**Terminal 2 - Frontend:**
```bash
cd FrontEndV2
npm start
```

**Both must run simultaneously!**

### Production Build

```bash
cd FrontEndV2
npm run build
# Outputs to /build directory
```

---

## Key Features Implemented

✅ Document upload to Unity Catalog Volumes  
✅ Real-time processing status with animations  
✅ Human-in-the-loop validation workflow  
✅ Bronze → Silver data promotion  
✅ Portfolio dashboard with live data  
✅ Natural language chat interface  
✅ Market-level analytics  
✅ Responsive design (mobile + desktop)  
✅ Error handling and timeout management  
✅ Databricks design system compliance  

---

## Testing

### Backend Connection Test
```bash
cd backend
python test_connection.py
```

Verifies:
- Environment variables set
- Databricks connection works
- SQL Warehouse accessible
- Tables exist and have data

### Manual Testing Checklist

1. **Upload Flow**
   - [ ] Upload PDF successfully
   - [ ] See processing animation
   - [ ] Validation form appears
   - [ ] Submit validation
   - [ ] See success message

2. **Portfolio View**
   - [ ] See list of all leases
   - [ ] Search works
   - [ ] Sorting works
   - [ ] Data displays correctly

3. **Chat Interface**
   - [ ] Message sent successfully
   - [ ] Response received
   - [ ] Sample questions work
   - [ ] Typing indicator shows

4. **Hero Page**
   - [ ] KPIs load
   - [ ] Recent extractions show
   - [ ] Market summary displays
   - [ ] Navigation cards work

---

## Common Issues & Solutions

### "Backend connection error"
- Ensure backend is running on port 5001
- Check backend terminal for errors
- Verify .env file exists and is correct

### "Processing timeout"
- File uploaded successfully but extraction taking >4 min
- Check Portfolio page after a few minutes
- Verify Databricks jobs are running

### "No data showing"
- Ensure bronze_leases table has data
- Check browser console for API errors
- Verify SQL Warehouse is running (not stopped)

### "Permission denied" errors
- Activate proper Python environment
- Run: `pip install -r requirements.txt`
- Check Databricks token hasn't expired

---

## Future Enhancements

- [ ] Integrate Databricks Genie API for advanced NLP
- [ ] Add export functionality (Excel, CSV)
- [ ] Batch upload multiple PDFs
- [ ] Advanced filtering and saved views
- [ ] Real-time notifications via WebSocket
- [ ] Risk scoring visualization
- [ ] Document comparison tool
- [ ] Historical trend analysis

---

## Technology Stack

**Frontend**: React 18, Framer Motion, Feather Icons  
**Backend**: Flask, Databricks SDK, python-dotenv  
**Data**: Unity Catalog, Delta Lake, SQL Warehouses  
**AI**: Databricks Agent Framework  

---

**Built with ❤️ for FINS Platform**

