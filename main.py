from fastapi import FastAPI, WebSocket
from fastapi.websockets import WebSocketDisconnect
import asyncio
import aiohttp
import json

app = FastAPI()

# Dictionary to hold connections and thresholds for each user
connections: dict[str, dict] = {}

@app.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: str):
    await websocket.accept()
    connections[client_id] = {"websocket": websocket, "thresholds": {}, "last_alert_below": {}, "last_alert_above": {}}
    
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("action") == "subscribe":
                stock = data.get("stock")
                threshold = float(data.get("threshold"))
                connections[client_id]["thresholds"][stock] = threshold
                connections[client_id]["last_alert_below"][stock] = False
                connections[client_id]["last_alert_above"][stock] = False
            elif data.get("action") == "unsubscribe":
                stock = data.get("stock")
                if stock in connections[client_id]["thresholds"]:
                    del connections[client_id]["thresholds"][stock]
                    del connections[client_id]["last_alert_below"][stock]
                    del connections[client_id]["last_alert_above"][stock]
    except WebSocketDisconnect:
        # Clean up
        client_data = connections.get(client_id, {})
        if 'websocket' in client_data:
            try:
                await client_data['websocket'].close()
            except:
                pass  # Ignore if already closed or other issues
        del connections[client_id]

# Function to connect to a real-time stock data feed using aiohttp
async def connect_to_stock_feed():
    while True:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.ws_connect('wss://ws-api.iextrading.com/1.0/tops') as websocket:
                    await websocket.send_json({"symbols": ["AAPL", "GOOGL"]})  # Subscribe to stocks
                    async for msg in websocket:
                        if msg.type == aiohttp.WSMsgType.TEXT:
                            data = json.loads(msg.data)
                            if 'symbol' in data and 'lastSalePrice' in data:
                                await update_stock_price(data['symbol'], float(data['lastSalePrice']))
                        elif msg.type == aiohttp.WSMsgType.CLOSED:
                            break  # Connection closed, will retry in outer loop
                        elif msg.type == aiohttp.WSMsgType.ERROR:
                            break  # Error occurred, will retry in outer loop
        except Exception as e:
            print(f"Error in stock feed: {e}")
            await asyncio.sleep(1)  # Wait before retry

# Update stock price function
async def update_stock_price(stock: str, price: float):
    for client_id, client_data in connections.items():
        if stock in client_data["thresholds"]:
            threshold = client_data["thresholds"][stock]
            if price < threshold and not client_data["last_alert_below"][stock]:
                await client_data["websocket"].send_json({"stock": stock, "price": price, "alert": "Price below threshold!"})
                client_data["last_alert_below"][stock] = True
                client_data["last_alert_above"][stock] = False  # Reset the other alert
            elif price > threshold and not client_data["last_alert_above"][stock]:
                await client_data["websocket"].send_json({"stock": stock, "price": price, "alert": "Price above threshold!"})
                client_data["last_alert_above"][stock] = True
                client_data["last_alert_below"][stock] = False  # Reset the other alert

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(connect_to_stock_feed())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)