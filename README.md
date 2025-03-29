# DevMons - Cryptocurrency Exchange Comparison Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Docker](https://img.shields.io/badge/Docker-Ready-brightgreen.svg)](https://www.docker.com/)
[![Vue.js](https://img.shields.io/badge/Vue.js-3.x-42b883.svg)](https://vuejs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.95+-009688.svg)](https://fastapi.tiangolo.com/)

## 📋 Overview

DevMons is a comprehensive cryptocurrency exchange comparison platform designed to help traders, investors, and enthusiasts make informed decisions by comparing cryptocurrency prices, fees, and features across multiple exchanges in real-time.

### 🚀 Key Features

- **Real-time Price Comparison**: Compare cryptocurrency prices across multiple exchanges simultaneously
- **Historical Price Analysis**: View and analyze historical price trends
- **Exchange Fee Comparison**: Compare trading fees, withdrawal fees, and other costs
- **Advanced Filtering**: Filter comparisons by exchange, cryptocurrency, or specific criteria
- **Responsive Design**: Seamless experience across desktop, tablet, and mobile devices
- **User-friendly Interface**: Clean, intuitive UI designed for both beginners and professional traders

## 🔧 Tech Stack

- **Frontend**:
  - Vue.js 3 with Composition API
  - TypeScript for type safety
  - Tailwind CSS for styling
  - Pinia for state management
  - Vue Router for navigation
  
- **Backend**:
  - FastAPI (Python) for RESTful API
  - PostgreSQL for data storage
  - Redis for caching
  
- **Infrastructure**:
  - Docker for containerization
  - Nginx for reverse proxy

## ⚙️ Prerequisites

- Docker and Docker Compose
- Git

## 🚀 Getting Started

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/GuzlejM/devmons.git
   cd devmons
   ```

2. Start all services using Docker Compose:
   ```bash
   docker compose up -d
   ```

3. Access the application:
   - Frontend: http://localhost
   - API Documentation: http://localhost:8000/docs

### Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/GuzlejM/devmons.git
   cd devmons
   ```

2. Start the development environment:
   ```bash
   # Start all services
   docker compose -f docker-compose.dev.yml up -d
   
   # For frontend development with hot-reloading
   cd crypto-exchange-frontend
   npm install
   npm run dev
   ```

3. Access development endpoints:
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 📊 Use Cases

### For Traders
- Compare current prices across exchanges to identify arbitrage opportunities
- Analyze fee structures to minimize trading costs
- Monitor market depth and liquidity across platforms

### For Investors
- Track historical performance of assets across exchanges
- Compare withdrawal fees for long-term storage strategies
- Identify exchanges with the best security features

### For Developers
- Access standardized data from multiple exchanges
- Build custom tools and integrations with the API
- Utilize Docker-based architecture for easy deployment and scaling

## 🔍 Project Structure

```
devmons/
├── crypto-exchange-frontend/    # Vue.js frontend
│   ├── public/                  # Static assets
│   │   ├── assets/              # Images, fonts, etc.
│   │   │   ├── src/                     # Source code
│   │   │   │   ├── components/          # Reusable Vue components
│   │   │   │   ├── stores/              # Pinia stores
│   │   │   │   ├── views/               # Page components
│   │   │   │   ├── router/              # Vue Router configuration
│   │   │   │   ├── types/               # TypeScript type definitions
│   │   │   │   ├── services/            # API services
│   │   │   │   ├── utils/               # Utility functions
│   │   │   │   ├── App.vue              # Root component
│   │   │   │   └── main.ts              # Application entry point
│   │   │   ├── Dockerfile               # Frontend Docker configuration
│   │   │   └── package.json             # Dependencies and scripts
│   │   ├── crypto_exchange_comparison/  # FastAPI backend
│   │   │   ├── api/                     # API endpoints
│   │   │   ├── core/                    # Core functionality
│   │   │   ├── db/                      # Database models and queries
│   │   │   ├── schemas/                 # Pydantic schemas
│   │   │   ├── services/                # External service integrations
│   │   │   ├── main.py                  # Application entry point
│   │   │   └── Dockerfile               # Backend Docker configuration
│   │   ├── docker-compose.yml           # Production Docker Compose
│   │   ├── docker-compose.dev.yml       # Development Docker Compose
│   │   ├── nginx.conf                   # Nginx configuration
│   │   └── README.md                    # Project documentation
```

## 📝 API Documentation

The API documentation is automatically generated using Swagger UI and can be accessed at http://localhost:8000/docs when the application is running.

### Key Endpoints

- `GET /api/coins/` - List all available cryptocurrencies
- `GET /api/exchanges/` - List all supported exchanges
- `GET /api/compare/{coin_id}/` - Compare prices for a specific cryptocurrency
- `GET /api/history/{coin_id}/` - Get historical data for a specific cryptocurrency

## 🧪 Testing

```bash
# Run backend tests
docker exec -it devmons-api pytest

# Run frontend tests
docker exec -it devmons-frontend npm test
```

## 🔄 Updating

To update the application to the latest version:

```bash
git pull
docker compose down
docker compose build
docker compose up -d
```

## 🛠️ Troubleshooting

### Common Issues

1. **Services not starting properly:**
   ```bash
   docker compose down
   docker compose up -d
   ```

2. **Database connection issues:**
   ```bash
   docker compose restart db
   docker compose restart api
   ```

3. **Frontend not loading:**
   - Check browser console for errors
   - Clear browser cache
   - Rebuild frontend container:
     ```bash
     docker compose build frontend
     docker compose up -d frontend
     ```

4. **API returning errors:**
   - Check logs:
     ```bash
     docker compose logs api
     ```

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add some amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📜 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 📞 Support

For support, please create an issue in the GitHub repository or contact the maintainers directly.

## 🙏 Acknowledgements

- CoinGecko API for cryptocurrency data
- All open-source libraries and frameworks used in this project 

## 🪟 Windows Quick Start (No Prerequisites)

### For Users Without Development Tools

If you're on Windows and don't have any development tools installed, follow these simple steps:

1. **Install Docker Desktop**:
   - Download Docker Desktop from [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)
   - Run the installer and follow the prompts (no special configuration needed)
   - After installation, start Docker Desktop from the Start menu

2. **Download the Project**:
   - Download and install Git from [https://git-scm.com/download/win](https://git-scm.com/download/win) (use default options)
   - Open Command Prompt (search for "cmd" in the Start menu)
   - Clone the repository:
     ```
     git clone https://github.com/GuzlejM/devmons.git
     cd devmons
     ```
   
   Alternatively, if you don't want to install Git:
   - Download the project as a ZIP file from [https://github.com/GuzlejM/devmons](https://github.com/GuzlejM/devmons)
   - Extract the ZIP file to a folder on your computer
   - Open Command Prompt and navigate to the extracted folder

3. **Start the Application**:
   - Make sure Docker Desktop is running (check the icon in the system tray)
   - In Command Prompt, run:
     ```
     docker compose up -d
     ```
   - Wait until all containers are running (this may take a few minutes on first run)

4. **Access the Application**:
   - Open your web browser (Chrome, Firefox, Edge, etc.)
   - Go to [http://localhost](http://localhost)
   - The application should load and be ready to use

5. **Common Issues on Windows**:
   - If Docker fails to start, make sure Hyper-V is enabled (Docker installer should do this automatically)
   - If you see "port already in use" errors, check if another application is using ports 80 or 8000
   - For WSL2 backend issues, run the WSL update command in PowerShell:
     ```
     wsl --update
     ```

6. **To Stop the Application**:
   - In Command Prompt, navigate to the project folder and run:
     ```
     docker compose down
     ```
   - This will stop all containers 