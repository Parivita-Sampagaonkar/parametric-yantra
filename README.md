# 🏛️ Parametric Yantra Generator v0.6

> Generate scientifically accurate astronomical instruments with modern parametric CAD

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Next.js 14](https://img.shields.io/badge/Next.js-14-black)](https://nextjs.org/)

## 🎯 What is This?

The Parametric Yantra Generator creates historically accurate astronomical instruments (yantras) from India's Jantar Mantar observatories, adapted to any location on Earth. Each yantra is:

- **Parametrically generated** based on latitude, longitude, and scale
- **Truth-checked** against modern ephemeris (JPL/IAU)
- **Fabrication-ready** with DXF, STL, STEP, and PDF exports
- **AR-enabled** for on-site alignment guidance

## ✨ Features (v0.6 - 60% Complete)

### ✅ Implemented
- ✅ **Samrat Yantra** (Equatorial Sundial) - Full parametric generation
- ✅ **Rama Yantra** (Alt-Azimuth Pillars) - Full parametric generation
- ✅ **Location picker** with famous sites and custom coordinates
- ✅ **Ephemeris validation** using Astropy & Skyfield
- ✅ **3D preview** with Three.js
- ✅ **CAD exports**: DXF, STL, GLTF, PDF with dimensions
- ✅ **Accuracy badges** (Excellent/Good/Acceptable/Poor)
- ✅ **REST API** with FastAPI
- ✅ **Database** (PostgreSQL + PostGIS)
- ✅ **Caching** (Redis)
- ✅ **Docker** containerization

### 🚧 Partial
- 🚧 AR alignment (UI ready, needs mobile sensors)
- 🚧 Time travel simulation (basic timeline)
- 🚧 Multi-language support (i18next configured)

### ❌ Not Yet Implemented
- ❌ 5 additional yantras (Digamsa, Dhruva-Praksha, etc.)
- ❌ Eclipse validation
- ❌ Collaborative mode (WebSockets)
- ❌ Citizen science platform
- ❌ VR Virtual Jantar Mantar
- ❌ AI-assisted recommendations
- ❌ Full security suite (Keycloak, audit logs)

## 🚀 Quick Start

### Prerequisites
```bash
# Required
- Docker & Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.12+ (for backend development)

# Optional
- PostgreSQL 15+ (if not using Docker)
- Redis 7+ (if not using Docker)
```

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/parametric-yantra.git
cd parametric-yantra
```

2. **Setup environment variables**
```bash
cp .env.example .env
# Edit .env with your configuration
```

3. **Start with Docker (Easiest)**
```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f backend
```

Services will be available at:
- 🌐 Frontend: http://localhost:3000
- 🔧 Backend API: http://localhost:8000
- 📚 API Docs: http://localhost:8000/docs
- 🗄️ Database UI: http://localhost:8080 (Adminer)
- 📦 MinIO Console: http://localhost:9001

4. **Or run manually**

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

## 📖 Usage

### 1. Select a Location
Choose from famous Jantar Mantar sites or enter custom coordinates:
- Jaipur Jantar Mantar (26.9124°N, 75.7873°E)
- Delhi Jantar Mantar (28.6273°N, 77.2167°E)
- Custom location with lat/lon

### 2. Configure Yantra
- **Type**: Samrat (equatorial) or Rama (alt-azimuth)
- **Scale**: 0.5m (desktop) to 10m (monument)
- **Material Thickness**: 3-50mm
- **Kerf Compensation**: 0-10mm for laser/CNC cutting

### 3. Generate
Click "Generate Yantra" to create:
- Parametric 3D geometry
- Dimensional drawings with tolerances
- Bill of materials
- Validation report (accuracy vs. ephemeris)

### 4. Export
Download fabrication files:
- **DXF**: For CAD software (AutoCAD, Fusion 360)
- **STL**: For 3D printing
- **GLTF**: For 3D visualization
- **PDF**: Dimensioned drawings with assembly instructions

### 5. Validate
Review accuracy metrics:
- Altitude error (degrees)
- Azimuth error (degrees)
- RMS error
- Accuracy level badge

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│           Next.js Frontend (Port 3000)       │
│  React + TypeScript + Three.js + Tailwind   │
└──────────────────┬──────────────────────────┘
                   │ REST API
┌──────────────────▼──────────────────────────┐
│        FastAPI Backend (Port 8000)           │
│  Python + Pydantic + Astropy + CadQuery     │
└──────────┬───────────────┬──────────────────┘
           │               │
    ┌──────▼──────┐ ┌─────▼──────┐
    │ PostgreSQL  │ │   Redis    │
    │  + PostGIS  │ │  (Cache)   │
    └─────────────┘ └────────────┘
           │
    ┌──────▼──────┐
    │  MinIO/R2   │
    │  (Storage)  │
    └─────────────┘
```

### Tech Stack

**Frontend:**
- Next.js 14 (React 18, TypeScript)
- Three.js + React-Three-Fiber (3D visualization)
- Zustand (state management)
- TanStack Query (data fetching)
- Tailwind CSS (styling)
- MapLibre GL JS (maps)

**Backend:**
- FastAPI (Python 3.12)
- Astropy & Skyfield (ephemeris)
- CadQuery (parametric CAD)
- ezdxf, trimesh, pygltflib (exports)
- ReportLab (PDF generation)
- SQLAlchemy + PostgreSQL + PostGIS
- Redis (caching)

**Infrastructure:**
- Docker & Docker Compose
- Cloudflare R2 / MinIO (storage)
- GitHub Actions (CI/CD)
- Sentry (error tracking)

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test
npm run test:e2e

# Security scans
docker run --rm -v $(pwd):/app aquasec/trivy fs /app
semgrep --config=auto .
```

## 📦 Deployment

### Option 1: Fly.io (Recommended - Free Tier)

```bash
# Install Fly CLI
curl -L https://fly.io/install.sh | sh

# Backend
cd backend
fly launch --name yantra-api
fly deploy

# Get database URL
fly postgres create --name yantra-db
fly postgres attach yantra-db

# Frontend on Cloudflare Pages
cd frontend
npm run build
npx wrangler pages deploy out/
```

### Option 2: Railway

1. Connect GitHub repository
2. Select `backend/` as root for API service
3. Add PostgreSQL addon
4. Deploy frontend separately or use monorepo setup

### Option 3: Self-Hosted (VPS)

```bash
# On your server
git clone <repo>
cd parametric-yantra
cp .env.example .env
# Edit .env with production values
docker-compose -f docker-compose.prod.yml up -d
```

## 🔒 Security

- JWT authentication with short-lived tokens
- CORS restricted to known origins
- Input validation (Pydantic + Zod)
- Rate limiting (Redis)
- Signed URLs for file downloads
- SQL injection protection (SQLAlchemy ORM)
- XSS protection (React escaping + CSP)
- HTTPS enforced in production
- Security headers (HSTS, X-Frame-Options)
- Regular dependency updates (Renovate)
- Automated security scans (Trivy, Semgrep)

## 🤝 Contributing

Contributions welcome! Please read [CONTRIBUTING.md](./CONTRIBUTING.md) first.

**Priority areas:**
1. Implementing remaining 5 yantras
2. Mobile app AR features
3. Collaborative mode (WebSockets + Yjs)
4. Citizen science platform
5. AI-assisted recommendations
6. VR mode

## 📄 License

MIT License - see [LICENSE](./LICENSE) file

## 🙏 Acknowledgments

- Based on the astronomical instruments at India's Jantar Mantar observatories
- Built with support from the Indian astronomical heritage community
- Ephemeris data from JPL/IAU
- Magnetic declination from NOAA WMM2020

## 📞 Support

- 📧 Email: support@yantra-generator.org
- 💬 Discord: [Join our community](https://discord.gg/yantra)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/parametric-yantra/issues)
- 📚 Docs: [Full Documentation](https://docs.yantra-generator.org)

---

**Built with ❤️ for preserving India's astronomical heritage**

*Astronomy • Mathematics • Engineering • Heritage*