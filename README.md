# Stock Price Alert API

This is a FastAPI application designed to provide real-time stock price alerts based on user-defined thresholds. It uses WebSocket connections to manage real-time data feeds and client notifications.

## Overview

The application:

- Allows clients to subscribe to stock price alerts for specific stocks at certain price thresholds.
- Connects to a real-time stock data feed (currently configured for IEX Cloud's WebSocket API).
- Sends alerts to clients when stock prices cross their set thresholds.

## Setup

### Prerequisites

- Python 3.9+
- [FastAPI](https://fastapi.tiangolo.com/)
- [aiohttp](https://docs.aiohttp.org/en/stable/) for WebSocket handling
- [uvicorn](https://www.uvicorn.org/) as the ASGI server

### Installation

1. **Clone the repository:**
   ```bash
   git clone 
   cd stocks-api

2. **Set up a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`

3. **Install dependencies:**
    ```bash
    pip install -r requirements.txt

4. **Run the application:**
    ```bash
    uvicorn main:app --reload
    ```
**Configuration** 

API Keys: 
    You'll need an API key for IEX Cloud or whichever real-time data feed you're using. 
    Place your API key in the main.py where indicated ```(YOUR_API_KEY_HERE)```.

**Usage** 

WebSocket Endpoints
  - Subscribe to Alerts:
        Endpoint: ```/ws/{client_id}```
        Send JSON with ```{"action": "subscribe", "stock": "AAPL", "threshold": 150.00}```

    - Unsubscribe from Alerts:
        Endpoint: ```/ws/{client_id}```
        Send JSON with ```{"action": "unsubscribe", "stock": "AAPL"}```

**Example Client**
Here's a simple example using JavaScript and WebSocket to interact with this API:

***javascript**

    ```bash
    const socket = new WebSocket('ws://localhost:8000/ws/your-unique-client-id');

    socket.onmessage = function(event) {
        console.log('Received data:', JSON.parse(event.data));
    };

    socket.onopen = function() {
        socket.send(JSON.stringify({"action": "subscribe", "stock": "AAPL", "threshold": 150.00}));
        // To unsubscribe later
        // socket.send(JSON.stringify({"action": "unsubscribe", "stock": "AAPL"}));
    };
  
    ```
**Contributing**
Fork the repository
Create your feature branch  ```(git checkout -b feature/AmazingFeature)```
Commit your changes (git commit -am 'Add some AmazingFeature')
Push to the branch (git push origin feature/AmazingFeature)
Create a new Pull Request

**License**
[Choose an appropriate license]

**Acknowledgements**
FastAPI Team
IEX Cloud for providing the stock data (if using their service)

**TODO**
Implement authentication for secure client connections
Add unit tests
Implement error logging with a service like Sentry
Enhance error handling for WebSocket connections
Add support for more data providers