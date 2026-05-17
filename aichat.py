import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MAX_MESSAGES = 20
ARCHIVE_MAX_SUMMARIES = 10
DEEPSEEK_MODEL = os.environ.get('DEEPSEEK_MODEL')
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

def save_archive(summaries):
    with open(ARCHIVE_FILE, "w", encoding="utf-8") as f:
        json.dump(summaries, f, ensure_ascii=False, indent=2)

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
        model=DEEPSEEK_MODEL,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=300,
        temperature=0.3
    )
    
    return response.choices[0].message.content

def trim_messages(messages):
    if len(messages) <= MAX_MESSAGES:
        return messages
    
    system_msgs = [m for m in messages if m["role"] == "system"]
    other_msgs = [m for m in messages if m["role"] != "system"]
    
    latest_summary = None
    if other_msgs and "【历史总结】" in other_msgs[0].get("content", ""):
        latest_summary = other_msgs[0]
        other_msgs = other_msgs[1:]
    
    if len(other_msgs) <= MAX_MESSAGES:
        return system_msgs + [latest_summary] + other_msgs if latest_summary else system_msgs + other_msgs
    
    excess_count = len(other_msgs) - MAX_MESSAGES
    excess_messages = other_msgs[:excess_count]
    remaining_messages = other_msgs[excess_count:]
    
    archive = load_archive()
    
    raw_in_archive = [m for m in archive if "【历史总结】" not in m.get("content", "")]
    
    all_raw_messages = raw_in_archive + excess_messages
    
    if len(all_raw_messages) >= ARCHIVE_MAX_SUMMARIES:
        summary = summarize_messages(all_raw_messages)
        if summary:
            summary_msg = {
                "role": "user",
                "content": f"【历史总结】{summary}",
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            existing_summaries = [m for m in archive if "【历史总结】" in m.get("content", "")]
            
            if len(existing_summaries) >= ARCHIVE_MAX_SUMMARIES:
                mega_summary = summarize_messages(existing_summaries + [summary_msg])
                if mega_summary:
                    archive = [{
                        "role": "user",
                        "content": f"【历史总结】{mega_summary}",
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    }]
                else:
                    archive = existing_summaries[-(ARCHIVE_MAX_SUMMARIES-1):] + [summary_msg]
            else:
                archive = existing_summaries + [summary_msg]
            
            save_archive(archive)
    else:
        archive.extend(excess_messages)
        save_archive(archive)
    
    if latest_summary:
        return system_msgs + [latest_summary] + remaining_messages
    else:
        return system_msgs + remaining_messages

def prepare_api_messages(messages):
    return [{k: v for k, v in m.items() if k in ["role", "content"]} for m in messages]

def deepseek_chat(messages, model=DEEPSEEK_MODEL, temperature=0.7, max_tokens=None, user_name="", ai_name=""):
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
    if not DEEPSEEK_MODEL:
        raise ValueError("请在 .env 文件中设置 DEEPSEEK_MODEL 配置")
    
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
    
    messages = load_history()
    
    archive = load_archive()
    summaries_in_archive = [m for m in archive if "【历史总结】" in m.get("content", "")]
    
    if summaries_in_archive:
        print(f"发现 {len(summaries_in_archive)} 条历史总结")
    
    messages = trim_messages(messages)
    
    if summaries_in_archive:
        latest_summary = summaries_in_archive[-1]
        messages.insert(0, latest_summary)
    
    save_history(messages)
    
    if messages:
        print(f"已加载历史记录（共 {len(messages)} 条消息）\n")
    
    while True:
        user_input = input(f"{user_name}: ").strip()
        
        if user_input == '退出':
            messages.append(add_timestamp({"role": "user", "content": "我要退出了，跟我说再见吧！"}))
            
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
