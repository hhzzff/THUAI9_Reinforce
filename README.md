# THUAI9_Reinforce

这是一个基于 Python 的强化学习环境模拟器，专注于网格世界中的资源交易博弈。项目实现了符合 [Gymnasium](https://gymnasium.farama.org/) 标准的接口，允许使用主流强化学习算法（如 PPO）进行智能体训练，同时也支持（Windows 平台下的）手动控制测试。

## 核心功能 (Key Features)

- **Grid-World 经济模拟**: 包含地图探索、单位移动、以及在不同市场间利用价格波动买卖商品的核心逻辑。
- **自定义 Gymnasium 环境**: 提供了 `AI9GymEnv` 类，实现了标准的 `reset`, `step` 接口，并通过计算资产变化 (`money_diff`) 设计了奖励函数。
- **Stable-Baselines3 集成**: 提供了使用 [Stable-Baselines3](https://stable-baselines3.readthedocs.io/) 的 PPO 算法进行训练的完整示例 (`train_demo.py`)。
- **高度可配置**: 通过 `config/settings.py` 可以轻松调整地图尺寸、物品类型、价格波动逻辑等参数。

## 项目结构 (File Structure)

| 文件 | 说明 |
| :--- | :--- |
| `main.py` | 游戏核心逻辑实现，包含 `GameEnv`, `Market`, `Unit` 等类。 |
| `ai_gym_env.py` | Gymnasium 环境封装，负责 Observation 编码和 Reward 计算，适配 RL 框架。 |
| `train_demo.py` | 强化学习训练脚本，包含自定义的回调函数用于周期性评估模型。 |
| `control.py` | 人类玩家手动控制脚本，用于调试游戏逻辑和体验环境。 |
| `config/settings.py` | 全局配置文件，定义地图大小、资源类型、物理规则等。 |

## 安装与运行 (Installation & Usage)

本项目推荐使用 **uv** 进行高效的依赖管理。

### 1. 环境准备

如果您的环境中尚未安装 uv，请先安装：

```bash
pip install uv
```

同步项目的依赖环境：

```bash
uv sync
```

### 2. 运行脚本

#### 启动训练 (Reinforcement Learning)

使用以下命令启动 PPO 算法的模型训练 demo：

```bash
uv run train_demo.py
```

#### 启动手动控制 (Manual Control)

> **⚠️ 平台限制警告**  
> 体验控制台控制界面 (`control.py`) 依赖 `msvcrt` 库，因此**仅支持 Windows 系统**运行。  
> 请勿在 Linux/macOS 环境下尝试运行此脚本，否则会因缺少依赖报错。

在 Windows 环境下，使用以下命令启动控制台交互界面，通过键盘控制单位移动和交易：

```bash
uv run control.py
```

## 配置 (Configuration)

您可以修改 `config/settings.py` 来改变实验设定，例如：
- `MAP_WIDTH` / `MAP_HEIGHT`: 修改地图尺寸。
- `TIME_STEP_DURATION`: 修改时间步长（影响模拟速度）。
- `INITIAL_MONEY`: 修改初始资金。
- `PRODUCTS`: 修改商品类型和价格波动范围。
