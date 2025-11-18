"""
Desert Crossing Game - Optimization Solver

This module provides optimization algorithms to find the optimal strategy
for the Desert Crossing Game using dynamic programming.
"""

from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass
import copy
import sys
import os

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from desert_crossing_game import (
    GameConfig, Map, Weather, GameState, DesertCrossingGame,
    LocationType, create_sample_map, create_sample_weather
)


@dataclass
class Action:
    """Represents a possible action in the game."""
    type: str  # "stay", "move", "mine", "buy"
    target_location: Optional[int] = None  # For move actions
    water_to_buy: float = 0.0  # For buy actions
    food_to_buy: float = 0.0  # For buy actions
    mine: bool = False  # For stay actions at mines
    
    def __str__(self) -> str:
        if self.type == "move":
            return f"移动到位置{self.target_location}"
        elif self.type == "mine":
            return "挖矿"
        elif self.type == "stay":
            return "停留"
        elif self.type == "buy":
            return f"购买({self.water_to_buy:.1f}水, {self.food_to_buy:.1f}食物)"
        return self.type


@dataclass
class StateKey:
    """Key for memoization in dynamic programming."""
    day: int
    position: int
    water_level: int  # Discretized water level
    food_level: int  # Discretized food level
    money_level: int  # Discretized money level
    purchased_at_start: bool
    
    def __hash__(self) -> int:
        return hash((self.day, self.position, self.water_level, self.food_level, 
                    self.money_level, self.purchased_at_start))
    
    def __eq__(self, other) -> bool:
        if not isinstance(other, StateKey):
            return False
        return (self.day == other.day and self.position == other.position and
                self.water_level == other.water_level and self.food_level == other.food_level and
                self.money_level == other.money_level and 
                self.purchased_at_start == other.purchased_at_start)


