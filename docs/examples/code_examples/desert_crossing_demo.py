"""
Desert Crossing Game - Parameter Demonstration

This script demonstrates the impact of the actual 2020 competition parameters
on resource consumption and game strategy.
"""

from desert_crossing_game import (
    GameConfig, Weather, create_actual_weather_forecast
)


def demonstrate_weather_consumption():
    """Demonstrate weather-dependent consumption rates."""
    print("="*70)
    print("资源消耗演示 - Resource Consumption Demonstration")
    print("="*70)
    
    config = GameConfig()
    
    print("\n基础消耗量（停留时）- Base Consumption (Staying):")
    print("-"*70)
    for weather in [Weather.SUNNY, Weather.HOT, Weather.SANDSTORM]:
        water, food = config.get_consumption(weather, 1.0)
        print(f"{weather.value:8s}: {water:5.1f} 箱水, {food:5.1f} 箱食物")
    
    print("\n移动消耗量（×2倍）- Moving Consumption (×2):")
    print("-"*70)
    for weather in [Weather.SUNNY, Weather.HOT, Weather.SANDSTORM]:
        water, food = config.get_consumption(weather, config.moving_multiplier)
        print(f"{weather.value:8s}: {water:5.1f} 箱水, {food:5.1f} 箱食物")
    
    print("\n挖矿消耗量（×3倍）- Mining Consumption (×3):")
    print("-"*70)
    for weather in [Weather.SUNNY, Weather.HOT, Weather.SANDSTORM]:
        water, food = config.get_consumption(weather, config.mining_multiplier)
        print(f"{weather.value:8s}: {water:5.1f} 箱水, {food:5.1f} 箱食物")


def show_weather_forecast():
    """Display the actual 30-day weather forecast."""
    print("\n" + "="*70)
    print("30天天气预报 - 30-Day Weather Forecast")
    print("="*70)
    
    forecast = create_actual_weather_forecast()
    
    # Count weather types
    weather_counts = {
        Weather.SUNNY: 0,
        Weather.HOT: 0,
        Weather.SANDSTORM: 0
    }
    
    print("\n日期 | 天气 | 停留消耗      | 移动消耗        | 挖矿消耗")
    print("-"*70)
    
    config = GameConfig()
    
    # Show first 10 days in detail
    for day in range(1, min(11, len(forecast))):
        weather = forecast[day]
        stay_w, stay_f = config.get_consumption(weather, 1.0)
        move_w, move_f = config.get_consumption(weather, 2.0)
        mine_w, mine_f = config.get_consumption(weather, 3.0)
        
        print(f" {day:2d}  | {weather.value:4s} | {stay_w:.0f}水 {stay_f:.0f}食 | {move_w:.0f}水 {move_f:.0f}食 | {mine_w:.0f}水 {mine_f:.0f}食")
        weather_counts[weather] += 1
    
    print("...")
    
    # Count remaining days
    for day in range(11, len(forecast)):
        weather = forecast[day]
        weather_counts[weather] += 1
    
    print("\n天气统计 (Days 1-30):")
    print("-"*70)
    total_days = sum(weather_counts.values())
    for weather, count in weather_counts.items():
        percentage = (count / total_days) * 100
        print(f"{weather.value:8s}: {count:2d} 天 ({percentage:.1f}%)")


def calculate_resource_needs():
    """Calculate minimum resources needed for different strategies."""
    print("\n" + "="*70)
    print("资源需求分析 - Resource Requirements Analysis")
    print("="*70)
    
    config = GameConfig()
    forecast = create_actual_weather_forecast()
    
    # Strategy 1: Direct path (4 moves: Start->Mine->Village->End)
    print("\n策略1: 直接路径（4次移动）")
    print("路径: 起点 → 矿山 → 村庄 → 终点")
    print("-"*70)
    
    # Assume moves on days 0, 1, 2, 3
    total_water = 0
    total_food = 0
    
    for day in [0, 1, 2, 3]:
        weather = forecast[day]
        water, food = config.get_consumption(weather, config.moving_multiplier)
        total_water += water
        total_food += food
        print(f"第{day}天 ({weather.value}): {water:.0f}水 + {food:.0f}食")
    
    print(f"\n总需求: {total_water:.0f} 箱水, {total_food:.0f} 箱食物")
    print(f"总重量: {total_water * config.water_weight + total_food * config.food_weight:.0f} kg")
    cost = total_water * config.water_base_price + total_food * config.food_base_price
    print(f"最低成本: ¥{cost:.2f}")
    
    # Strategy 2: With mining (stay + mine for a few days)
    print("\n策略2: 包含挖矿（移动+停留+挖矿）")
    print("路径: 起点 → 矿山(停留+挖矿3天) → 村庄 → 终点")
    print("-"*70)
    
    total_water = 0
    total_food = 0
    
    # Day 0: Move to mine
    weather = forecast[0]
    water, food = config.get_consumption(weather, config.moving_multiplier)
    total_water += water
    total_food += food
    print(f"第0天 移动 ({weather.value}): {water:.0f}水 + {food:.0f}食")
    
    # Day 1: Stay at mine (can't mine on arrival)
    weather = forecast[1]
    water, food = config.get_consumption(weather, 1.0)
    total_water += water
    total_food += food
    print(f"第1天 停留 ({weather.value}): {water:.0f}水 + {food:.0f}食")
    
    # Days 2-4: Mine
    for day in [2, 3, 4]:
        weather = forecast[day]
        water, food = config.get_consumption(weather, config.mining_multiplier)
        total_water += water
        total_food += food
        print(f"第{day}天 挖矿 ({weather.value}): {water:.0f}水 + {food:.0f}食 (收入: ¥1000)")
    
    # Days 5-6: Move to village and end
    for day in [5, 6]:
        weather = forecast[day]
        water, food = config.get_consumption(weather, config.moving_multiplier)
        total_water += water
        total_food += food
        print(f"第{day}天 移动 ({weather.value}): {water:.0f}水 + {food:.0f}食")
    
    print(f"\n总需求: {total_water:.0f} 箱水, {total_food:.0f} 箱食物")
    print(f"总重量: {total_water * config.water_weight + total_food * config.food_weight:.0f} kg")
    cost = total_water * config.water_base_price + total_food * config.food_base_price
    mining_income = 3 * 1000  # 3 days of mining
    print(f"资源成本: ¥{cost:.2f}")
    print(f"挖矿收入: ¥{mining_income:.2f}")
    print(f"净成本: ¥{cost - mining_income:.2f}")


def main():
    """Run all demonstrations."""
    demonstrate_weather_consumption()
    show_weather_forecast()
    calculate_resource_needs()
    
    print("\n" + "="*70)
    print("演示结束 - End of Demonstration")
    print("="*70)


if __name__ == "__main__":
    main()
