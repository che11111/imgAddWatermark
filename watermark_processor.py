#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水印处理核心模块
负责图片水印的添加、位置计算、透明度处理等功能
"""

from PIL import Image, ImageEnhance
import os
import tempfile
from pathlib import Path

class WatermarkProcessor:
    """水印处理器"""
    
    def __init__(self):
        self.supported_formats = {'.jpg', '.jpeg', '.png', '.bmp', '.gif'}
    
    def is_supported_format(self, file_path):
        """检查文件格式是否支持"""
        return Path(file_path).suffix.lower() in self.supported_formats
    
    def calculate_watermark_position(self, base_size, watermark_size, position):
        """计算水印位置"""
        base_width, base_height = base_size
        watermark_width, watermark_height = watermark_size
        
        positions = {
            'top_left': (0, 0),
            'top_right': (base_width - watermark_width, 0),
            'bottom_left': (0, base_height - watermark_height),
            'bottom_right': (base_width - watermark_width, base_height - watermark_height),
            'center': ((base_width - watermark_width) // 2, (base_height - watermark_height) // 2)
        }
        
        return positions.get(position, positions['bottom_right'])
    
    def resize_watermark(self, watermark_img, base_img, scale_factor):
        """调整水印大小"""
        base_width, base_height = base_img.size
        
        # 计算新的水印尺寸
        max_dimension = max(base_width, base_height)
        new_size = int(max_dimension * scale_factor)
        
        # 保持水印的宽高比
        watermark_width, watermark_height = watermark_img.size
        if watermark_width > watermark_height:
            new_width = new_size
            new_height = int((new_size * watermark_height) / watermark_width)
        else:
            new_height = new_size
            new_width = int((new_size * watermark_width) / watermark_height)
        
        return watermark_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    def apply_opacity(self, watermark_img, opacity):
        """应用透明度"""
        if watermark_img.mode != 'RGBA':
            watermark_img = watermark_img.convert('RGBA')
        
        # 创建透明度遮罩
        alpha = watermark_img.split()[-1]
        alpha = ImageEnhance.Brightness(alpha).enhance(opacity)
        watermark_img.putalpha(alpha)
        
        return watermark_img
    
    def add_watermark(self, input_path, watermark_path, output_path, position='bottom_right', 
                     opacity=0.7, scale=0.1):
        """
        添加水印到图片
        
        Args:
            input_path: 输入图片路径
            watermark_path: 水印图片路径
            output_path: 输出图片路径
            position: 水印位置 ('top_left', 'top_right', 'bottom_left', 'bottom_right', 'center')
            opacity: 透明度 (0.0-1.0)
            scale: 水印缩放比例 (0.0-1.0)
        """
        try:
            # 检查文件是否存在
            if not os.path.exists(input_path):
                raise FileNotFoundError(f"输入文件不存在: {input_path}")
            
            if not os.path.exists(watermark_path):
                raise FileNotFoundError(f"水印文件不存在: {watermark_path}")
            
            # 打开基础图片
            with Image.open(input_path) as base_img:
                # 转换为RGB模式（如果需要）
                if base_img.mode in ('RGBA', 'LA'):
                    background = Image.new('RGB', base_img.size, (255, 255, 255))
                    if base_img.mode == 'RGBA':
                        background.paste(base_img, mask=base_img.split()[-1])
                    else:
                        background.paste(base_img, mask=base_img.split()[-1])
                    base_img = background
                elif base_img.mode != 'RGB':
                    base_img = base_img.convert('RGB')
                
                # 打开水印图片
                with Image.open(watermark_path) as watermark_img:
                    # 调整水印大小
                    watermark_resized = self.resize_watermark(watermark_img, base_img, scale)
                    
                    # 应用透明度
                    watermark_with_opacity = self.apply_opacity(watermark_resized, opacity)
                    
                    # 计算水印位置
                    position_coords = self.calculate_watermark_position(
                        base_img.size, 
                        watermark_with_opacity.size, 
                        position
                    )
                    
                    # 创建结果图片
                    result_img = base_img.copy()
                    
                    # 粘贴水印
                    if watermark_with_opacity.mode == 'RGBA':
                        result_img.paste(watermark_with_opacity, position_coords, watermark_with_opacity)
                    else:
                        result_img.paste(watermark_with_opacity, position_coords)
                    
                    # 确保输出目录存在
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    
                    # 保存结果
                    # 根据输出文件扩展名确定保存格式
                    output_ext = Path(output_path).suffix.lower()
                    if output_ext in ['.jpg', '.jpeg']:
                        result_img.save(output_path, 'JPEG', quality=95, optimize=True)
                    elif output_ext == '.png':
                        result_img.save(output_path, 'PNG', optimize=True)
                    else:
                        # 默认保存为JPEG
                        if not output_ext:
                            output_path = output_path + '.jpg'
                        result_img.save(output_path, 'JPEG', quality=95, optimize=True)
                    
                    return True
                    
        except Exception as e:
            raise Exception(f"添加水印时出错: {str(e)}")
    
    def create_preview(self, input_path, watermark_path, position='bottom_right', 
                      opacity=0.7, scale=0.1):
        """
        创建预览图片
        
        Args:
            input_path: 输入图片路径
            watermark_path: 水印图片路径
            position: 水印位置
            opacity: 透明度
            scale: 水印缩放比例
            
        Returns:
            预览图片的临时文件路径
        """
        try:
            # 创建临时文件
            temp_dir = tempfile.gettempdir()
            preview_path = os.path.join(temp_dir, "watermark_preview.jpg")
            
            # 添加水印到预览图片
            self.add_watermark(input_path, watermark_path, preview_path, 
                             position, opacity, scale)
            
            return preview_path
            
        except Exception as e:
            raise Exception(f"创建预览时出错: {str(e)}")
    
    def batch_process(self, input_dir, watermark_path, output_dir, position='bottom_right',
                     opacity=0.7, scale=0.1, progress_callback=None):
        """
        批量处理图片
        
        Args:
            input_dir: 输入目录
            watermark_path: 水印文件路径
            output_dir: 输出目录
            position: 水印位置
            opacity: 透明度
            scale: 水印缩放比例
            progress_callback: 进度回调函数 callback(current, total, filename)
            
        Returns:
            (成功数量, 总数量, 错误列表)
        """
        try:
            input_path = Path(input_dir)
            output_path = Path(output_dir)
            
            # 确保输出目录存在
            output_path.mkdir(parents=True, exist_ok=True)
            
            # 获取所有支持的图片文件（递归搜索）
            image_files = set()  # 使用set避免重复
            for ext in self.supported_formats:
                image_files.update(input_path.rglob(f"*{ext}"))
                image_files.update(input_path.rglob(f"*{ext.upper()}"))
            
            image_files = list(image_files)  # 转换回列表
            
            total_files = len(image_files)
            success_count = 0
            errors = []
            
            for i, image_file in enumerate(image_files):
                try:
                    if progress_callback:
                        progress_callback(i, total_files, image_file.name)
                    
                    # 计算相对路径，保留目录结构
                    relative_path = image_file.relative_to(input_path)
                    output_file = output_path / relative_path
                    
                    # 确保输出子目录存在
                    output_file.parent.mkdir(parents=True, exist_ok=True)
                    
                    self.add_watermark(
                        str(image_file),
                        watermark_path,
                        str(output_file),
                        position,
                        opacity,
                        scale
                    )
                    success_count += 1
                    
                except Exception as e:
                    error_msg = f"处理文件 {image_file.name} 时出错: {str(e)}"
                    errors.append(error_msg)
                    print(error_msg)
            
            if progress_callback:
                progress_callback(total_files, total_files, "完成")
            
            return success_count, total_files, errors
            
        except Exception as e:
            raise Exception(f"批量处理时出错: {str(e)}")
    
    def get_source_files_excluding_watermarked(self, source_dir):
        """
        获取源目录中的文件，排除watermarked相关目录
        
        Args:
            source_dir: 源目录路径
            
        Returns:
            list: 源文件列表（不包含watermarked目录中的文件）
        """
        try:
            source_path = Path(source_dir)
            
            # 获取所有图片文件
            all_files = set()
            for ext in self.supported_formats:
                all_files.update(source_path.rglob(f"*{ext}"))
                all_files.update(source_path.rglob(f"*{ext.upper()}"))
            
            # 过滤出不在watermarked相关目录中的文件
            source_files = []
            watermarked_dirs = ['watermarked', 'watermarked_new']  # 需要排除的目录名
            
            for file_path in all_files:
                # 检查文件路径中是否包含watermarked相关目录
                relative_path = file_path.relative_to(source_path)
                path_parts = relative_path.parts
                
                # 如果路径中不包含watermarked相关目录，则保留
                if not any(part in watermarked_dirs for part in path_parts):
                    source_files.append(file_path)
            
            return source_files
            
        except Exception as e:
            print(f"获取源文件列表时出错: {e}")
            return []
    
    def get_processed_files(self, source_dir, watermarked_dir):
        """
        获取已经处理过的文件列表
        
        Args:
            source_dir: 源目录路径
            watermarked_dir: 水印目录路径
            
        Returns:
            set: 已处理文件的相对路径集合
        """
        try:
            source_path = Path(source_dir)
            watermarked_path = Path(watermarked_dir)
            
            if not watermarked_path.exists():
                return set()
            
            # 获取水印目录中的所有图片文件
            watermarked_files = set()
            for ext in self.supported_formats:
                watermarked_files.update(watermarked_path.rglob(f"*{ext}"))
                watermarked_files.update(watermarked_path.rglob(f"*{ext.upper()}"))
            
            # 转换为相对路径集合
            processed_relative_paths = set()
            for file_path in watermarked_files:
                try:
                    # 计算相对于水印目录的相对路径
                    relative_path = file_path.relative_to(watermarked_path)
                    processed_relative_paths.add(relative_path)
                except ValueError:
                    continue
            
            return processed_relative_paths
            
        except Exception as e:
            print(f"获取已处理文件列表时出错: {e}")
            return set()
    
    def filter_unprocessed_files(self, source_files, source_dir, watermarked_dir):
        """
        过滤出未处理的文件
        
        Args:
            source_files: 源文件列表
            source_dir: 源目录路径
            watermarked_dir: 水印目录路径
            
        Returns:
            list: 未处理的文件列表
        """
        try:
            source_path = Path(source_dir)
            processed_files = self.get_processed_files(source_dir, watermarked_dir)
            
            unprocessed_files = []
            for file_path in source_files:
                try:
                    # 计算源文件的相对路径
                    relative_path = file_path.relative_to(source_path)
                    
                    # 检查是否已处理
                    if relative_path not in processed_files:
                        unprocessed_files.append(file_path)
                        
                except ValueError:
                    # 如果无法计算相对路径，则认为未处理
                    unprocessed_files.append(file_path)
            
            return unprocessed_files
            
        except Exception as e:
            print(f"过滤未处理文件时出错: {e}")
            return source_files  # 出错时返回所有文件

    def get_image_info(self, image_path):
        """获取图片信息"""
        try:
            with Image.open(image_path) as img:
                return {
                    'size': img.size,
                    'mode': img.mode,
                    'format': img.format,
                    'filename': os.path.basename(image_path)
                }
        except Exception as e:
            raise Exception(f"获取图片信息时出错: {str(e)}")
