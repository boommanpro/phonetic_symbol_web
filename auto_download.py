#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
英语音标音视频自动下载脚本

此脚本会自动访问英语音标网站，提取并下载所有48个音标的音频和视频文件
"""

import os
import sys
import time
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import re
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("download.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 确保目录存在
def ensure_directories():
    """确保audio和video目录存在"""
    for dir_name in ['audio', 'video']:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            logger.info(f"已创建目录: {dir_name}")

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

# 提取音频和视频URL
def extract_media_urls(page_content, page_id):
    """从页面内容中提取音频和视频URL"""
    media_urls = {
        'audio': None,
        'video': None
    }
    
    if not page_content:
        return media_urls
    
    soup = BeautifulSoup(page_content, 'html.parser')
    
    # 尝试多种方法提取音频URL
    try:
        # 方法1: 查找audio标签
        audio_tags = soup.find_all('audio')
        for audio in audio_tags:
            if audio.get('src'):
                media_urls['audio'] = audio.get('src')
                break
        
        # 方法2: 查找带有音频相关类名的元素
        if not media_urls['audio']:
            audio_elements = soup.find_all(lambda tag: tag.name == 'source' and 'audio' in tag.get('type', ''))
            for element in audio_elements:
                if element.get('src'):
                    media_urls['audio'] = element.get('src')
                    break
        
        # 方法3: 搜索包含audio的脚本内容
        if not media_urls['audio']:
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    audio_match = re.search(r'"(https?://[^"\']*\.mp3[^"\']*)"', str(script.string))
                    if audio_match:
                        media_urls['audio'] = audio_match.group(1)
                        break
    except Exception as e:
        logger.error(f"提取音频URL失败 (页面ID: {page_id}): {str(e)}")
    
    # 尝试多种方法提取视频URL
    try:
        # 方法1: 查找video标签
        video_tags = soup.find_all('video')
        for video in video_tags:
            if video.get('src'):
                media_urls['video'] = video.get('src')
                break
            # 检查source标签
            source_tags = video.find_all('source')
            for source in source_tags:
                if source.get('src'):
                    media_urls['video'] = source.get('src')
                    break
        
        # 方法2: 搜索包含video的脚本内容
        if not media_urls['video']:
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    video_match = re.search(r'"(https?://[^"\']*\.mp4[^"\']*)"', str(script.string))
                    if video_match:
                        media_urls['video'] = video_match.group(1)
                        break
    except Exception as e:
        logger.error(f"提取视频URL失败 (页面ID: {page_id}): {str(e)}")
    
    return media_urls

# 下载文件
def download_file(url, save_path):
    """下载文件并显示进度"""
    try:
        if not url:
            logger.warning(f"URL为空，跳过下载: {save_path}")
            return False
        
        # 确保URL是完整的
        if not url.startswith('http'):
            if url.startswith('//'):
                url = 'https:' + url
            elif url.startswith('/'):
                url = 'https://www.yyybabc.com' + url
            else:
                # 如果不是以http或/开头，可能是相对路径或有其他格式问题
                logger.warning(f"URL格式不标准: {url}")
                # 尝试最常见的相对路径处理方式
                url = 'https://www.yyybabc.com' + '/' + url.lstrip('./')
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36'
        }
        
        # 流式下载大文件
        with requests.get(url, headers=headers, stream=True, timeout=30) as r:
            r.raise_for_status()
            total_size = int(r.headers.get('content-length', 0))
            
            # 使用tqdm显示进度
            progress_bar = tqdm(
                desc=os.path.basename(save_path),
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
        
        logger.info(f"文件下载成功: {save_path}")
        return True
    except Exception as e:
        logger.error(f"文件下载失败 {save_path}: {str(e)}")
        # 下载失败时删除不完整的文件
        if os.path.exists(save_path):
            try:
                os.remove(save_path)
            except:
                pass
        return False

# 下载单个页面的媒体文件
def download_media_for_page(page_id):
    """下载单个页面的音频和视频文件"""
    url = f"https://www.yyybabc.com/p/d{page_id}.html"
    logger.info(f"开始处理页面: {url}")
    
    # 获取页面内容
    page_content = get_page_content(url)
    if not page_content:
        return False
    
    # 提取媒体URL
    media_urls = extract_media_urls(page_content, page_id)
    
    # 下载音频文件
    audio_success = False
    if media_urls['audio']:
        audio_path = f"audio/phonetic-{page_id}.mp3"
        audio_success = download_file(media_urls['audio'], audio_path)
    else:
        logger.warning(f"未找到音频URL (页面ID: {page_id})")
    
    # 下载视频文件
    video_success = False
    if media_urls['video']:
        video_path = f"video/phonetic-{page_id}.mp4"
        video_success = download_file(media_urls['video'], video_path)
    else:
        logger.warning(f"未找到视频URL (页面ID: {page_id})")
    
    # 至少成功下载一个文件就算成功
    return audio_success or video_success

# 主函数
def main():
    """主函数"""
    print("="*60)
    print("英语音标音视频自动下载脚本")
    print("="*60)
    print("\n此脚本将自动下载所有48个英语音标的音频和视频文件。")
    print("请确保您有足够的网络带宽和存储空间。")
    print("\n下载过程中可能会遇到一些页面无法访问或资源不存在的情况，")
    print("这些情况将被记录在download.log文件中。\n")
    
    # 确保目录存在
    ensure_directories()
    
    # 开始下载
    start_time = time.time()
    success_count = 0
    fail_count = 0
    
    print("开始下载音视频文件...\n")
    
    # 遍历所有48个音标页面
    for page_id in range(1, 49):
        success = download_media_for_page(page_id)
        if success:
            success_count += 1
        else:
            fail_count += 1
        
        # 添加延迟以避免对服务器造成过大压力
        if page_id < 48:
            time.sleep(1)
    
    # 统计结果
    end_time = time.time()
    duration = end_time - start_time
    
    print("\n" + "="*60)
    print("下载统计结果")
    print("="*60)
    print(f"总耗时: {duration:.2f} 秒")
    print(f"成功下载: {success_count} 个页面的媒体文件")
    print(f"下载失败: {fail_count} 个页面的媒体文件")
    print("="*60)
    print("\n下载完成！您可以查看download.log文件获取详细信息。")
    print("请在浏览器中打开index.html开始使用音标学习网站。")

if __name__ == "__main__":
    main()