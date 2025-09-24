#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
英语音标单词提取和下载脚本

此脚本会自动访问英语音标网站，从d1.html到d48.html提取单词信息
并下载相关单词发音到words-voice目录
"""

import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import logging
import json

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("extract_words.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 确保目录存在
def ensure_directories():
    """确保words-voice目录存在"""
    if not os.path.exists('words-voice'):
        os.makedirs('words-voice')
        logger.info(f"已创建目录: words-voice")

# 获取页面内容
def get_page_content(url):
    """获取网页内容"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text
    except Exception as e:
        logger.error(f"获取页面 {url} 失败: {str(e)}")
        return None

# 从页面提取单词信息
def extract_words_from_page(page_content, page_id):
    """从页面内容中提取单词信息"""
    words = []
    word_audio_urls = {}
    
    if not page_content:
        return words, word_audio_urls
    
    soup = BeautifulSoup(page_content, 'html.parser')
    
    try:
        # 查找所有audio标签，提取单词和URL
        audio_tags = soup.find_all('audio')
        for audio in audio_tags:
            if audio.get('src'):
                audio_url = audio.get('src')
                # 使用正则表达式从src中提取单词名
                import re
                # 匹配路径中的单词名，例如 words/bird.aac 中的 bird
                match = re.search(r'/([^/]+)\.(?:aac|mp3|wav)', audio_url)
                if match:
                    word = match.group(1)
                    words.append(word)
                    word_audio_urls[word] = audio_url
                else:
                    # 如果正则表达式没有匹配到，尝试使用id作为备选方案
                    if audio.get('id'):
                        word = audio.get('id')
                        words.append(word)
                        word_audio_urls[word] = audio_url
        
        # 如果没有找到足够的单词，尝试其他方式查找
        if len(words) < 2:
            # 查找单词表格或列表
            word_elements = soup.find_all(['td', 'li', 'span'], class_=lambda x: x and ('word' in x or 'pronunciation' in x))
            for element in word_elements:
                text = element.text.strip().lower()
                if text and len(text) > 1 and text.isalpha():
                    if text not in words:
                        words.append(text)
        
    except Exception as e:
        logger.error(f"提取单词信息失败 (页面ID: {page_id}): {str(e)}")
    
    return words, word_audio_urls

# 下载单词发音文件
def download_word_audio(url, word):
    """下载单词发音文件"""
    try:
        if not url:
            logger.warning(f"URL为空，跳过下载单词: {word}")
            return False
        
        # 确保URL是完整的
        if not url.startswith('http'):
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                url = 'https://www.yyybabc.com' + url
            else:
                # 如果不是以http或/开头，可能是相对路径或有其他格式问题
                url = 'https://www.yyybabc.com' + '/' + url.lstrip('./')
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
        
        save_path = f"words-voice/word-{word}.mp3"
        
        # 流式下载文件
        with requests.get(url, headers=headers, stream=True, timeout=30) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            
            # 使用tqdm显示进度
            progress_bar = tqdm(
                desc=f"word-{word}.mp3",
                total=total_size,
                unit='B',
                unit_scale=True,
                unit_divisor=1024,
                leave=False
            )
            
            with open(save_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        progress_bar.update(len(chunk))
            
            progress_bar.close()
        
        logger.info(f"单词发音文件下载成功: {save_path}")
        return True
    except Exception as e:
        logger.error(f"单词发音文件下载失败 {word}: {str(e)}")
        # 下载失败时删除不完整的文件
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
            except:
                pass
        return False

# 提取和下载单个页面的单词信息
def process_page(page_id):
    """提取和下载单个页面的单词信息"""
    url = f"https://www.yyybabc.com/p/d{page_id}.html"
    logger.info(f"开始处理页面: {url}")
    
    # 获取页面内容
    page_content = get_page_content(url)
    if not page_content:
        return False, [], {}
    
    # 提取单词信息
    words, word_audio_urls = extract_words_from_page(page_content, page_id)
    
    if not words:
        logger.warning(f"未找到单词信息 (页面ID: {page_id})")
        return False, [], {}
    
    logger.info(f"找到单词: {', '.join(words)} (页面ID: {page_id})")
    
    # 下载单词发音文件
    downloaded_words = []
    for word in words:
        if word in word_audio_urls and word_audio_urls[word]:
            success = download_word_audio(word_audio_urls[word], word)
            if success:
                downloaded_words.append(word)
        else:
            # 尝试直接构造URL下载
            constructed_url = f"https://www.yyybabc.com/assets/words/{word}.aac"
            logger.info(f"尝试构造URL下载: {constructed_url}")
            success = download_word_audio(constructed_url, word)
            if success:
                downloaded_words.append(word)
        
        # 添加延迟以避免对服务器造成过大压力
        time.sleep(0.5)
    
    return True, words, downloaded_words

# 主函数
def main():
    """主函数"""
    print("="*60)
    print("英语音标单词提取和下载脚本")
    print("="*60)
    print("\n此脚本将自动从d1.html到d48.html提取单词信息并下载发音文件。")
    print("下载的文件将保存在words-voice目录中。\n")
    
    # 确保目录存在
    ensure_directories()
    
    # 存储所有音标的单词映射
    phonetic_words_map = {}
    
    # 开始处理
    start_time = time.time()
    success_count = 0
    total_words = 0
    downloaded_words_count = 0
    
    print("开始提取和下载单词信息...\n")
    
    # 遍历所有48个音标页面
    for page_id in range(1, 49):
        success, all_words, downloaded_words = process_page(page_id)
        if success:
            success_count += 1
            phonetic_words_map[str(page_id)] = all_words
            total_words += len(all_words)
            downloaded_words_count += len(downloaded_words)
        
        # 添加延迟以避免对服务器造成过大压力
        if page_id < 48:
            time.sleep(1)
    
    # 保存单词映射为JSON文件，供前端使用
    with open('phonetic_words.json', 'w', encoding='utf-8') as f:
        json.dump(phonetic_words_map, f, ensure_ascii=False, indent=2)
    logger.info("单词映射已保存到phonetic_words.json")
    
    # 统计结果
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "="*60)
    print("处理统计结果")
    print("="*60)
    print(f"总耗时: {duration:.2f} 秒")
    print(f"成功处理: {success_count} 个页面")
    print(f"提取单词总数: {total_words} 个")
    print(f"成功下载单词发音: {downloaded_words_count} 个")
    print("="*60)
    print("\n处理完成！单词映射已保存到phonetic_words.json")
    print("请在浏览器中打开index.html开始使用带有单词功能的音标学习网站。")

if __name__ == "__main__":
    main()