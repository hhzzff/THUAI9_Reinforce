# ==========================================
# 1. 地图与环境设置 (Map & Environment)
# ==========================================

# 地图尺寸
MAP_WIDTH = 5
MAP_HEIGHT = 5

# 地块类型编码 (Grid Types)
GRID_TYPE_EMPTY = 0    # 空地
GRID_TYPE_OBSTACLE = 1 # 障碍
GRID_TYPE_MARKET = 2   # 市场

# 时间设置
# 物理规则：移速 2格/s。为了方便离散模拟，定义 1 Tick = 0.25s。
# 此时单位速度为 1格/2Tick。
TIME_STEP_DURATION = 0.25 # 秒

# ==========================================
# 2. 玩家与单位设置 (Player & Units)
# ==========================================

# 初始资源
INITIAL_MONEY = 1000

# 移动单位属性 (Unit)
UNIT_SPEED = 2      # 格/s (对应 1格/2Tick)

# 单位装载容量
UNIT_CAPACITY = 1   # 件

# ==========================================
# 3. 产品属性 (Products)
# ==========================================

# 产品ID定义
PRODUCT_SEMICONDUCTOR = 0

# 买入、卖出时间
PRODUCT_TRANSACTION_TIME = 1  # Second

# 产品详细配置表
# key: 产品ID
# value: dict(name, base_val_range)
PRODUCTS = {
    PRODUCT_SEMICONDUCTOR: {
        "name": "半导体",
        "val_range": (40, 120),
    },
}

# ==========================================
# 4. 动作空间定义 (Action Space)
# ==========================================

# --- 单位动作 (Unit Actions) ---
# 离散空间大小: 7
# 0: 原地待命
# 1-4: 移动 (上, 下, 左, 右)
# 5: 购买商品
# 6: 出售商品

U_ACT_WAIT = 0

# 移动指令 (注意: 坐标系 x垂直向下, y水平向右)
U_ACT_MOVE_UP = 1    # x - 1
U_ACT_MOVE_DOWN = 2  # x + 1
U_ACT_MOVE_LEFT = 3  # y - 1
U_ACT_MOVE_RIGHT = 4 # y + 1

# 装载指令
U_ACT_LOAD_0 = 5

# 出售指令
U_ACT_SELL_ALL = 6

# ==========================================
# 5. 积分规则 (Scoring)
# ==========================================
SCORE_SALES_FACTOR = 10.0 # 销售额 x 10