class DesertCrossingOptimizer:
    """Optimizer for finding optimal strategy in Desert Crossing Game."""
    
    def __init__(self, config: GameConfig, game_map: Map, weather_forecast: List[Weather]):
        """Initialize optimizer.
        
        Args:
            config: Game configuration
            game_map: The game map
            weather_forecast: Weather forecast for each day
        """
        self.config = config
        self.map = game_map
        self.weather_forecast = weather_forecast
        
        # Discretization parameters (for state space reduction)
        self.water_discretization = 5.0  # Discretize water in units of 5 boxes
        self.food_discretization = 5.0  # Discretize food in units of 5 boxes
        self.money_discretization = 100.0  # Discretize money in units of 100
        
        # Memoization
        self.memo: Dict[StateKey, Tuple[float, List[Action]]] = {}
    
    def discretize_state(self, state: GameState) -> StateKey:
        """Convert continuous state to discrete state key for memoization.
        
        Args:
            state: Current game state
        
        Returns:
            Discretized state key
        """
        return StateKey(
            day=state.day,
            position=state.position,
            water_level=int(state.water / self.water_discretization),
            food_level=int(state.food / self.food_discretization),
            money_level=int(state.money / self.money_discretization),
            purchased_at_start=state.purchased_at_start
        )
    
    def get_possible_actions(self, state: GameState) -> List[Action]:
        """Get all possible actions from current state.
        
        Args:
            state: Current game state
        
        Returns:
            List of possible actions
        """
        actions = []
        current_loc = self.map.locations[state.position]
        weather = self.weather_forecast[state.day] if state.day < len(self.weather_forecast) else Weather.SUNNY
        
        # If at start and haven't purchased yet, consider buying
        if current_loc.type == LocationType.START and not state.purchased_at_start:
            # Generate some purchase options
            purchase_options = [
                (50.0, 75.0),   # Conservative
                (100.0, 150.0), # Moderate
                (150.0, 200.0), # Aggressive
            ]
            
            for water, food in purchase_options:
                cost = water * self.config.water_base_price + food * self.config.food_base_price
                if cost <= state.money and state.can_carry(water, food, self.config):
                    actions.append(Action("buy", water_to_buy=water, food_to_buy=food))
        
        # If at village, consider buying
        if current_loc.type == LocationType.VILLAGE:
            # Small purchases at village (expensive)
            purchase_options = [
                (10.0, 15.0),
                (20.0, 30.0),
            ]
            
            for water, food in purchase_options:
                water_price = self.config.get_water_price(at_village=True)
                food_price = self.config.get_food_price(at_village=True)
                cost = water * water_price + food * food_price
                
                new_water = state.water + water
                new_food = state.food + food
                
                if cost <= state.money and state.can_carry(new_water, new_food, self.config):
                    actions.append(Action("buy", water_to_buy=water, food_to_buy=food))
        
        # If at mine and not just arrived, consider mining
        if current_loc.type == LocationType.MINE and not state.arrived_at_mine_today:
            water_needed = self.config.base_water_consumption * self.config.mining_multiplier
            food_needed = self.config.base_food_consumption * self.config.mining_multiplier
            if state.water >= water_needed and state.food >= food_needed:
                actions.append(Action("mine", mine=True))
        
        # Consider staying (if not forced by sandstorm, this is optional)
        water_needed = self.config.base_water_consumption
        food_needed = self.config.base_food_consumption
        if state.water >= water_needed and state.food >= food_needed:
            actions.append(Action("stay"))
        
        # Consider moving to adjacent locations (if not sandstorm)
        if weather != Weather.SANDSTORM:
            for neighbor_id in current_loc.neighbors:
                water_needed = self.config.base_water_consumption * self.config.moving_multiplier
                food_needed = self.config.base_food_consumption * self.config.moving_multiplier
                if state.water >= water_needed and state.food >= food_needed:
                    actions.append(Action("move", target_location=neighbor_id))
        
        return actions
    
    def simulate_action(self, state: GameState, action: Action) -> Optional[GameState]:
        """Simulate an action and return the resulting state.
        
        Args:
            state: Current state
            action: Action to simulate
        
        Returns:
            New state after action, or None if action is invalid
        """
        # Create a copy of the state
        new_state = copy.deepcopy(state)
        current_loc = self.map.locations[state.position]
        
        if action.type == "buy":
            # Calculate cost
            at_village = current_loc.type == LocationType.VILLAGE
            water_price = self.config.get_water_price(at_village)
            food_price = self.config.get_food_price(at_village)
            cost = action.water_to_buy * water_price + action.food_to_buy * food_price
            
            # Check if valid
            if cost > new_state.money:
                return None
            
            new_state.water += action.water_to_buy
            new_state.food += action.food_to_buy
            
            if not new_state.can_carry(new_state.water, new_state.food, self.config):
                return None
            
            new_state.money -= cost
            
            if current_loc.type == LocationType.START:
                new_state.purchased_at_start = True
            
            return new_state
        
        elif action.type == "stay" or action.type == "mine":
            # Calculate consumption
            multiplier = self.config.mining_multiplier if action.type == "mine" else 1.0
            water_consumed = self.config.base_water_consumption * multiplier
            food_consumed = self.config.base_food_consumption * multiplier
            
            # Check resources
            if new_state.water < water_consumed or new_state.food < food_consumed:
                return None
            
            new_state.water -= water_consumed
            new_state.food -= food_consumed
            
            # Add mining income
            if action.type == "mine":
                new_state.money += self.config.mine_base_income
            
            new_state.day += 1
            new_state.arrived_at_mine_today = False
            
            return new_state
        
        elif action.type == "move":
            # Check weather
            weather = self.weather_forecast[state.day] if state.day < len(self.weather_forecast) else Weather.SUNNY
            if weather == Weather.SANDSTORM:
                return None
            
            # Check if valid move
            if action.target_location not in current_loc.neighbors:
                return None
            
            # Calculate consumption
            water_consumed = self.config.base_water_consumption * self.config.moving_multiplier
            food_consumed = self.config.base_food_consumption * self.config.moving_multiplier
            
            # Check resources
            if new_state.water < water_consumed or new_state.food < food_consumed:
                return None
            
            new_state.water -= water_consumed
            new_state.food -= food_consumed
            new_state.position = action.target_location
            new_state.day += 1
            
            # Check if arrived at mine
            target_loc = self.map.locations[action.target_location]
            new_state.arrived_at_mine_today = (target_loc.type == LocationType.MINE)
            
            # Check if reached destination
            if new_state.position == self.map.end_id:
                new_state.game_over = True
                new_state.success = True
                # Return remaining resources
                water_return = new_state.water * self.config.water_base_price * self.config.return_price_ratio
                food_return = new_state.food * self.config.food_base_price * self.config.return_price_ratio
                new_state.money += water_return + food_return
                new_state.water = 0
                new_state.food = 0
            
            return new_state
        
        return None
    
    def solve_recursive(self, state: GameState, depth: int = 0, max_depth: int = 50) -> Tuple[float, List[Action]]:
        """Recursively solve for optimal strategy using dynamic programming.
        
        Args:
            state: Current game state
            depth: Current recursion depth
            max_depth: Maximum recursion depth to prevent infinite loops
        
        Returns:
            Tuple of (maximum money achievable, list of optimal actions)
        """
        # Base cases
        if depth >= max_depth:
            return (state.money, [])
        
        if state.day > self.config.deadline:
            return (0.0, [])  # Failed - exceeded deadline
        
        if state.game_over:
            if state.success:
                return (state.money, [])
            else:
                return (0.0, [])  # Failed
        
        # Check memoization
        state_key = self.discretize_state(state)
        if state_key in self.memo:
            return self.memo[state_key]
        
        # Get possible actions
        actions = self.get_possible_actions(state)
        
        if not actions:
            # No valid actions - game over
            return (0.0, [])
        
        # Try each action and find the best one
        best_money = 0.0
        best_actions = []
        
        for action in actions:
            new_state = self.simulate_action(state, action)
            
            if new_state is None:
                continue
            
            # Recursively solve from new state
            future_money, future_actions = self.solve_recursive(new_state, depth + 1, max_depth)
            
            if future_money > best_money:
                best_money = future_money
                best_actions = [action] + future_actions
        
        # Memoize result
        self.memo[state_key] = (best_money, best_actions)
        
        return (best_money, best_actions)
    
    def solve(self) -> Tuple[float, List[Action]]:
        """Find optimal strategy for the game.
        
        Returns:
            Tuple of (maximum money achievable, list of optimal actions)
        """
        initial_state = GameState(
            money=self.config.initial_funds,
            position=self.map.start_id
        )
        
        return self.solve_recursive(initial_state)


