# Quick Start Guide

Get your AI Diary application up and running in 5 minutes!

## Prerequisites

Make sure you have the following installed:

- [Docker Desktop](https://www.docker.com/products/docker-desktop)
- [Node.js 20+](https://nodejs.org/)
- [Python 3.11+](https://www.python.org/downloads/)

## Step 1: Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd JD_Project

# Run the setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
```

## Step 2: Configure Environment

Create a `.env` file in the project root:

```bash
cp env.example .env
```

Edit `.env` and add your credentials:

```bash
# OpenAI
OPENAI_API_KEY=sk-your-key-here

# Firebase (get from Firebase Console)
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=123456789
VITE_FIREBASE_APP_ID=1:123:web:abc123

# Backend
FIREBASE_PROJECT_ID=your-project-id
VITE_API_URL=http://localhost:8000
```

## Step 3: Set Up Firebase

1. **Create Firebase Project**

   - Go to [Firebase Console](https://console.firebase.google.com)
   - Click "Add project"
   - Follow the setup wizard

2. **Enable Authentication**

   - In your project, go to "Authentication"
   - Click "Get started"
   - Enable "Email/Password" sign-in method

3. **Create Firestore Database**

   - Go to "Firestore Database"
   - Click "Create database"
   - Start in production mode
   - Choose a location (e.g., us-central)

4. **Download Service Account**
   - Go to Project Settings > Service Accounts
   - Click "Generate new private key"
   - Save the file as `service-account.json` in your project root

## Step 4: Start the Application

```bash
# Start all services with Docker Compose
docker-compose up
```

Wait for all services to start. You should see:

- ✅ Frontend running on http://localhost:5173
- ✅ Backend API on http://localhost:8000
- ✅ Weaviate on http://localhost:8080

## Step 5: Use the Application

1. **Open your browser** and go to http://localhost:5173

2. **Create an account**

   - Click "Sign Up"
   - Enter your email and password
   - Click "Create Account"

3. **Create your first diary**

   - Click "New Entry"
   - Write a title and content
   - Click "Save"

4. **Get AI Insight**
   - Open your diary
   - Click "Get AI Insight"
   - Wait for the AI to analyze your entry
   - View your personalized feedback!

## Troubleshooting

### Port Already in Use

If you see port errors, stop other services:

```bash
# Stop any running services
docker-compose down

# Kill processes using the ports
lsof -ti:5173,8000,8080 | xargs kill -9
```

### Firebase Authentication Error

Make sure:

- Firebase Authentication is enabled
- Your API keys in `.env` are correct
- `service-account.json` is in the project root

### Cannot Connect to Backend

Check:

- Backend container is running: `docker ps`
- View backend logs: `docker-compose logs backend`
- API endpoint: http://localhost:8000/health

### Weaviate Connection Issues

```bash
# Restart Weaviate
docker-compose restart weaviate

# Check Weaviate health
curl http://localhost:8080/v1/.well-known/ready
```

## Next Steps

- 📖 Read the full [README.md](README.md) for detailed documentation
- 🚀 Learn about [Deployment](DEPLOYMENT.md) to GCP
- 🏗️ Understand the [Architecture](ARCHITECTURE.md)
- 💻 Explore the [API Documentation](http://localhost:8000/docs)

## Useful Commands

```bash
# View all services
docker-compose ps

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart a service
docker-compose restart backend

# Stop all services
docker-compose down

# Clean up everything
make clean
```

## Development Workflow

### Frontend Development

```bash
# Install dependencies
cd frontend
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Run linter
npm run lint
```

### Backend Development

```bash
# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn app.main:app --reload

# Run tests
pytest
```

## Support

If you encounter any issues:

1. Check the logs: `docker-compose logs`
2. Verify your `.env` configuration
3. Ensure all prerequisites are installed
4. Open an issue on GitHub

Happy journaling! ✨
