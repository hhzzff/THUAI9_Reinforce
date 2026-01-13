import gymnasium as gym
import numpy as np
from gymnasium import spaces
from main import GameEnv
from config.settings import *

class AI9GymEnv(gym.Env):
    """
    将 GameEnv 适配为 Gymnasium 标准环境
    通信协议：
    - Input (Action): Discrete(7)
    - Output (Observation): Box(float32) 归一化的向量
    """
    metadata = {"render_modes": ["console"]}

    def __init__(self):
        super().__init__()
        self.game = GameEnv()
        
        # 动作空间：0-6 (对应 settings.py 中的定义)
        self.action_space = spaces.Discrete(7)

        # 观察空间：定义 AI 能看到的特征向量 (归一化到 0-1 或 -1 到 1 之间)
        # 1. Unit X (Norm)
        # 2. Unit Y (Norm)
        # 3. Busy State (0-1)
        # 4. Inventory Volume (0-1)
        # 5. Money (Log scale or Norm)
        # 6. Nearest Market Dist X
        # 7. Nearest Market Dist Y
        # 8. Market Price (Normalized)
        self.observation_space = spaces.Box(low=-1.0, high=1.0, shape=(8,), dtype=np.float32)
        
        self.max_steps = 1000 # 限制每局最大步数

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        obs_dict = self.game.reset()
        self.current_step = 0
        self.prev_money = self.game.money
        return self._encode_obs(obs_dict), {}

    def step(self, action):
        observation = self.game.step(action)
        self.current_step += 1
        
        # --- 奖励函数设计 (Reward Engineering) ---
        reward = 0.0
        
        # 1. 赚钱奖励: 这一步赚的钱 (如果是负数则是花钱)
        money_diff = self.game.money - self.prev_money
        if money_diff > 0:
            reward += money_diff * 0.1 # 销售奖励
        elif money_diff < 0:
            reward += money_diff * 0.01 # 购买成本产生的微小负反馈(可选)
            
        # 2. 时间惩罚: 鼓励尽快行动
        reward -= 0.01
        
        # 更新状态
        self.prev_money = self.game.money
        
        # 结束条件
        terminated = False
        truncated = self.current_step >= self.max_steps
        
        return self._encode_obs(observation), reward, terminated, truncated, {}

    def _encode_obs(self, obs_raw):
        """将复杂的字典状态转化为扁平的 Numpy 数组"""
        u = self.game.units[0]
        
        # 找到最近的市场信息
        nearest_m = None
        min_dist = 999
        for m in self.game.markets:
            d = u.pos.distance_to(m.pos)
            if d < min_dist:
                min_dist = d
                nearest_m = m
        
        # 构建特征
        features = []
        
        # 1. 自身位置 (归一化 0~1)
        features.append(u.pos.x / MAP_HEIGHT)
        features.append(u.pos.y / MAP_WIDTH)
        
        # 2. 状态
        features.append(u.busy_ticks / 10.0) # 假设最大忙碌时间约为4-10
        item_count = sum(u.inventory.values())
        features.append(item_count / UNIT_CAPACITY)
        
        # 3. 资金 (简化处理：是否足够买入)
        # 简单的 0/1 表示是否有钱买基本半导体
        can_afford = 1.0 if self.game.money >= 40 else 0.0
        features.append(can_afford)
        
        # 4. 相对市场的向量 (归一化 -1~1)
        if nearest_m:
            dx = (nearest_m.pos.x - u.pos.x) / MAP_HEIGHT
            dy = (nearest_m.pos.y - u.pos.y) / MAP_WIDTH
            price = nearest_m.get_price(PRODUCT_SEMICONDUCTOR, self.game.time)
            norm_price = (price - 40) / (120 - 40) # 基于 settings 里的 range
        else:
            dx, dy, norm_price = 0, 0, 0
            
        features.append(dx)
        features.append(dy)
        features.append(norm_price)
        
        return np.array(features, dtype=np.float32)

    def render(self):
        # 简单打印当前步数和金钱
        print(f"Step: {self.current_step}, Money: {self.game.money:.2f}")
