# Disha AI Health Coach

India's first AI health coach - A mini AI health coach chat application with WhatsApp-like UX, featuring intelligent context management, long-term memory, and medical protocol integration.

![Disha AI Health Coach](https://img.shields.io/badge/Status-Production%20Ready-green) ![Python](https://img.shields.io/badge/Python-3.9+-blue) ![Next.js](https://img.shields.io/badge/Next.js-14-black) ![FastAPI](https://img.shields.io/badge/FastAPI-0.109-teal) ![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Latest-blue)

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Architecture Overview](#-architecture-overview)
- [Local Setup](#-local-setup)
- [Deployment Guide](#-deployment-guide) 🚀
- [How It Works](#-how-it-works)
- [API Documentation](#-api-documentation)
- [LLM Integration](#-llm-integration)
- [Trade-offs & Design Decisions](#-trade-offs--design-decisions)
- [Future Improvements](#-future-improvements)

---

## ✨ Features

### Core Features

- **WhatsApp-like Chat Interface**: Familiar, conversational UI that users already know
- **Infinite Scroll**: Load chat history automatically as you scroll up
- **Smart Context Management**: Prevents token overflow while maintaining conversation quality
- **Long-term Memory**: AI remembers important user details across conversations
- **Medical Protocol Matching**: Automatically applies relevant health protocols
- **Real-time Typing Indicators**: Know when AI is generating a response
- **Onboarding Flow**: Intelligent conversation to gather user context

### Technical Features

- **Cursor-based Pagination**: Efficient message history loading
- **Redis Caching**: Fast access to protocols and typing indicators
- **Token Budget Management**: Keeps LLM calls within limits
- **Robust Error Handling**: Graceful degradation and user-friendly error messages
- **Auto-scroll**: Automatically scrolls to latest message
- **Input Validation**: Prevents empty messages, handles edge cases

---

## 🛠 Tech Stack

### Backend

- **Framework**: FastAPI (Python) - High performance, async support, auto-generated docs
- **Database**: PostgreSQL - Reliable relational database with JSONB support
- **Cache**: Redis - Fast in-memory data store for sessions and frequently accessed data
- **ORM**: SQLAlchemy - Powerful Python SQL toolkit and ORM
- **LLM**: OpenAI via OpenRouter - Cost-effective AI inference

### Frontend

- **Framework**: Next.js 14 (TypeScript) - React framework with app router
- **Styling**: TailwindCSS - Utility-first CSS framework
- **HTTP Client**: Axios - Promise-based HTTP client
- **Date Formatting**: date-fns - Modern JavaScript date utility library

### Infrastructure

- **Database Migrations**: Alembic (optional, using SQLAlchemy create_all for simplicity)
- **Environment Management**: python-dotenv, Pydantic Settings
- **Type Safety**: TypeScript (Frontend), Pydantic (Backend)

---

## 🏗 Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         Frontend                            │
│                      (Next.js + React)                      │
│                                                             |
│  • ChatInterface: Main chat UI with infinite scroll         │
│  • MessageBubble: Individual message component              │
│  • TypingIndicator: Animated typing dots                    │
│  • API Client: Axios-based backend communication            │
└────────────────────┬────────────────────────────────────────┘
                     │ HTTP/REST API
                     │
┌────────────────────┴────────────────────────────────────────-┐
│                         Backend                              │
│                    (FastAPI + Python)                        │
│                                                              │
│  Routes Layer:                                               │
│  • /api/messages - Send/receive messages                     │
│  • /api/users - User management                              │
│  • /api/typing - Typing indicator                            │
│                                                              │
│  Services Layer:                                             │
│  • LLMService: OpenRouter integration + context building     │
│  • MemoryService: Extract and retrieve long-term memories    │
│  • ProtocolService: Match and inject medical protocols       │
│  • CacheService: Redis caching for performance               │
│                                                              │
│  Data Layer:                                                 │
│  • Models: SQLAlchemy ORM models                             │
│  • Schemas: Pydantic request/response validation             │
└───────────┬─────────────────────┬───────────────────────────-┘
            │                     │
    ┌───────┴────────┐    ┌──────-┴─────┐
    │   PostgreSQL   │    │    Redis    │
    │   (Database)   │    │   (Cache)   │
    └────────────────┘    └─────────────┘
            │
    ┌───────┴────────────────────────┐
    │  Tables:                       │
    │  • users                       │
    │  • messages                    │
    │  • memories                    │
    │  • protocols                   │
    └────────────────────────────────┘
```

### Request Flow

1. **User sends message** → Frontend
2. **POST /api/messages** → Backend API
3. **Store user message** → PostgreSQL
4. **Set typing indicator** → Redis
5. **Build LLM context**:
   - Fetch recent messages
   - Retrieve relevant memories
   - Match protocols
   - Manage token budget
6. **Call OpenRouter API** → Generate AI response
7. **Store AI message** → PostgreSQL
8. **Extract memories** (if interval reached) → PostgreSQL
9. **Return response** → Frontend
10. **Update UI** → Display messages + clear typing indicator

---

## 🚀 Local Setup

### Prerequisites

Ensure you have the following installed:

- **Python 3.9+**
- **Node.js 18+**
- **PostgreSQL 12+**
- **Redis 6+**

### Step 1: Clone the Repository

```bash
git clone https://github.com/Saurabhdixit93/AI-Health-Coach
cd AI-Health-Coach
```

### Step 2: Database Setup

#### Install PostgreSQL (if not installed)

**macOS:**

```bash
brew install postgresql@15
brew services start postgresql@15
```

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

#### Create Database

```bash
# Access PostgreSQL
psql postgres

# Create database
CREATE DATABASE disha_db;

# Create user (optional)
CREATE USER disha_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE disha_db TO disha_user;

# Exit
\q
```

### Step 3: Redis Setup

#### Install Redis (if not installed)

**macOS:**

```bash
brew install redis
brew services start redis
```

**Ubuntu/Debian:**

```bash
sudo apt update
sudo apt install redis-server
sudo systemctl start redis-server
```

#### Verify Redis is running

```bash
redis-cli ping
# Should return: PONG
```

### Step 4: Backend Setup

```bash
cd backend

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env file and add your OpenRouter API key
# DATABASE_URL=postgresql://your-db-user:your-db-password@localhost:5432/disha_db
# REDIS_URL=redis://localhost:6379/0
# OPENROUTER_API_KEY=sk-or-v1-your-api-key
# AI_MODEL=openai/gpt-oss-120b:free

# Initialize database (creates tables and seeds protocols)
python -m app.init_db

# You'll see output like:
# ✓ Tables created successfully
# ✓ Created 6 new protocols
# ✓ Created demo user with ID: <uuid>
# Save this user ID for testing!

# Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The backend will be available at: **http://localhost:8000**

API docs: **http://localhost:8000/docs**

### Step 5: Frontend Setup

Open a **new terminal window**:

```bash
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.local.example .env.local

# The default API URL should be: http://localhost:8000
# Edit if your backend runs on a different port

# Start development server
npm run dev
```

The frontend will be available at: **http://localhost:3000**

### Step 6: Test the Application

1. **Open browser**: Navigate to http://localhost:3000
2. **First visit**: Application creates a demo user automatically
3. **Start chatting**: Send "Hi!" to begin conversation with Disha
4. **Test features**:
   - Send health-related queries (fever, stomach ache, etc.)
   - Scroll up to test infinite scroll
   - Watch typing indicator while AI responds
   - Check if AI remembers context from earlier messages

---

## 💡 How It Works

### 1. Context Management

The LLM service builds context from multiple sources:

```python
Context Components:
├── System Prompt (~300 tokens)
│   └── Disha's persona, guidelines, and behavior
├── Long-term Memories (~400 tokens)
│   └── Top 3-5 relevant memories about user
├── Medical Protocols (~300 tokens)
│   └── Matched protocols based on keywords
└── Recent Messages (~1500 tokens)
    └── Last 10-15 messages (dynamically adjusted)

Total Input: ~2500 tokens (safe for 4K context window)
Max Output: 500 tokens
```

**Overflow Handling:**

- Monitor total token count before LLM call
- If > 3000 tokens, reduce message count
- Always keep system prompt + top 2 memories
- Prioritize recent conversation over old messages

### 2. Memory Extraction

Every 5 messages, the system extracts key information:

**Extraction Categories:**

- **Demographics**: Age, gender, location
- **Health Conditions**: Chronic illness, allergies
- **Medications**: Current treatments
- **Lifestyle**: Diet, exercise, sleep habits
- **Symptoms**: Recent concerns

**Storage:**

- Stored in `memories` table with importance score (0-1)
- Retrieved by relevance and recency
- Used to personalize future responses

### 3. Protocol Matching

**Keyword-based Matching:**

```javascript
User: "I have a fever and headache"
          ↓
Keywords detected: ["fever", "headache"]
          ↓
Matched protocols:
  - Fever Management
  - Headache Management
          ↓
Protocol instructions injected into LLM context
          ↓
AI responds with protocol-guided advice
```

**Seed Protocols:**

1. Fever Management
2. Stomach Issues
3. Cold and Cough
4. Headache Management
5. Emergency Situations (always advise seeking help)
6. Refund Policy (redirect to support)

### 4. Pagination Strategy

**Cursor-based Pagination** (not offset-based):

```
Advantages:
✓ Consistent results even with new data
✓ No duplicate messages
✓ Efficient for large datasets
✓ Better performance for infinite scroll

How it works:
1. Client requests: GET /api/messages?user_id=X&limit=50
2. Server returns: 50 messages + next_cursor (last message ID)
3. Client requests more: GET /api/messages?user_id=X&before=<cursor>&limit=50
4. Repeat until has_more = false
```

---

## 📚 API Documentation

### Endpoints

#### **POST /api/users**

Create a new user.

**Request:**

```json
{
  "name": "John Doe",
  "metadata": {
    "age": 30,
    "location": "Mumbai"
  }
}
```

**Response:**

```json
{
  "id": "uuid",
  "name": "John Doe",
  "metadata": {...},
  "created_at": "2025-12-23T...",
  "updated_at": "2025-12-23T..."
}
```

---

#### **GET /api/users/{user_id}**

Get user by ID.

---

#### **POST /api/messages**

Send a message and receive AI response.

**Request:**

```json
{
  "user_id": "uuid",
  "content": "I have a fever",
  "is_onboarding": false
}
```

**Response:**

```json
{
  "user_message": {
    "id": "uuid",
    "role": "user",
    "content": "I have a fever",
    "created_at": "..."
  },
  "ai_response": {
    "id": "uuid",
    "role": "assistant",
    "content": "I'm sorry to hear that...",
    "created_at": "..."
  }
}
```

---

#### **GET /api/messages**

Get paginated message history.

**Query Parameters:**

- `user_id` (required): User UUID
- `before` (optional): Cursor for pagination
- `limit` (optional): Number of messages (default: 50, max: 100)

**Response:**

```json
{
  "messages": [...],
  "has_more": true,
  "next_cursor": "uuid"
}
```

---

#### **GET /api/typing/{user_id}**

Get typing indicator status.

**Response:**

```json
{
  "is_typing": true,
  "user_id": "uuid"
}
```

---

#### **GET /api/health**

Health check endpoint.

---

## 🤖 LLM Integration

### OpenRouter Configuration

**Provider**: OpenAI via OpenRouter  
**Model**: `openai/gpt-oss-120b:free` (configurable)  
**Temperature**: 0.7 (balanced creativity and consistency)  
**Max Tokens**: 500 (concise responses)

### System Prompt

The AI is instructed to:

- Act as a warm, empathetic health coach (like a caring WhatsApp friend)
- Provide personalized guidance based on user context
- Ask clarifying questions
- Follow medical protocols
- Keep responses concise (2-4 sentences)
- **Never provide emergency medical advice** - always redirect to doctors

### Why OpenRouter?

1. **Cost-effective**: Free tier available, pay-as-you-go pricing
2. **Multiple models**: Easy to switch between providers
3. **No vendor lock-in**: OpenAI-compatible API
4. **Reliable**: High uptime and good performance

---

## 🔄 Trade-offs & Design Decisions

### Key Decisions

| Decision                           | Rationale                                         | Alternative                      |
| ---------------------------------- | ------------------------------------------------- | -------------------------------- |
| **FastAPI over Flask**             | Async/await support, auto-docs, modern type hints | Flask with extensions            |
| **Cursor pagination**              | More efficient for infinite scroll than offset    | Offset-based pagination          |
| **Keyword matching for protocols** | Simple, fast, no external dependencies            | Semantic search with embeddings  |
| **Periodic memory extraction**     | Balances cost vs. context quality                 | Real-time extraction (expensive) |
| **Single session model**           | Simpler UX and backend                            | Multi-session with create/delete |
| **Redis for caching**              | Fast, widely adopted, simple setup                | Memcached or in-memory dict      |
| **SQLAlchemy ORM**                 | Type safety, relationship management              | Raw SQL queries                  |
| **WhatsApp-like UI**               | Familiar to users, conversational feel            | ChatGPT-like interface           |

### Performance Optimizations

- **Redis caching** for protocols (24h TTL)
- **Connection pooling** for PostgreSQL
- **Cursor-based pagination** for efficient data fetching
- **Token counting** to prevent context overflow
- **Lazy loading** of message history

### Security Considerations

⚠️ **This is a demo application**. For production:

- Add user authentication (JWT, OAuth)
- Implement rate limiting
- Sanitize user inputs
- Add HTTPS/TLS
- Use environment-specific configs
- Add logging and monitoring
- Implement CSRF protection
- Add API key rotation

---

## 🚧 Future Improvements

### If I Had More Time...

#### High Priority

- **WebSockets**: Real-time bidirectional communication instead of polling
- **Vector Database**: Use Pinecone/Weaviate for semantic memory search
- **Message Streaming**: Stream AI responses token-by-token for better UX
- **Authentication**: JWT-based auth with signup/login
- **Multi-session Support**: Allow users to create/delete conversations

#### Medium Priority

- **Advanced RAG**: Embed medical knowledge base for better protocol matching
- **Voice Input/Output**: WhatsApp-style voice messages
- **File Uploads**: Share medical reports, prescriptions
- **Better Onboarding**: Adaptive flow based on user type
- **Analytics Dashboard**: Track engagement, common queries

#### Nice to Have

- **Sentiment Analysis**: Detect user mood and adjust tone
- **Wearables Integration**: Sync with Fitbit, Apple Health
- **Multilingual Support**: Hindi, Tamil, Bengali, etc.
- **Export Chat**: Download conversation as PDF
- **A/B Testing**: Experiment with different prompts
- **Mobile Apps**: Native iOS/Android apps

---

## 🐛 Troubleshooting

### Backend Issues

**Port already in use:**

```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

**Database connection error:**

```bash
# Check if PostgreSQL is running
pg_isready

# Check database exists
psql -l | grep disha_db
```

**Redis connection error:**

```bash
# Check if Redis is running
redis-cli ping

# Start Redis
brew services start redis  # macOS
sudo systemctl start redis  # Linux
```

### Frontend Issues

**API connection failed:**

- Verify backend is running on port 8000
- Check `.env.local` has correct `NEXT_PUBLIC_API_URL`
- Check CORS settings in backend config

**Node modules error:**

```bash
rm -rf node_modules package-lock.json
npm install
```

---

## 📝 License

This project is created for educational/assignment purposes.

---

## 👨‍💻 Author

Built with ❤️ for Curelink (Disha AI Health Coach Assignment)

---

## 📞 Support

For issues or questions:

1. Check the troubleshooting section above
2. Review API docs at http://localhost:8000/docs
3. Check logs in terminal for error messages

---

**Enjoy chatting with Disha! 🏥💚**
