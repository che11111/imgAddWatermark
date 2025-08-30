#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
水印添加工具 - 批量给目录下所有图片文件添加水印
版本: 1.0
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import threading
from pathlib import Path
from watermark_processor import WatermarkProcessor

class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title("imgAddWatermark v2.0 - 批量水印添加工具")
        self.root.geometry("800x750")
        self.root.resizable(True, True)
        
        # 设置窗口图标
        try:
            icon_path = Path(__file__).parent / "imgAddWatermark.ico"
            if icon_path.exists():
                self.root.iconbitmap(str(icon_path))
        except Exception as e:
            print(f"加载图标失败: {e}")
        
        # 初始化水印处理器
        self.processor = WatermarkProcessor()
        
        # 变量
        self.source_dir = tk.StringVar()
        self.watermark_path = tk.StringVar()
        self.output_dir = tk.StringVar()
        self.position = tk.StringVar(value="bottom_right")
        self.opacity = tk.DoubleVar(value=0.7)
        self.scale = tk.DoubleVar(value=0.1)
        self.progress_var = tk.DoubleVar()
        
        # 新增智能检测选项
        self.skip_processed = tk.BooleanVar(value=True)  # 跳过已处理文件
        self.output_mode = tk.StringVar(value="watermarked")  # 输出模式
        self.auto_detect_watermarked = tk.BooleanVar(value=True)  # 自动检测 watermarked 目录
        
        self.setup_ui()
        
    def setup_ui(self):
        """设置用户界面"""
        # 主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        
        # 配置网格权重
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # 标题
        title_label = ttk.Label(main_frame, text="imgAddWatermark - 批量水印添加工具", 
                               font=("微软雅黑", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # 源目录选择
        ttk.Label(main_frame, text="源图片目录:").grid(row=1, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.source_dir, width=50).grid(row=1, column=1, sticky="ew", padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="浏览", command=self.browse_source_dir).grid(row=1, column=2, pady=5)
        
        # 水印文件选择
        ttk.Label(main_frame, text="水印文件:").grid(row=2, column=0, sticky=tk.W, pady=5)
        ttk.Entry(main_frame, textvariable=self.watermark_path, width=50).grid(row=2, column=1, sticky="ew", padx=(5, 5), pady=5)
        ttk.Button(main_frame, text="浏览", command=self.browse_watermark).grid(row=2, column=2, pady=5)
        
        # 设置框架
        settings_frame = ttk.LabelFrame(main_frame, text="水印设置", padding="10")
        settings_frame.grid(row=3, column=0, columnspan=3, sticky="ew", pady=20)
        settings_frame.columnconfigure(1, weight=1)
        
        # 水印位置
        ttk.Label(settings_frame, text="水印位置:").grid(row=0, column=0, sticky=tk.W, pady=5)
        position_combo = ttk.Combobox(settings_frame, textvariable=self.position, 
                                    values=["top_left", "top_right", "bottom_left", "bottom_right", "center"],
                                    state="readonly")
        position_combo.grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=5)
        
        # 透明度
        ttk.Label(settings_frame, text="透明度:").grid(row=1, column=0, sticky=tk.W, pady=5)
        opacity_frame = ttk.Frame(settings_frame)
        opacity_frame.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=5)
        opacity_frame.columnconfigure(0, weight=1)
        
        opacity_scale = ttk.Scale(opacity_frame, from_=0.1, to=1.0, variable=self.opacity, 
                                orient=tk.HORIZONTAL)
        opacity_scale.grid(row=0, column=0, sticky="ew")
        opacity_label = ttk.Label(opacity_frame, text="70%")
        opacity_label.grid(row=0, column=1, padx=(10, 0))
        
        # 更新透明度显示
        def update_opacity_label(*args):
            opacity_label.config(text=f"{int(self.opacity.get() * 100)}%")
        self.opacity.trace('w', update_opacity_label)
        
        # 水印大小
        ttk.Label(settings_frame, text="水印大小:").grid(row=2, column=0, sticky=tk.W, pady=5)
        scale_frame = ttk.Frame(settings_frame)
        scale_frame.grid(row=2, column=1, sticky="ew", padx=(5, 0), pady=5)
        scale_frame.columnconfigure(0, weight=1)
        
        scale_scale = ttk.Scale(scale_frame, from_=0.05, to=1.0, variable=self.scale, 
                              orient=tk.HORIZONTAL)
        scale_scale.grid(row=0, column=0, sticky="ew")
        scale_label = ttk.Label(scale_frame, text="10%")
        scale_label.grid(row=0, column=1, padx=(10, 0))
        
        # 更新大小显示
        def update_scale_label(*args):
            scale_label.config(text=f"{int(self.scale.get() * 100)}%")
        self.scale.trace('w', update_scale_label)
        
        # 输出和智能检测设置框架
        smart_frame = ttk.LabelFrame(main_frame, text="输出和智能检测设置", padding="10")
        smart_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=10)
        smart_frame.columnconfigure(1, weight=1)
        
        # 输出模式选择（提前到第一位，更突出）
        ttk.Label(smart_frame, text="输出模式:", font=("微软雅黑", 9, "bold")).grid(row=0, column=0, sticky="w", pady=5)
        
        output_frame = ttk.Frame(smart_frame)
        output_frame.grid(row=0, column=1, sticky="ew", padx=(10, 0), pady=5)
        
        ttk.Radiobutton(output_frame, text="输出到 /watermarked 目录", 
                       variable=self.output_mode, value="watermarked").pack(anchor="w")
        ttk.Radiobutton(output_frame, text="输出到 /watermarked_new 目录", 
                       variable=self.output_mode, value="watermarked_new").pack(anchor="w")
        ttk.Radiobutton(output_frame, text="输出到指定目录", 
                       variable=self.output_mode, value="custom").pack(anchor="w")
        
        # 自定义输出目录选择
        custom_output_frame = ttk.Frame(smart_frame)
        custom_output_frame.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(5, 10))
        custom_output_frame.columnconfigure(1, weight=1)
        
        ttk.Label(custom_output_frame, text="自定义目录:").grid(row=0, column=0, sticky="w", padx=(0, 5))
        self.custom_output_entry = ttk.Entry(custom_output_frame, textvariable=self.output_dir, width=40)
        self.custom_output_entry.grid(row=0, column=1, sticky="ew", padx=(0, 5))
        self.custom_output_button = ttk.Button(custom_output_frame, text="浏览", command=self.browse_output_dir)
        self.custom_output_button.grid(row=0, column=2)
        
        # 初始状态下隐藏自定义目录选择
        custom_output_frame.grid_remove()
        self.custom_output_frame = custom_output_frame  # 保存引用以便控制显示/隐藏
        
        # 分隔线
        ttk.Separator(smart_frame, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky="ew", pady=10)
        
        # 跳过已处理文件选项
        skip_check = ttk.Checkbutton(smart_frame, text="跳过已添加水印的图片（将检测 “输入目录/watermarked” 与 “输入目录/其他子文件或文件夹下” 的图片是否重复）", 
                                   variable=self.skip_processed)
        skip_check.grid(row=3, column=0, columnspan=2, sticky="w", pady=5)
        
        # 监听输出模式变化
        def on_output_mode_change(*args):
            mode = self.output_mode.get()
            if mode == "custom":
                # 显示自定义目录选择
                self.custom_output_frame.grid()
                # 如果还没有自定义目录，弹出选择对话框
                if not self.output_dir.get() or self.output_dir.get().endswith(("watermarked", "watermarked_new")):
                    self.browse_output_dir()
            else:
                # 隐藏自定义目录选择
                self.custom_output_frame.grid_remove()
        
        self.output_mode.trace('w', on_output_mode_change)
        
        # 进度条和状态
        progress_frame = ttk.Frame(main_frame)
        progress_frame.grid(row=5, column=0, columnspan=3, sticky="ew", pady=20)
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress_bar = ttk.Progressbar(progress_frame, variable=self.progress_var, 
                                          maximum=100)
        self.progress_bar.grid(row=0, column=0, sticky="ew", pady=5)
        
        self.status_label = ttk.Label(progress_frame, text="准备就绪")
        self.status_label.grid(row=1, column=0, pady=5)
        
        # 按钮框架
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=20)
        
        self.start_button = ttk.Button(button_frame, text="开始添加水印", 
                                     command=self.start_processing, style="Accent.TButton")
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="预览效果", command=self.preview_watermark).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="清空设置", command=self.clear_settings).pack(side=tk.LEFT)
        
        # 设置默认水印文件
        watermark_file = Path("watermark.png")
        if watermark_file.exists():
            self.watermark_path.set(str(watermark_file.absolute()))
    
    def browse_source_dir(self):
        """浏览源目录"""
        directory = filedialog.askdirectory(title="选择包含图片的源目录")
        if directory:
            self.source_dir.set(directory)
    
    def browse_watermark(self):
        """浏览水印文件"""
        filetypes = (
            ("图片文件", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("PNG文件", "*.png"),
            ("JPEG文件", "*.jpg *.jpeg"),
            ("所有文件", "*.*")
        )
        filename = filedialog.askopenfilename(title="选择水印文件", filetypes=filetypes)
        if filename:
            self.watermark_path.set(filename)
    
    def browse_output_dir(self):
        """浏览输出目录"""
        directory = filedialog.askdirectory(title="选择输出目录")
        if directory:
            self.output_dir.set(directory)
    
    def validate_inputs(self):
        """验证输入"""
        if not self.source_dir.get():
            messagebox.showerror("错误", "请选择源图片目录")
            return False
        
        if not os.path.exists(self.source_dir.get()):
            messagebox.showerror("错误", "源目录不存在")
            return False
        
        if not self.watermark_path.get():
            messagebox.showerror("错误", "请选择水印文件")
            return False
        
        if not os.path.exists(self.watermark_path.get()):
            messagebox.showerror("错误", "水印文件不存在")
            return False
        
        # 检查输出目录（只有在选择自定义模式时才需要检查）
        if self.output_mode.get() == "custom":
            if not self.output_dir.get():
                messagebox.showerror("错误", "请选择自定义输出目录")
                return False
        
        return True
    
    def get_actual_output_dir(self):
        """获取实际输出目录"""
        source_path = Path(self.source_dir.get())
        if self.output_mode.get() == "watermarked":
            return str(source_path / "watermarked")
        elif self.output_mode.get() == "watermarked_new":
            return str(source_path / "watermarked_new")
        else:  # custom
            return self.output_dir.get()
    
    def get_watermarked_dir(self):
        """获取水印检测目录"""
        source_path = Path(self.source_dir.get())
        return str(source_path / "watermarked")
    
    def preview_watermark(self):
        """预览水印效果"""
        if not self.validate_inputs():
            return
        
        try:
            # 找到第一个图片文件进行预览（排除watermarked目录）
            source_dir = Path(self.source_dir.get())
            image_files = self.processor.get_source_files_excluding_watermarked(str(source_dir))
            
            if not image_files:
                messagebox.showwarning("警告", "源目录中没有找到图片文件")
                return
            
            # 使用第一个图片文件进行预览
            sample_image = str(image_files[0])
            
            preview_path = self.processor.create_preview(
                sample_image,
                self.watermark_path.get(),
                self.position.get(),
                self.opacity.get(),
                self.scale.get()
            )
            
            # 打开预览图片
            os.startfile(preview_path)
            
        except Exception as e:
            messagebox.showerror("预览错误", f"生成预览时出错: {str(e)}")
    
    def start_processing(self):
        """开始处理"""
        if not self.validate_inputs():
            return
        
        # 在新线程中运行处理过程
        self.start_button.config(state="disabled")
        thread = threading.Thread(target=self.process_images)
        thread.daemon = True
        thread.start()
    
    def process_images(self):
        """处理图片"""
        try:
            # 更新状态
            self.root.after(0, lambda: self.status_label.config(text="正在扫描图片文件..."))
            
            # 获取所有图片文件（排除watermarked相关目录）
            source_dir = Path(self.source_dir.get())
            image_files = self.processor.get_source_files_excluding_watermarked(str(source_dir))
            
            if not image_files:
                self.root.after(0, lambda: messagebox.showwarning("警告", "源目录中没有找到图片文件"))
                return
            
            # 确保输出目录存在
            output_dir = Path(self.get_actual_output_dir())
            output_dir.mkdir(parents=True, exist_ok=True)
            
            total_found = len(image_files)
            
            # 智能检测已处理文件
            if self.skip_processed.get():
                self.root.after(0, lambda: self.status_label.config(text="正在检测已处理文件..."))
                watermarked_dir = self.get_watermarked_dir()
                image_files = self.processor.filter_unprocessed_files(
                    image_files, self.source_dir.get(), watermarked_dir
                )
                
                skipped_count = total_found - len(image_files)
                if skipped_count > 0:
                    self.root.after(0, lambda: self.status_label.config(
                        text=f"智能检测: 跳过 {skipped_count} 个已处理文件"))
            
            if not image_files:
                self.root.after(0, lambda: messagebox.showinfo("信息", 
                    f"所有图片都已处理完成！\n总计扫描: {total_found} 个文件\n已处理: {total_found} 个文件"))
                return
            
            total_files = len(image_files)
            processed = 0
            
            for i, image_file in enumerate(image_files):
                try:
                    # 更新状态
                    self.root.after(0, lambda f=image_file.name: 
                                   self.status_label.config(text=f"正在处理: {f}"))
                    
                    # 计算相对路径，保留目录结构
                    relative_path = image_file.relative_to(source_dir)
                    output_path = output_dir / relative_path
                    
                    # 确保输出子目录存在
                    output_path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 处理图片
                    self.processor.add_watermark(
                        str(image_file),
                        self.watermark_path.get(),
                        str(output_path),
                        self.position.get(),
                        self.opacity.get(),
                        self.scale.get()
                    )
                    
                    processed += 1
                    progress = (processed / total_files) * 100
                    self.root.after(0, lambda p=progress: self.progress_var.set(p))
                    
                except Exception as e:
                    print(f"处理文件 {image_file} 时出错: {e}")
                    continue
            
            # 完成信息
            completion_msg = f"水印添加完成！\n"
            if self.skip_processed.get() and total_found > total_files:
                skipped = total_found - total_files
                completion_msg += f"总计扫描: {total_found} 个文件\n跳过已处理: {skipped} 个文件\n新处理: {processed} 个文件"
            else:
                completion_msg += f"成功处理 {processed} 个文件"
            
            completion_msg += f"\n输出目录: {output_dir}"
            
            self.root.after(0, lambda: self.status_label.config(text=f"完成! 成功处理 {processed} 个文件"))
            self.root.after(0, lambda: messagebox.showinfo("完成", completion_msg))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("错误", f"处理过程中出错: {str(e)}"))
        
        finally:
            self.root.after(0, lambda: self.start_button.config(state="normal"))
            self.root.after(0, lambda: self.progress_var.set(0))
    
    def clear_settings(self):
        """清空设置"""
        self.source_dir.set("")
        self.watermark_path.set("")
        self.output_dir.set("")
        self.position.set("bottom_right")
        self.opacity.set(0.7)
        self.scale.set(0.1)
        self.output_mode.set("watermarked")  # 重置为默认模式
        self.skip_processed.set(True)  # 重置智能检测选项
        self.progress_var.set(0)
        self.status_label.config(text="准备就绪")

def main():
    """主函数"""
    root = tk.Tk()
    app = WatermarkApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()