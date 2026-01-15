import math
import random
from dataclasses import dataclass
import copy
from config.settings import *

@dataclass
class Point:
    x: int
    y: int

    def distance_to(self, other: 'Point') -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)

class Market:
    def __init__(self, x, y, name="Market"):
        self.pos = Point(x, y)
        self.name = name
        # 模拟价格函数 Price(t)，这里简单用正弦波模拟波动
        self.price_funcs = {
            p_name: lambda t, base=p["val_range"][0], top=p["val_range"][1]: 
                base + (top - base) * (0.5 * (math.sin(t) + 1))
            for p_name, p in PRODUCTS.items()
        }

    def get_price(self, product_name, t):
        return self.price_funcs[product_name](t)

class Unit:
    def __init__(self, u_id, x, y):
        self.id = u_id
        self.pos = Point(x, y)
        self.inventory = {p: 0 for p in PRODUCTS}
        self.busy_ticks = 0  # 剩余忙碌时间 (ticks)
        self.state = "idle"  # idle, moving, loading, selling

    def move(self, direction: str):
        if direction == U_ACT_MOVE_UP:
            self.pos.x = max(0, self.pos.x - 1)
        elif direction == U_ACT_MOVE_DOWN:
            self.pos.x = min(MAP_HEIGHT - 1, self.pos.x + 1)
        elif direction == U_ACT_MOVE_LEFT:
            self.pos.y = max(0, self.pos.y - 1)
        elif direction == U_ACT_MOVE_RIGHT:
            self.pos.y = min(MAP_WIDTH - 1, self.pos.y + 1)
        return True

class GameEnv:
    """
    对外暴露: reset(), step(commands)
    """
    def __init__(self):
        self.reset()

    def reset(self):
        self.time = 0
        self.money = INITIAL_MONEY
        # 单位结构: id, x, y, load_count, load_type, state, target_x, target_y
        self.units = [Unit(0, 0, 0)]
        # 初始化市场 (简化位置)
        self.markets = []
        self.map_grid = [
            [GRID_TYPE_EMPTY for _ in range(MAP_HEIGHT)]
                for _ in range(MAP_WIDTH)
        ]
        self._init_map()
        return self._get_observation()

    def _init_map(self):
        # 随机生成几个市场
        for i in range(3):
            mx, my = random.randint(0, MAP_HEIGHT - 1), random.randint(0, MAP_WIDTH - 1)
            # 避免重叠
            while self.map_grid[mx][my] != GRID_TYPE_EMPTY:
                 mx, my = random.randint(0, MAP_HEIGHT - 1), random.randint(0, MAP_WIDTH - 1)
            
            self.map_grid[mx][my] = GRID_TYPE_MARKET
            self.markets.append(Market(mx, my, f"Market_{i}"))

    def step(self, command: int):
        self.time += 0.25

        self._handle_command(command)

        return self._get_observation()

    def _handle_command(self, cmd):
        u = self.units[0]
        if u.busy_ticks > 0:
            u.busy_ticks -= 1
            if u.busy_ticks == 0:
                self._complete_transaction(u)
            return
        if cmd == U_ACT_WAIT: u.state = "idle"
        elif cmd >= U_ACT_MOVE_UP and cmd <= U_ACT_MOVE_RIGHT:
            u.state = "moving"
            u.move(cmd)
        elif cmd == U_ACT_LOAD_0:
            # 尝试开始购买
            if self._can_buy(u):
                u.state = "loading"
                u.busy_ticks = int(PRODUCT_TRANSACTION_TIME / TIME_STEP_DURATION)
        elif cmd == U_ACT_SELL_ALL:
            # 尝试开始出售
            if self._can_sell(u):
                u.state = "selling"
                u.busy_ticks = int(PRODUCT_TRANSACTION_TIME / TIME_STEP_DURATION)


    def _complete_transaction(self, unit: Unit):
        """持续时间结束后执行实际的交易逻辑"""
        if unit.state == "loading":
            self._execute_buy(unit)
        elif unit.state == "selling":
            self._execute_sell(unit)

    def _find_nearby_market(self, unit: Unit):
        """查找单位当前位置附近的有效市场"""
        for market in self.markets:
            if unit.pos.distance_to(market.pos) <= 1:
                return market
        return None

    def _can_buy(self, unit: Unit) -> bool:
        market = self._find_nearby_market(unit)
        if not market: return False

        # 检查库存
        current_load = sum(unit.inventory.values())
        if current_load >= UNIT_CAPACITY: return False
        
        product_id = PRODUCT_SEMICONDUCTOR
        # 检查资金 (预查)
        if self.money < market.get_price(product_id, self.time): return False
        
        return True

    def _can_sell(self, unit: Unit) -> bool:
        market = self._find_nearby_market(unit)
        return market is not None

    def _execute_buy(self, unit: Unit):
        # 再次检查市场存在性（虽然目前市场不移动）
        market = self._find_nearby_market(unit)
        if not market: return

        product_id = PRODUCT_SEMICONDUCTOR
        price = market.get_price(product_id, self.time)
        
        # 再次检查资金并执行扣款
        if self.money >= price:
            self.money -= price
            unit.inventory[product_id] += 1

    def _execute_sell(self, unit: Unit):
        market = self._find_nearby_market(unit)
        if not market: return

        revenue = 0
        for p_id, count in unit.inventory.items():
            if count > 0:
                price = market.get_price(p_id, self.time)
                revenue += price * count
                unit.inventory[p_id] = 0
        
        self.money += revenue
    
    def _process_buy(self, unit: Unit):
        market = self._find_nearby_market(unit)
        if not market: return # 附近无市场

        # 检查库存
        current_load = sum(unit.inventory.values())
        if current_load >= UNIT_CAPACITY: return # 库存已满
        
        product_id = PRODUCT_SEMICONDUCTOR # 简化为单一产品

        if self.money < market.get_price(product_id, self.time): return # 资金不足

        # 执行交易
        price = market.get_price(product_id, self.time)
        self.money -= price
        unit.inventory[product_id] += 1

    def _process_sell(self, unit: Unit):
        market = self._find_nearby_market(unit)
        if not market: return

        revenue = 0
        for p_id, count in unit.inventory.items():
            if count > 0:
                price = market.get_price(p_id, self.time)
                revenue += price * count
                unit.inventory[p_id] = 0
        
        self.money += revenue

    def _get_observation(self):
        # 返回深拷贝的状态字典，防止玩家修改
        return {
            "time": copy.deepcopy(self.time),
            "units": [copy.deepcopy(u) for u in self.units],
            "markets": copy.deepcopy(self.markets),
            "map": copy.deepcopy(self.map_grid),
        }