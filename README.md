# Python Learning Platform

A comprehensive web-based platform for learning Python programming with interactive lessons, real-world projects, and achievement tracking.

## Features

### 📚 **Learning Materials**
- **6 Detailed Chapters** with explanations and examples
- Interactive code examples you can run instantly
- Concept boxes and pro tips for deeper understanding
- Support for English 🇬🇧 and Arabic 🇸🇦

### 🎯 **Structured Learning**
- **4 Comprehensive Courses**
  - Python Fundamentals (Beginner)
  - Intermediate Python (Intermediate)
  - Advanced Python (Advanced)
  - Data Science & APIs (Intermediate)
- Visual curriculum maps showing progression
- Progress tracking per course

### 💻 **Interactive Coding**
- **17 Lessons** with hands-on exercises
- **Auto-grading system** that checks your code
- Code editor with hints and solutions
- Instant feedback on your exercises

### 🛠️ **Real-World Projects**
- **3 Project-Based Challenges**
  - Web Scraper (BeautifulSoup & Requests)
  - Data Analysis (Pandas & NumPy)
  - Weather App API Integration
- Multi-step project exercises
- Real-world applications learning

### 🏆 **Gamification & Tracking**
- **Streak Counter** - Track consecutive days of learning
- **Achievement Badges** - Unlock 9 different badges
- **Progress Dashboard** - Visual progress tracking
- **Statistics** - Monitor your learning journey

### 🌐 **Multilingual Support**
- Full Arabic translation (عربي)
- English support
- Automatic RTL layout for Arabic
- Easy language switching

## Tech Stack

### Backend
- **Framework**: Flask (Python)
- **Database**: SQLite
- **Authentication**: JWT
- **Code Execution**: Local Python subprocess

### Frontend
- **Framework**: React
- **Language**: JavaScript
- **Editor**: Monaco Editor
- **Styling**: CSS-in-JS

## Getting Started

### Prerequisites
- Python 3.6+
- Node.js 12+
- npm or yarn

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/python-learning-app.git
cd python-learning-app
```

2. **Backend Setup**
```bash
cd backend
pip install -r requirements.txt
python test_server.py
```

3. **Frontend Setup** (new terminal)
```bash
cd frontend
npm install
npm start
```

4. **Open in Browser**
```
http://localhost:3000
```

## Usage

### For Learners

1. **Register** a new account or use test credentials:
   - Email: `test@test.com`
   - Password: `123456`

2. **Choose Your Path**
   - Go to **Courses** to see structured learning paths
   - Start with **Python Fundamentals**
   - Progress through lessons and exercises

3. **Interactive Learning**
   - Read explanations on **Learn** page
   - Run code examples instantly
   - Complete **Lessons** with auto-grading
   - Build **Projects** for real-world skills

4. **Track Progress**
   - View **Dashboard** for statistics
   - Check **Achievements** you've unlocked
   - Monitor your **Streak**

5. **Languages**
   - Click language button (عربي / English) in navbar
   - Learn in your preferred language

## Project Structure

```
python-learning-app/
├── backend/
│   ├── test_server.py          # Main Flask app
│   ├── requirements.txt         # Python dependencies
│   └── instance/
│       └── test.db             # SQLite database
├── frontend/
│   ├── src/
│   │   ├── pages/              # React pages
│   │   ├── components/         # Reusable components
│   │   ├── context/            # Context providers
│   │   ├── App.js              # Main app component
│   │   └── translations.js      # Language translations
│   └── package.json            # Node dependencies
└── README.md
```

## Available Pages

- `/` - Home page
- `/register` - User registration
- `/login` - User login
- `/dashboard` - Learning dashboard with stats
- `/learn` - Interactive Python book with examples
- `/courses` - Structured learning paths
- `/lessons/:id` - Individual lesson with exercises
- `/projects` - Real-world project challenges
- `/projects/:projectId` - Project workspace

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login user

### Learning
- `GET /api/lessons` - Get all lessons
- `GET /api/lessons/:id` - Get lesson with exercises
- `GET /api/progress` - Get user progress
- `GET /api/streak` - Get user streak
- `GET /api/achievements` - Get user achievements

### Code Execution
- `POST /api/run` - Execute Python code
- `POST /api/submit/:id` - Submit exercise solution

### Projects
- `GET /api/projects` - Get all projects
- `GET /api/projects/:id` - Get project details

## Features in Development

- Advanced analytics
- Collaborative learning
- Code sharing and feedback
- Mobile app
- More languages
- Custom learning paths
- Certificates

## Contributing

Contributions are welcome! Please feel free to:
1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see LICENSE file for details.

## Author

Created by Abdel for Python learners worldwide.

## Support

For issues, questions, or suggestions:
- Create an issue on GitHub
- Contact: your.email@example.com

## Roadmap

- [ ] Mobile responsive design
- [ ] Mobile app (React Native)
- [ ] More programming languages
- [ ] Team learning features
- [ ] Certificates of completion
- [ ] Integration with popular job boards
- [ ] Video lessons integration
- [ ] Live coding sessions

---

**Happy Learning!** 🎓

Start at `/learn` for a guided introduction, or jump to `/courses` to choose your learning path.
