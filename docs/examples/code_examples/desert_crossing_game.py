"""
Desert Crossing Game - Mathematical Modeling Optimization Problem

This is an Operations Research teaching game from the 2020 National College Student
Mathematical Modeling Competition (Problem B).

The game simulates a player crossing a desert with limited resources (water, food, money)
while making optimal decisions to maximize remaining funds at the destination.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import sys


class Weather(Enum):
    """Weather conditions in the desert."""
    SUNNY = "晴朗"
    HOT = "高温"
    SANDSTORM = "沙暴"


class LocationType(Enum):
    """Types of locations on the map."""
    START = "起点"
    END = "终点"
    DESERT = "沙漠"
    MINE = "矿山"
    VILLAGE = "村庄"


@dataclass
class GameConfig:
    """Game configuration and constants."""
    # Basic settings
    deadline: int = 30  # Maximum days to reach destination
    initial_funds: float = 10000.0  # Starting money
    weight_limit: float = 1200.0  # Maximum weight capacity (kg)
    
    # Resource settings
    water_base_price: float = 5.0  # Base price per box of water
    food_base_price: float = 10.0  # Base price per box of food
    water_weight: float = 3.0  # Weight per box of water (kg)
    food_weight: float = 2.0  # Weight per box of food (kg)
    
    # Consumption rates
    base_water_consumption: float = 5.0  # Boxes per day when staying
    base_food_consumption: float = 7.0  # Boxes per day when staying
    moving_multiplier: float = 2.0  # Consumption multiplier when moving
    mining_multiplier: float = 3.0  # Consumption multiplier when mining
    
    # Economic settings
    village_price_multiplier: float = 2.0  # Village prices vs base prices
    return_price_ratio: float = 0.5  # Return value ratio at destination
    mine_base_income: float = 1000.0  # Base income per day of mining
    
    def get_water_price(self, at_village: bool = False) -> float:
        """Get water price based on location."""
        return self.water_base_price * (self.village_price_multiplier if at_village else 1.0)
    
    def get_food_price(self, at_village: bool = False) -> float:
        """Get food price based on location."""
        return self.food_base_price * (self.village_price_multiplier if at_village else 1.0)


@dataclass
class Location:
    """A location on the map."""
    id: int
    type: LocationType
    x: int
    y: int
    neighbors: List[int] = field(default_factory=list)
    
    def __str__(self) -> str:
        return f"{self.type.value}({self.id})"


@dataclass
class GameState:
    """Current state of the game."""
    day: int = 0
    position: int = 0  # Current location ID
    water: float = 0.0  # Boxes of water
    food: float = 0.0  # Boxes of food
    money: float = 0.0  # Remaining funds
    purchased_at_start: bool = False  # Has purchased at start
    arrived_at_mine_today: bool = False  # Just arrived at mine
    game_over: bool = False
    success: bool = False
    
    def get_total_weight(self, config: GameConfig) -> float:
        """Calculate total weight of carried resources."""
        return self.water * config.water_weight + self.food * config.food_weight
    
    def can_carry(self, water: float, food: float, config: GameConfig) -> bool:
        """Check if player can carry the specified resources."""
        weight = water * config.water_weight + food * config.food_weight
        return weight <= config.weight_limit


@dataclass
class Map:
    """Game map with locations."""
    locations: Dict[int, Location] = field(default_factory=dict)
    start_id: int = 0
    end_id: int = 1
    
    def add_location(self, location: Location) -> None:
        """Add a location to the map."""
        self.locations[location.id] = location
        if location.type == LocationType.START:
            self.start_id = location.id
        elif location.type == LocationType.END:
            self.end_id = location.id
    
    def add_edge(self, loc1_id: int, loc2_id: int) -> None:
        """Add bidirectional connection between two locations."""
        if loc1_id in self.locations and loc2_id in self.locations:
            if loc2_id not in self.locations[loc1_id].neighbors:
                self.locations[loc1_id].neighbors.append(loc2_id)
            if loc1_id not in self.locations[loc2_id].neighbors:
                self.locations[loc2_id].neighbors.append(loc1_id)
    
    def get_distance(self, loc1_id: int, loc2_id: int) -> int:
        """Calculate Manhattan distance between two locations."""
        loc1 = self.locations[loc1_id]
        loc2 = self.locations[loc2_id]
        return abs(loc1.x - loc2.x) + abs(loc1.y - loc2.y)


class DesertCrossingGame:
    """Main game engine for the Desert Crossing Game."""
    
    def __init__(self, config: GameConfig, game_map: Map, weather_forecast: List[Weather]):
        """Initialize the game.
        
        Args:
            config: Game configuration
            game_map: The map with locations
            weather_forecast: Weather for each day (index = day number)
        """
        self.config = config
        self.map = game_map
        self.weather_forecast = weather_forecast
        self.state = GameState(money=config.initial_funds, position=game_map.start_id)
    
    def get_weather(self, day: int) -> Weather:
        """Get weather for a specific day."""
        if 0 <= day < len(self.weather_forecast):
            return self.weather_forecast[day]
        return Weather.SUNNY
    
    def purchase_resources(self, water: float, food: float) -> bool:
        """Purchase resources at current location.
        
        Args:
            water: Boxes of water to purchase
            food: Boxes of food to purchase
        
        Returns:
            True if purchase successful, False otherwise
        """
        current_loc = self.map.locations[self.state.position]
        
        # Check if can purchase at this location
        at_village = current_loc.type == LocationType.VILLAGE
        at_start = current_loc.type == LocationType.START
        
        if not (at_village or (at_start and not self.state.purchased_at_start)):
            return False
        
        # Calculate cost
        water_price = self.config.get_water_price(at_village)
        food_price = self.config.get_food_price(at_village)
        total_cost = water * water_price + food * food_price
        
        # Check if can afford and carry
        if total_cost > self.state.money:
            return False
        
        new_water = self.state.water + water
        new_food = self.state.food + food
        
        if not self.state.can_carry(new_water, new_food, self.config):
            return False
        
        # Execute purchase
        self.state.water = new_water
        self.state.food = new_food
        self.state.money -= total_cost
        
        if at_start:
            self.state.purchased_at_start = True
        
        return True
    
    def consume_resources(self, water: float, food: float) -> bool:
        """Consume resources.
        
        Args:
            water: Boxes of water to consume
            food: Boxes of food to consume
        
        Returns:
            True if resources available, False if insufficient
        """
        if self.state.water >= water and self.state.food >= food:
            self.state.water -= water
            self.state.food -= food
            return True
        return False
    
    def stay(self, mine: bool = False) -> bool:
        """Stay at current location for one day.
        
        Args:
            mine: Whether to mine (only valid at mines)
        
        Returns:
            True if action successful, False otherwise
        """
        current_loc = self.map.locations[self.state.position]
        
        # Check if mining is valid
        if mine:
            if current_loc.type != LocationType.MINE:
                return False
            if self.state.arrived_at_mine_today:
                return False
        
        # Calculate consumption
        multiplier = 1.0
        if mine:
            multiplier = self.config.mining_multiplier
        
        water_consumed = self.config.base_water_consumption * multiplier
        food_consumed = self.config.base_food_consumption * multiplier
        
        # Consume resources
        if not self.consume_resources(water_consumed, food_consumed):
            self.state.game_over = True
            self.state.success = False
            return False
        
        # Add mining income
        if mine:
            self.state.money += self.config.mine_base_income
        
        # Advance day
        self.state.day += 1
        self.state.arrived_at_mine_today = False
        
        # Check if time limit exceeded
        if self.state.day > self.config.deadline:
            self.state.game_over = True
            self.state.success = False
        
        return True
    
    def move(self, target_location_id: int) -> bool:
        """Move to an adjacent location.
        
        Args:
            target_location_id: ID of target location
        
        Returns:
            True if move successful, False otherwise
        """
        # Check if it's a sandstorm day
        if self.get_weather(self.state.day) == Weather.SANDSTORM:
            return False
        
        # Check if target is adjacent
        current_loc = self.map.locations[self.state.position]
        if target_location_id not in current_loc.neighbors:
            return False
        
        # Calculate consumption
        water_consumed = self.config.base_water_consumption * self.config.moving_multiplier
        food_consumed = self.config.base_food_consumption * self.config.moving_multiplier
        
        # Consume resources
        if not self.consume_resources(water_consumed, food_consumed):
            self.state.game_over = True
            self.state.success = False
            return False
        
        # Move
        self.state.position = target_location_id
        self.state.day += 1
        
        # Check if arrived at mine
        target_loc = self.map.locations[target_location_id]
        self.state.arrived_at_mine_today = (target_loc.type == LocationType.MINE)
        
        # Check if reached destination
        if self.state.position == self.map.end_id:
            self.state.game_over = True
            self.state.success = True
            # Return remaining resources for half price
            water_return = self.state.water * self.config.water_base_price * self.config.return_price_ratio
            food_return = self.state.food * self.config.food_base_price * self.config.return_price_ratio
            self.state.money += water_return + food_return
            self.state.water = 0
            self.state.food = 0
        
        # Check if time limit exceeded
        if self.state.day > self.config.deadline:
            self.state.game_over = True
            self.state.success = False
        
        return True
    
    def print_state(self) -> None:
        """Print current game state."""
        current_loc = self.map.locations[self.state.position]
        weather = self.get_weather(self.state.day)
        
        print(f"\n{'='*60}")
        print(f"第 {self.state.day} 天 | 天气: {weather.value}")
        print(f"位置: {current_loc}")
        print(f"资金: ¥{self.state.money:.2f}")
        print(f"水: {self.state.water:.1f} 箱 | 食物: {self.state.food:.1f} 箱")
        print(f"负重: {self.state.get_total_weight(self.config):.1f}/{self.config.weight_limit:.1f} kg")
        print(f"{'='*60}")


def create_sample_map() -> Map:
    """Create a sample map for testing.
    
    This creates a simple linear path: Start -> Mine -> Village -> End
    """
    game_map = Map()
    
    # Create locations
    start = Location(0, LocationType.START, 0, 0)
    mine = Location(1, LocationType.MINE, 1, 0)
    village = Location(2, LocationType.VILLAGE, 2, 0)
    end = Location(3, LocationType.END, 3, 0)
    
    # Add locations to map
    game_map.add_location(start)
    game_map.add_location(mine)
    game_map.add_location(village)
    game_map.add_location(end)
    
    # Add edges
    game_map.add_edge(0, 1)  # Start <-> Mine
    game_map.add_edge(1, 2)  # Mine <-> Village
    game_map.add_edge(2, 3)  # Village <-> End
    
    return game_map


def create_sample_weather(days: int) -> List[Weather]:
    """Create sample weather forecast.
    
    Args:
        days: Number of days to forecast
    
    Returns:
        List of weather conditions
    """
    # Simple pattern: mostly sunny with occasional hot/sandstorm
    weather = [Weather.SUNNY] * days
    
    # Add some variation
    if days >= 5:
        weather[4] = Weather.HOT
    if days >= 10:
        weather[9] = Weather.SANDSTORM
    if days >= 15:
        weather[14] = Weather.HOT
    
    return weather


def run_sample_game():
    """Run a sample game with a simple strategy."""
    print("=" * 60)
    print("沙漠穿越游戏 - Desert Crossing Game")
    print("2020年全国大学生数学建模竞赛 B题")
    print("=" * 60)
    
    # Create game configuration
    config = GameConfig(
        deadline=30,
        initial_funds=10000.0,
        weight_limit=1200.0,
    )
    
    # Create map and weather
    game_map = create_sample_map()
    weather_forecast = create_sample_weather(config.deadline + 5)
    
    # Initialize game
    game = DesertCrossingGame(config, game_map, weather_forecast)
    
    print("\n游戏开始！")
    print(f"初始资金: ¥{config.initial_funds:.2f}")
    print(f"截止日期: 第 {config.deadline} 天")
    print(f"负重上限: {config.weight_limit:.1f} kg")
    
    # Print map
    print("\n地图:")
    for loc_id, loc in game_map.locations.items():
        neighbors = [str(game_map.locations[n].type.value) for n in loc.neighbors]
        print(f"  {loc} -> 相邻: {', '.join(neighbors)}")
    
    game.print_state()
    
    # Simple strategy: Buy at start, move through locations, mine once, then reach end
    print("\n执行策略...")
    
    # Day 0: Purchase resources at start
    print("\n第0天: 在起点购买资源")
    water_to_buy = 100.0
    food_to_buy = 150.0
    if game.purchase_resources(water_to_buy, food_to_buy):
        print(f"  购买成功: {water_to_buy}箱水, {food_to_buy}箱食物")
        print(f"  花费: ¥{water_to_buy * config.water_base_price + food_to_buy * config.food_base_price:.2f}")
    game.print_state()
    
    # Day 1: Move to mine
    print("\n第1天: 移动到矿山")
    if game.move(1):
        print("  移动成功")
    game.print_state()
    
    # Day 2: Stay at mine (can't mine on arrival day)
    print("\n第2天: 在矿山停留（不能在到达当天挖矿）")
    if game.stay(mine=False):
        print("  停留成功")
    game.print_state()
    
    # Day 3: Mine at the mine
    print("\n第3天: 在矿山挖矿")
    if game.stay(mine=True):
        print(f"  挖矿成功，获得 ¥{config.mine_base_income:.2f}")
    game.print_state()
    
    # Day 4: Move to village
    print("\n第4天: 移动到村庄")
    if game.move(2):
        print("  移动成功")
    game.print_state()
    
    # Day 5: Move to end
    print("\n第5天: 移动到终点")
    if game.move(3):
        print("  移动成功")
    game.print_state()
    
    # Final results
    print("\n" + "=" * 60)
    if game.state.success:
        print("游戏成功！")
        print(f"最终资金: ¥{game.state.money:.2f}")
        print(f"用时: {game.state.day} 天")
    else:
        print("游戏失败！")
        if game.state.day > config.deadline:
            print("原因: 超过截止日期")
        else:
            print("原因: 资源耗尽")
    print("=" * 60)


if __name__ == "__main__":
    run_sample_game()
