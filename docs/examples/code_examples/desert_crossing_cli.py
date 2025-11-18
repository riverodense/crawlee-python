"""
Desert Crossing Game - Interactive CLI Interface

An interactive command-line interface for playing the Desert Crossing Game.
"""

import sys
import os
from typing import Optional

# Add current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from desert_crossing_game import (
    GameConfig, Map, Weather, DesertCrossingGame, Location, LocationType,
    create_sample_map, create_sample_weather
)


class DesertCrossingCLI:
    """Interactive CLI for Desert Crossing Game."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.game: Optional[DesertCrossingGame] = None
        self.config: Optional[GameConfig] = None
        self.game_map: Optional[Map] = None
    
    def print_banner(self) -> None:
        """Print game banner."""
        print("\n" + "="*70)
        print("       沙漠穿越游戏 - Desert Crossing Game")
        print("     2020年全国大学生数学建模竞赛 B题")
        print("="*70)
    
    def print_help(self) -> None:
        """Print available commands."""
        print("\n可用命令 (Available Commands):")
        print("  status    - 查看当前状态 (View current status)")
        print("  map       - 查看地图 (View map)")
        print("  weather   - 查看天气预报 (View weather forecast)")
        print("  buy       - 购买资源 (Buy resources)")
        print("  move      - 移动到其他位置 (Move to another location)")
        print("  stay      - 停留原地 (Stay at current location)")
        print("  mine      - 在矿山挖矿 (Mine at mine location)")
        print("  help      - 显示帮助 (Show help)")
        print("  quit      - 退出游戏 (Quit game)")
    
    def setup_game(self) -> None:
        """Setup a new game."""
        print("\n游戏设置 (Game Setup)")
        print("-" * 70)
        
        # Get configuration
        print("\n使用默认设置? (Use default settings?) [Y/n]: ", end="")
        use_default = input().strip().lower()
        
        if use_default in ['', 'y', 'yes']:
            self.config = GameConfig()
            self.game_map = create_sample_map()
            weather_forecast = create_sample_weather(self.config.deadline + 5)
        else:
            # Custom configuration
            print("\n初始资金 (Initial funds) [10000]: ", end="")
            initial_funds = input().strip()
            initial_funds = float(initial_funds) if initial_funds else 10000.0
            
            print("截止日期 (Deadline in days) [30]: ", end="")
            deadline = input().strip()
            deadline = int(deadline) if deadline else 30
            
            print("负重上限 (Weight limit) [1200]: ", end="")
            weight_limit = input().strip()
            weight_limit = float(weight_limit) if weight_limit else 1200.0
            
            self.config = GameConfig(
                deadline=deadline,
                initial_funds=initial_funds,
                weight_limit=weight_limit
            )
            
            self.game_map = create_sample_map()
            weather_forecast = create_sample_weather(deadline + 5)
        
        # Initialize game
        self.game = DesertCrossingGame(self.config, self.game_map, weather_forecast)
        
        print("\n游戏初始化成功！(Game initialized successfully!)")
        self.show_status()
    
    def show_status(self) -> None:
        """Show current game status."""
        if not self.game:
            print("游戏未初始化 (Game not initialized)")
            return
        
        self.game.print_state()
        
        # Show current location info
        current_loc = self.game.map.locations[self.game.state.position]
        print(f"\n当前位置类型: {current_loc.type.value}")
        
        # Show available actions
        print("\n可能的行动:")
        if current_loc.type == LocationType.START and not self.game.state.purchased_at_start:
            print("  - 购买资源 (buy)")
        if current_loc.type == LocationType.VILLAGE:
            print("  - 购买资源 (buy)")
        if current_loc.type == LocationType.MINE and not self.game.state.arrived_at_mine_today:
            print("  - 挖矿 (mine)")
        print("  - 停留 (stay)")
        
        weather = self.game.get_weather(self.game.state.day)
        if weather != Weather.SANDSTORM:
            print("  - 移动到相邻位置 (move)")
            for neighbor_id in current_loc.neighbors:
                neighbor = self.game.map.locations[neighbor_id]
                print(f"      位置 {neighbor_id}: {neighbor.type.value}")
    
    def show_map(self) -> None:
        """Show game map."""
        if not self.game_map:
            print("地图未加载 (Map not loaded)")
            return
        
        print("\n地图 (Map):")
        print("-" * 70)
        for loc_id, loc in self.game_map.locations.items():
            marker = " <-- 当前位置" if self.game and loc_id == self.game.state.position else ""
            neighbors = [f"{n}({self.game_map.locations[n].type.value})" 
                        for n in loc.neighbors]
            print(f"  [{loc_id}] {loc.type.value} (坐标: {loc.x},{loc.y}){marker}")
            if neighbors:
                print(f"       相邻: {', '.join(neighbors)}")
    
    def show_weather(self) -> None:
        """Show weather forecast."""
        if not self.game:
            print("游戏未初始化 (Game not initialized)")
            return
        
        print("\n天气预报 (Weather Forecast):")
        print("-" * 70)
        current_day = self.game.state.day
        for day in range(current_day, min(current_day + 10, len(self.game.weather_forecast))):
            weather = self.game.weather_forecast[day]
            marker = " <-- 今天" if day == current_day else ""
            print(f"  第 {day} 天: {weather.value}{marker}")
    
    def do_buy(self) -> None:
        """Handle buy action."""
        if not self.game:
            print("游戏未初始化 (Game not initialized)")
            return
        
        current_loc = self.game.map.locations[self.game.state.position]
        at_village = current_loc.type == LocationType.VILLAGE
        at_start = current_loc.type == LocationType.START
        
        if not (at_village or (at_start and not self.game.state.purchased_at_start)):
            print("当前位置无法购买资源 (Cannot buy resources at current location)")
            return
        
        # Show prices
        water_price = self.game.config.get_water_price(at_village)
        food_price = self.game.config.get_food_price(at_village)
        
        print(f"\n当前价格 (Current prices):")
        print(f"  水: ¥{water_price:.2f}/箱 (重量: {self.game.config.water_weight} kg/箱)")
        print(f"  食物: ¥{food_price:.2f}/箱 (重量: {self.game.config.food_weight} kg/箱)")
        print(f"\n当前资金: ¥{self.game.state.money:.2f}")
        print(f"当前负重: {self.game.state.get_total_weight(self.game.config):.1f}/{self.game.config.weight_limit:.1f} kg")
        
        # Get purchase amount
        print("\n购买水的数量 (箱) [0]: ", end="")
        water_input = input().strip()
        water = float(water_input) if water_input else 0.0
        
        print("购买食物的数量 (箱) [0]: ", end="")
        food_input = input().strip()
        food = float(food_input) if food_input else 0.0
        
        if water == 0 and food == 0:
            print("取消购买 (Purchase cancelled)")
            return
        
        # Calculate cost
        cost = water * water_price + food * food_price
        new_weight = (self.game.state.water + water) * self.game.config.water_weight + \
                     (self.game.state.food + food) * self.game.config.food_weight
        
        print(f"\n总花费: ¥{cost:.2f}")
        print(f"购买后负重: {new_weight:.1f}/{self.game.config.weight_limit:.1f} kg")
        print(f"购买后资金: ¥{self.game.state.money - cost:.2f}")
        
        print("\n确认购买? (Confirm purchase?) [Y/n]: ", end="")
        confirm = input().strip().lower()
        
        if confirm in ['', 'y', 'yes']:
            if self.game.purchase_resources(water, food):
                print("✓ 购买成功！(Purchase successful!)")
            else:
                print("✗ 购买失败！资金不足或超重 (Purchase failed! Insufficient funds or overweight)")
    
    def do_move(self) -> None:
        """Handle move action."""
        if not self.game:
            print("游戏未初始化 (Game not initialized)")
            return
        
        weather = self.game.get_weather(self.game.state.day)
        if weather == Weather.SANDSTORM:
            print("沙暴天气无法移动！(Cannot move during sandstorm!)")
            return
        
        current_loc = self.game.map.locations[self.game.state.position]
        
        if not current_loc.neighbors:
            print("当前位置没有相邻位置 (No adjacent locations)")
            return
        
        print("\n可移动的位置 (Available destinations):")
        for i, neighbor_id in enumerate(current_loc.neighbors):
            neighbor = self.game.map.locations[neighbor_id]
            print(f"  {i+1}. 位置 {neighbor_id}: {neighbor.type.value}")
        
        print("\n选择目标位置 (序号) [1]: ", end="")
        choice = input().strip()
        
        if not choice:
            choice = "1"
        
        try:
            index = int(choice) - 1
            if 0 <= index < len(current_loc.neighbors):
                target_id = current_loc.neighbors[index]
                
                # Show consumption based on current weather
                weather = self.game.get_weather(self.game.state.day)
                water_consumed, food_consumed = self.game.config.get_consumption(weather, self.game.config.moving_multiplier)
                
                print(f"\n移动消耗: {water_consumed:.1f}箱水, {food_consumed:.1f}箱食物")
                print(f"移动后剩余: {self.game.state.water - water_consumed:.1f}箱水, {self.game.state.food - food_consumed:.1f}箱食物")
                
                if self.game.move(target_id):
                    print(f"✓ 成功移动到位置 {target_id}！")
                    
                    if self.game.state.game_over:
                        if self.game.state.success:
                            print("\n" + "="*70)
                            print("🎉 恭喜！成功到达终点！(Congratulations! Reached destination!)")
                            print(f"最终资金: ¥{self.game.state.money:.2f}")
                            print(f"用时: {self.game.state.day} 天")
                            print("="*70)
                        else:
                            print("\n" + "="*70)
                            print("😞 游戏失败！(Game Over!)")
                            print("="*70)
                else:
                    print("✗ 移动失败！资源不足 (Move failed! Insufficient resources)")
            else:
                print("无效的选择 (Invalid choice)")
        except ValueError:
            print("无效的输入 (Invalid input)")
    
    def do_stay(self) -> None:
        """Handle stay action."""
        if not self.game:
            print("游戏未初始化 (Game not initialized)")
            return
        
        weather = self.game.get_weather(self.game.state.day)
        water_consumed, food_consumed = self.game.config.get_consumption(weather, 1.0)
        
        print(f"\n停留消耗: {water_consumed:.1f}箱水, {food_consumed:.1f}箱食物")
        print(f"停留后剩余: {self.game.state.water - water_consumed:.1f}箱水, {self.game.state.food - food_consumed:.1f}箱食物")
        
        print("\n确认停留? (Confirm stay?) [Y/n]: ", end="")
        confirm = input().strip().lower()
        
        if confirm in ['', 'y', 'yes']:
            if self.game.stay(mine=False):
                print("✓ 停留成功！")
            else:
                print("✗ 停留失败！资源不足或超过截止日期 (Stay failed!)")
    
    def do_mine(self) -> None:
        """Handle mine action."""
        if not self.game:
            print("游戏未初始化 (Game not initialized)")
            return
        
        current_loc = self.game.map.locations[self.game.state.position]
        
        if current_loc.type != LocationType.MINE:
            print("当前位置不是矿山！(Current location is not a mine!)")
            return
        
        if self.game.state.arrived_at_mine_today:
            print("到达矿山当天不能挖矿！(Cannot mine on arrival day!)")
            return
        
        weather = self.game.get_weather(self.game.state.day)
        water_consumed, food_consumed = self.game.config.get_consumption(weather, self.game.config.mining_multiplier)
        
        print(f"\n挖矿消耗: {water_consumed:.1f}箱水, {food_consumed:.1f}箱食物")
        print(f"挖矿收益: ¥{self.game.config.mine_base_income:.2f}")
        print(f"挖矿后剩余: {self.game.state.water - water_consumed:.1f}箱水, {self.game.state.food - food_consumed:.1f}箱食物")
        print(f"挖矿后资金: ¥{self.game.state.money + self.game.config.mine_base_income:.2f}")
        
        print("\n确认挖矿? (Confirm mining?) [Y/n]: ", end="")
        confirm = input().strip().lower()
        
        if confirm in ['', 'y', 'yes']:
            if self.game.stay(mine=True):
                print(f"✓ 挖矿成功！获得 ¥{self.game.config.mine_base_income:.2f}")
            else:
                print("✗ 挖矿失败！资源不足 (Mining failed! Insufficient resources)")
    
    def run(self) -> None:
        """Run the interactive CLI."""
        self.print_banner()
        print("\n欢迎来到沙漠穿越游戏！(Welcome to Desert Crossing Game!)")
        
        # Setup game
        self.setup_game()
        self.print_help()
        
        # Main game loop
        while self.game and not self.game.state.game_over:
            print("\n" + "-"*70)
            print("输入命令 (Enter command): ", end="")
            command = input().strip().lower()
            
            if command == "quit" or command == "exit" or command == "q":
                print("\n感谢游戏！(Thanks for playing!)")
                break
            elif command == "help" or command == "h" or command == "?":
                self.print_help()
            elif command == "status" or command == "s":
                self.show_status()
            elif command == "map" or command == "m":
                self.show_map()
            elif command == "weather" or command == "w":
                self.show_weather()
            elif command == "buy" or command == "b":
                self.do_buy()
            elif command == "move":
                self.do_move()
            elif command == "stay":
                self.do_stay()
            elif command == "mine":
                self.do_mine()
            elif command == "":
                continue
            else:
                print(f"未知命令: {command}. 输入 'help' 查看帮助.")
        
        if self.game and self.game.state.game_over:
            print("\n游戏结束！(Game ended!)")


def main():
    """Main entry point."""
    cli = DesertCrossingCLI()
    try:
        cli.run()
    except KeyboardInterrupt:
        print("\n\n游戏被中断 (Game interrupted)")
    except Exception as e:
        print(f"\n错误 (Error): {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
