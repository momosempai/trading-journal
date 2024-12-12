# Trading Journal Application

A web-based trading journal application to track and analyze your trading performance.

## Features

- Track trades with detailed information
- Calculate key performance indicators (KPIs)
- Monitor win rate and profit/loss
- Track trade execution quality, management, and psychology
- Visual performance analytics
- Docker support for easy deployment

## Tech Stack

- Backend: Python with Flask
- Database: SQLite
- Frontend: Bootstrap, Chart.js
- Container: Docker

## Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/YOUR_USERNAME/trading-journal.git
cd trading-journal
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app.py
```

### Docker Installation

1. Build and run with Docker Compose:
```bash
docker-compose up --build
```

## Usage

1. Access the application at `http://localhost:5000`
2. Add new trades using the "Add Trade" button
3. Track your performance through the dashboard
4. Close trades and add performance metrics

## Project Structure

```
trading-journal/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── Dockerfile         # Docker configuration
├── docker-compose.yml # Docker Compose configuration
├── static/
│   └── js/
│       └── main.js    # Frontend JavaScript
└── templates/
    └── index.html     # Main HTML template
```

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
