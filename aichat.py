import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MAX_MESSAGES = 20
HISTORY_FILE = "chat_history.json"
ARCHIVE_FILE = "chat_archive.json"
USER_CONFIG_FILE = "user.json"

def load_user_config():
    if os.path.exists(USER_CONFIG_FILE):
        try:
            with open(USER_CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return {"user_name": "", "ai_name": ""}
    return {"user_name": "", "ai_name": ""}

def save_user_config(config):
    with open(USER_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

def load_history():
    if os.path.exists(HISTORY_FILE):
        try:
            with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_history(messages):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def load_archive():
    if os.path.exists(ARCHIVE_FILE):
        try:
            with open(ARCHIVE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            return []
    return []

def save_archive(messages):
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(messages, f, ensure_ascii=False, indent=2)

def clear_archive():
    if os.path.exists(ARCHIVE_FILE):
        os.remove(ARCHIVE_FILE)

def summarize_messages(messages):
    if not messages:
        return ""
    
    content = "\n".join([f"{m['role']}: {m['content']}" for m in messages])
    prompt = f"""请总结以下对话历史，提取关键信息和要点：

{content}

总结要求：
1. 简洁明了，不超过200字
2. 保留重要人物、事件和关键信息
3. 用中文口语化表达
"""
    
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
    
    response = client.chat.completions.create(
        model="deepseek-v4-pro",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.3
    )
    
    return response.choices[0].message.content

ARCHIVE_THRESHOLD = 10

def trim_messages(messages):
    if len(messages) <= MAX_MESSAGES:
        return messages
    
    system_msgs = [m for m in messages if m["role"] == "system"]
    other_msgs = [m for m in messages if m["role"] != "system"]
    
    if len(other_msgs) > MAX_MESSAGES:
        excess_count = len(other_msgs) - MAX_MESSAGES
        excess_messages = other_msgs[:excess_count]
        remaining_messages = other_msgs[excess_count:]
        
        archive = load_archive()
        archive.extend(excess_messages)
        
        summary = summarize_messages(archive)
        if summary:
            summary_msg = add_timestamp({
                "role": "user",
                "content": f"【历史总结】{summary}"
            })
            remaining_messages.insert(0, summary_msg)
        
        clear_archive()
        
        return system_msgs + remaining_messages
    
    return system_msgs + other_msgs

def prepare_api_messages(messages):
    return [{k: v for k, v in m.items() if k in ["role", "content"]} for m in messages]

def deepseek_chat(messages, model="deepseek-v4-pro", temperature=0.7, max_tokens=None, user_name="", ai_name=""):
    api_key = os.environ.get('DEEPSEEK_API_KEY')
    if not api_key:
        raise ValueError("请设置 DEEPSEEK_API_KEY 环境变量")
    
    client = OpenAI(
        api_key=api_key,
        base_url="https://api.deepseek.com"
    )
    
    system_message = {
        "role": "system",
        "content": f"""你是一个友好的AI助手，名字叫{ai_name}。用户的名字是{user_name}，请在对话中使用这个名字称呼用户。
你的性格开朗、俏皮，喜欢用表情符号和可爱的语气。
保持回答简短有趣。
"""
    }
    
    api_messages = prepare_api_messages(messages)
    api_messages.insert(0, system_message)
    
    response = client.chat.completions.create(
        model=model,
        messages=api_messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=False,
        reasoning_effort="high",
        extra_body={"thinking": {"type": "enabled"}}
    )
    
    return response.choices[0].message.content

def add_timestamp(message):
    message["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return message

def main():
    user_config = load_user_config()
    user_name = user_config.get("user_name", "")
    ai_name = user_config.get("ai_name", "")
    
    if not user_name:
        user_name = input("请问你叫什么名字？").strip()
        while not user_name:
            user_name = input("请输入你的名字：").strip()
        
    if not ai_name:
        ai_name = input("那我该叫什么名字呢？").strip()
        while not ai_name:
            ai_name = input("请给我起个名字：").strip()
        
        user_config["user_name"] = user_name
        user_config["ai_name"] = ai_name
        save_user_config(user_config)
    
    print(f"\n欢迎回来，{user_name}！我是 {ai_name}～")
    print("输入 '退出' 退出程序\n")
    
    archive = load_archive()
    if archive:
        print(f"发现 {len(archive)} 条归档记录，正在总结...")
        summary = summarize_messages(archive)
        print(f"总结完成：{summary[:50]}...")
        clear_archive()
        
        messages = load_history()
        summary_msg = add_timestamp({
            "role": "user",
            "content": f"【历史总结】{summary}"
        })
        messages.insert(0, summary_msg)
        messages = trim_messages(messages)
        save_history(messages)
    else:
        messages = load_history()
    
    if len(messages) > MAX_MESSAGES:
        messages = messages[-MAX_MESSAGES:]
        save_history(messages)
    
    if messages:
        print(f"已加载历史记录（共 {len(messages)} 条消息）\n")
    
    while True:
        user_input = input(f"{user_name}: ").strip()
        
        if user_input == '退出':
            messages.append(add_timestamp({"role": "user", "content": "我要退出了，跟我说再见吧！"}))
            messages = trim_messages(messages)
            
            try:
                print(f"{ai_name}: ", end="", flush=True)
                response = deepseek_chat(messages, user_name=user_name, ai_name=ai_name)
                print(response)
                print()
                
                messages.append(add_timestamp({"role": "assistant", "content": response}))
                messages = trim_messages(messages)
                save_history(messages)
                print(f"对话已保存到 {HISTORY_FILE}")
            except Exception as e:
                print(f"错误: {e}\n")
                save_history(messages)
            break
        
        if not user_input:
            continue
        
        messages.append(add_timestamp({"role": "user", "content": user_input}))
        messages = trim_messages(messages)
        save_history(messages)
        
        try:
            print(f"{ai_name}: ", end="", flush=True)
            response = deepseek_chat(messages, user_name=user_name, ai_name=ai_name)
            print(response)
            print()
            
            messages.append(add_timestamp({"role": "assistant", "content": response}))
            messages = trim_messages(messages)
            save_history(messages)
        except Exception as e:
            print(f"错误: {e}\n")

if __name__ == "__main__":
    main()