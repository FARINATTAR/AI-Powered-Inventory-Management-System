from datetime import datetime, timedelta
import requests

OPENWEATHERMAP_API_KEY = "8898c552b51fb82d17534dcb58d5049b"  # Replace with your actual API key

def get_weather_forecast(location):
    """
    Fetch weather data for a city using OpenWeatherMap.
    `location` can be a city name like 'New York' or 'London'.
    """
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHERMAP_API_KEY}&units=metric"
    
    response = requests.get(url)
    data = response.json()

    if response.status_code != 200:
        return {"error": data.get("message", "Failed to fetch weather")}

    weather = {
        "temperature": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "weather": data["weather"][0]["main"],  # e.g., Rain, Clear
        "description": data["weather"][0]["description"]
    }
    return weather

class Product:
    def __init__(self, id, name, shelf_life_days, category=None):
        self.id = id
        self.name = name
        self.shelf_life_days = shelf_life_days
        self.category = category  # New attribute for category
        self.inventory = 0
        self.sales_history = []

    def add_sale(self, quantity):
        self.sales_history.append((datetime.now(), quantity))
        self.inventory -= quantity

    def get_forecast(self, days, location=None):
        # Enhanced forecasting logic
        if not self.sales_history:
            return 0
            
        # Get sales data for the last 30 days if available
        recent_sales = self.sales_history[-30:]
        if not recent_sales:
            return 0
            
        # Calculate daily average sales
        total_sales = sum(s[1] for s in recent_sales)
        avg_sales = total_sales / len(recent_sales)
        
        # Consider trend (increase/decrease in recent sales)
        if len(recent_sales) >= 14:  # Need at least 2 weeks of data
            first_half = sum(s[1] for s in recent_sales[:len(recent_sales)//2])
            second_half = sum(s[1] for s in recent_sales[len(recent_sales)//2:])
            trend_factor = second_half / first_half if first_half > 0 else 1
            
            # Adjust forecast based on trend
            avg_sales *= trend_factor
            
        # Add buffer based on shelf life
        buffer_factor = 1.1  # 10% buffer
        if days > self.shelf_life_days:
            buffer_factor = 1.2  # Increase buffer for longer periods
            
        # Calculate forecast for requested days
        forecast = int(avg_sales * days * buffer_factor)

        # Adjust forecast based on weather if location provided
        if location:
            weather = get_weather_forecast(location)
            if "temperature" in weather:
                temp = weather["temperature"]
                # Example adjustment: increase forecast for certain products if hot weather
                if temp > 30 and self.name.lower() in ["ice cream", "juice"]:
                    forecast = int(forecast * 1.2)
                # You can add more weather-based adjustments here

        return max(1, forecast)  # Ensure at least 1 unit is forecasted

    def get_recommended_order(self, days):
        forecast = self.get_forecast(days)
        
        # Consider current inventory and shelf life
        current_stock_days = self.inventory / (forecast / days) if forecast > 0 else 0
        
        # If current stock will last longer than requested period, no order needed
        if current_stock_days >= days:
            return 0
            
        # Calculate recommended order considering shelf life
        recommended_order = forecast - self.inventory
        
        # Ensure we don't order too much that would exceed shelf life
        max_order = forecast * (self.shelf_life_days / days)
        recommended_order = min(recommended_order, max_order)
        
        return max(0, int(recommended_order))

class Supplier:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.delivery_timelines = []  # list of delivery times in days
        self.costs = []  # list of costs per order
        self.quality_ratings = []  # list of quality ratings (1-5)

    def record_delivery(self, delivery_days, cost, quality_rating):
        self.delivery_timelines.append(delivery_days)
        self.costs.append(cost)
        self.quality_ratings.append(quality_rating)

    def average_delivery_time(self):
        if not self.delivery_timelines:
            return None
        return sum(self.delivery_timelines) / len(self.delivery_timelines)

    def average_cost(self):
        if not self.costs:
            return None
        return sum(self.costs) / len(self.costs)

    def average_quality(self):
        if not self.quality_ratings:
            return None
        return sum(self.quality_ratings) / len(self.quality_ratings)

def recommend_best_suppliers(suppliers):
    # Simple recommendation based on weighted score of delivery time, cost, and quality
    def score(supplier):
        delivery = supplier.average_delivery_time() or 0
        cost = supplier.average_cost() or 0
        quality = supplier.average_quality() or 0
        # Weights can be adjusted
        return (quality * 0.5) - (delivery * 0.3) - (cost * 0.2)

    scored_suppliers = sorted(suppliers, key=score, reverse=True)
    return scored_suppliers

# Example usage
if __name__ == "__main__":
    # Create a product
    apple = Product("A1", "Apple", 7)
    
    # Add some sales
    apple.add_sale(10)
    apple.add_sale(15)
    apple.add_sale(12)
    
    # Get forecast for next 7 days
    forecast = apple.get_forecast(7)
    recommended_order = apple.get_recommended_order(7)
    
    print(f"Forecast for next 7 days: {forecast} units")
    print(f"Recommended order: {recommended_order} units")
