# 沙漠穿越游戏 (Desert Crossing Game)

## 概述 (Overview)

这是一个基于**2020年全国大学生数学建模竞赛B题**的运筹学教学游戏。玩家需要在有限的资源（水、食物、资金）约束下，穿越沙漠并最大化剩余资金。

This is an Operations Research teaching game based on **Problem B of the 2020 National College Student Mathematical Modeling Competition**. Players need to cross a desert with limited resources (water, food, money) while maximizing remaining funds.

## 游戏规则 (Game Rules)

### 基本设定 (Basic Settings)

1. **时间单位**: 以天为单位，从第0天开始
2. **目标**: 在截止日期前到达终点，保留尽可能多的资金
3. **资源**: 水和食物（最小单位：箱）
4. **约束**: 每天携带的水和食物总重量不能超过负重上限

### 天气系统 (Weather System)

- **晴朗**: 正常活动
- **高温**: 正常活动
- **沙暴**: 必须停留原地，不能移动

### 行动规则 (Action Rules)

1. **移动**: 每天可移动到相邻区域，或原地停留
2. **资源消耗**:
   - 停留: 基础消耗量
   - 移动: 基础消耗量 × 2
   - 挖矿: 基础消耗量 × 3

### 地点类型 (Location Types)

1. **起点**: 可以用初始资金按基准价格购买资源（仅一次）
2. **矿山**: 可以挖矿获得资金（到达当天不能挖矿，沙暴日可以挖矿）
3. **村庄**: 可以购买资源（价格为基准价格的2倍）
4. **终点**: 到达后可退回剩余资源（退回价格为基准价格的50%）

### 经济系统 (Economic System)

- **初始资金**: ¥10,000
- **水价格**: ¥5/箱（基准），¥10/箱（村庄）
- **食物价格**: ¥10/箱（基准），¥20/箱（村庄）
- **挖矿收益**: ¥1,000/天
- **退回价格**: 基准价格 × 50%

## 文件说明 (Files)

### 1. `desert_crossing_game.py`

核心游戏引擎，包含：

- **GameConfig**: 游戏配置类
- **Location**: 地点类
- **Map**: 地图类
- **GameState**: 游戏状态类
- **DesertCrossingGame**: 主游戏引擎类

**运行示例游戏**:
```bash
python desert_crossing_game.py
```

### 2. `desert_crossing_optimizer.py`

优化求解器，使用动态规划算法寻找最优策略。

**特性**:
- 动态规划算法
- 状态空间离散化
- 记忆化搜索
- 最优策略计算

**运行优化器**:
```bash
python desert_crossing_optimizer.py
```

## 使用示例 (Usage Examples)

### 基本游戏示例

```python
from desert_crossing_game import (
    GameConfig, Map, Weather, DesertCrossingGame,
    create_sample_map, create_sample_weather
)

# 创建配置
config = GameConfig(
    deadline=30,
    initial_funds=10000.0,
    weight_limit=1200.0,
)

# 创建地图和天气预报
game_map = create_sample_map()
weather_forecast = create_sample_weather(30)

# 初始化游戏
game = DesertCrossingGame(config, game_map, weather_forecast)

# 购买资源
game.purchase_resources(water=100.0, food=150.0)

# 移动到相邻位置
game.move(target_location_id=1)

# 在矿山挖矿
game.stay(mine=True)

# 查看状态
game.print_state()
```

### 优化求解示例

```python
from desert_crossing_optimizer import DesertCrossingOptimizer
from desert_crossing_game import (
    GameConfig, create_sample_map, create_sample_weather
)

# 创建配置
config = GameConfig(deadline=30, initial_funds=10000.0)
game_map = create_sample_map()
weather_forecast = create_sample_weather(30)

# 创建优化器
optimizer = DesertCrossingOptimizer(config, game_map, weather_forecast)

# 求解最优策略
max_money, optimal_actions = optimizer.solve()

print(f"最大资金剩余: ¥{max_money:.2f}")
print(f"最优策略步数: {len(optimal_actions)}")
```

## 数学建模方法 (Mathematical Modeling Approaches)

### 1. 动态规划 (Dynamic Programming)

状态定义：`State = (day, position, water, food, money, flags)`

状态转移：
```
V(s) = max{V(s') | s' = next_state(s, action), action ∈ Actions(s)}
```

### 2. 线性规划 (Linear Programming)

可以将问题建模为混合整数线性规划 (MILP):

**决策变量**:
- `x[i,j,t]`: 第t天从位置i移动到位置j
- `w[t]`, `f[t]`: 第t天的水和食物数量
- `m[i,t]`: 第t天在位置i挖矿

**目标函数**:
```
maximize: money[T] + 0.5 * (5*w[T] + 10*f[T])
```

**约束条件**:
- 资源平衡约束
- 负重约束
- 时间约束
- 天气约束

### 3. 图搜索算法 (Graph Search)

- A* 搜索
- Dijkstra 算法
- 贪心启发式

## 扩展功能 (Extensions)

### 可能的扩展方向

1. **随机天气**: 天气不确定性，使用期望值优化
2. **复杂地图**: 多条路径、更多地点类型
3. **资源交易**: 在村庄出售资源
4. **多玩家模式**: 竞争或合作模式
5. **实时决策**: 未知天气下的在线决策
6. **GUI界面**: 图形用户界面
7. **强化学习**: 使用RL算法训练智能体

## 教学应用 (Educational Applications)

这个游戏可用于教学以下运筹学概念：

1. **动态规划**: 最优子结构、状态转移
2. **线性规划**: 约束优化、目标函数
3. **图论**: 最短路径、网络流
4. **决策理论**: 不确定性下的决策
5. **启发式算法**: 贪心、模拟退火
6. **资源管理**: 库存控制、供应链

## 性能优化 (Performance Optimization)

当前实现的优化器使用简单的动态规划，对于复杂场景可能较慢。改进方向：

1. **状态空间缩减**: 更粗粒度的离散化
2. **剪枝策略**: 提前终止无效分支
3. **启发式搜索**: A* 或其他启发式方法
4. **并行计算**: 多线程/多进程
5. **近似算法**: 遗传算法、模拟退火

## 参考资料 (References)

- 2020年全国大学生数学建模竞赛B题
- Dynamic Programming and Optimal Control (Dimitri Bertsekas)
- Introduction to Operations Research (Frederick Hillier)

## 许可证 (License)

本项目遵循 Apache License 2.0 开源协议。

## 联系方式 (Contact)

如有问题或建议，请通过 GitHub Issues 反馈。
