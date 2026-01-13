import os
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from ai_gym_env import AI9GymEnv

def train():
    # 1. 创建环境
    env = AI9GymEnv()
    
    # 可选：检查环境是否符合 Gym 标准 (Debug 用)
    # check_env(env) 

    # 2. 定义模型
    # MlpPolicy: 适用于向量输入的神经网络 (即我们 _encode_obs 返回的数组)
    model = PPO("MlpPolicy", env, verbose=1, 
                learning_rate=0.0003,
                n_steps=2048,
                batch_size=2,
                gamma=0.9)

    print("开始训练...")
    # 3. 训练 (time_steps 越大越强，建议 100,000 以上)
    model.learn(total_timesteps=50000)
    
    # 4. 保存模型
    model_path = "models/ppo_ai9_basic"
    os.makedirs(os.path.dirname(model_path), exist_ok=True)
    model.save(model_path)
    print(f"模型已保存至 {model_path}")

def test():
    # 测试训练好的模型
    env = AI9GymEnv()
    model = PPO.load("models/ppo_ai9_basic")
    
    obs, _ = env.reset()
    total_reward = 0
    
    for i in range(500):
        # deterministic=True 让模型输出最确定的动作，而不是随机探索
        action, _states = model.predict(obs, deterministic=True)
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        
        if (i+1) % 50 == 0:
            env.render()
            
        if terminated or truncated:
            break
            
    print(f"测试结束，总得分 (Reward): {total_reward:.2f}")

if __name__ == "__main__":
    train()
    # 训练完成后直接运行测试
    test()