def run_optimized_game():
    """Run the game with optimal strategy."""
    print("=" * 70)
    print("沙漠穿越游戏 - 最优策略求解器")
    print("Desert Crossing Game - Optimal Strategy Solver")
    print("=" * 70)
    
    # Create game configuration
    config = GameConfig(
        deadline=30,
        initial_funds=10000.0,
        weight_limit=1200.0,
    )
    
    # Create map and weather
    game_map = create_sample_map()
    weather_forecast = create_sample_weather(config.deadline + 5)
    
    print("\n正在计算最优策略...")
    print("(使用动态规划算法)\n")
    
    # Create optimizer
    optimizer = DesertCrossingOptimizer(config, game_map, weather_forecast)
    
    # Solve for optimal strategy
    max_money, optimal_actions = optimizer.solve()
    
    print(f"找到最优策略！")
    print(f"最大资金剩余: ¥{max_money:.2f}")
    print(f"总步数: {len(optimal_actions)}")
    
    # Execute the optimal strategy
    print("\n" + "=" * 70)
    print("执行最优策略:")
    print("=" * 70)
    
    game = DesertCrossingGame(config, game_map, weather_forecast)
    
    for i, action in enumerate(optimal_actions):
        print(f"\n步骤 {i+1}: {action}")
        
        # Execute action
        if action.type == "buy":
            game.purchase_resources(action.water_to_buy, action.food_to_buy)
        elif action.type == "move":
            game.move(action.target_location)
        elif action.type == "mine":
            game.stay(mine=True)
        elif action.type == "stay":
            game.stay(mine=False)
        
        game.print_state()
        
        if game.state.game_over:
            break
    
    # Final results
    print("\n" + "=" * 70)
    if game.state.success:
        print("✓ 游戏成功！")
        print(f"最终资金: ¥{game.state.money:.2f}")
        print(f"用时: {game.state.day} 天")
    else:
        print("✗ 游戏失败")
    print("=" * 70)


if __name__ == "__main__":
    run_optimized_game()
