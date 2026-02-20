#!/usr/bin/env python3
"""
FIS 3.1 工卡生成器 - CryptoPunks风格像素头像

基于用户参考设计实现：
- 删除四角校准标记
- 条形码统一宽度
- 角色标签统一宽度 (120px)
- CryptoPunks随机像素头像
- 状态指示器位置优化

Author: CyberMao
Version: 3.1.0
"""

from PIL import Image, ImageDraw, ImageFont
import random
import os
from datetime import datetime, timedelta

class BadgeGenerator:
    """FIS 3.1 SubAgent Badge Generator - CryptoPunks Pixel Style"""
    
    # Color scheme
    COLORS = {
        'primary': '#ff4d00',      # Orange
        'background': '#f5f5f0',   # Off-white paper
        'border': '#1a1a1a',       # Black
        'text': '#1a1a1a',         # Black text
        'secondary': '#666666',    # Gray
        'muted': '#999999',        # Light gray
        'divider': '#dddddd',      # Divider line
        'paper_line': '#e8e8e3',   # Paper texture
        'active': '#00c853',       # Green active
    }
    
    def __init__(self, output_dir=None):
        self.width = 1200
        self.height = 400
        self.output_dir = output_dir or os.path.expanduser('~/.openclaw/output/badges')
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load fonts
        self.fonts = self._load_fonts()
    
    def _load_fonts(self):
        """Load system fonts for pixel style"""
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
            "/usr/share/fonts/truetype/noto/NotoMono-Regular.ttf",
        ]
        
        fonts = {}
        default_font = ImageFont.load_default()
        
        # Try to find a usable monospace font
        usable_font = default_font
        for path in font_paths:
            if os.path.exists(path):
                try:
                    usable_font = ImageFont.truetype(path, 14)
                    break
                except:
                    continue
        
        # Create font variants
        try:
            fonts['title'] = ImageFont.truetype(usable_font.path, 24) if hasattr(usable_font, 'path') else default_font
            fonts['header'] = ImageFont.truetype(usable_font.path, 16) if hasattr(usable_font, 'path') else default_font
            fonts['text'] = ImageFont.truetype(usable_font.path, 14) if hasattr(usable_font, 'path') else default_font
            fonts['small'] = ImageFont.truetype(usable_font.path, 11) if hasattr(usable_font, 'path') else default_font
            fonts['pixel'] = ImageFont.truetype(usable_font.path, 10) if hasattr(usable_font, 'path') else default_font
        except:
            fonts = {
                'title': default_font,
                'header': default_font,
                'text': default_font,
                'small': default_font,
                'pixel': default_font,
            }
        
        return fonts
    
    def create_badge(self, agent_data, output_path=None):
        """Create a pixel-style badge"""
        # Create canvas
        card = Image.new('RGB', (self.width, self.height), self.COLORS['background'])
        draw = ImageDraw.Draw(card)
        
        # Add paper texture
        self._add_paper_texture(draw)
        
        # Add perforations (top and bottom)
        self._add_perforations(draw)
        
        # Add border
        self._add_border(draw)
        
        # Add header
        self._add_header(draw, agent_data)
        
        # Add left section (avatar + identity)
        self._add_left_section(draw, agent_data)
        
        # Add right section (capabilities)
        self._add_right_section(draw, agent_data)
        
        # Add footer
        self._add_footer(draw, agent_data)
        
        # Save
        if output_path is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            agent_id = agent_data.get('id', 'UNKNOWN').replace('/', '-')
            output_path = os.path.join(self.output_dir, f"badge_v6_{agent_id}_{timestamp}.png")
        
        card.save(output_path)
        return output_path
    
    def _add_paper_texture(self, draw):
        """Add paper texture lines"""
        for y in range(0, self.height, 2):
            if y % 4 == 0:
                draw.line([(0, y), (self.width, y)], fill=self.COLORS['paper_line'], width=1)
    
    def _add_perforations(self, draw):
        """Add top and bottom perforations"""
        hole_radius = 6
        hole_spacing = 20
        
        for x in range(0, self.width + hole_spacing, hole_spacing):
            # Top holes
            draw.ellipse([x - hole_radius, -hole_radius, x + hole_radius, hole_radius],
                        fill=self.COLORS['border'], outline=self.COLORS['border'])
            # Bottom holes
            draw.ellipse([x - hole_radius, self.height - hole_radius, 
                         x + hole_radius, self.height + hole_radius],
                        fill=self.COLORS['border'], outline=self.COLORS['border'])
    
    def _add_border(self, draw):
        """Add sharp black border"""
        draw.rectangle([3, 12, self.width - 3, self.height - 12], 
                      outline=self.COLORS['border'], width=3)
    
    def _add_calibration_marks(self, draw):
        """Add L-shaped calibration marks at corners"""
        mark_size = 8
        corners = [
            (8, 20),
            (self.width - 8, 20),
            (8, self.height - 20),
            (self.width - 8, self.height - 20)
        ]
        
        for x, y in corners:
            # Vertical line
            draw.line([(x, y - 8), (x, y)], fill=self.COLORS['border'], width=2)
            # Horizontal line
            draw.line([(x - 8, y), (x, y)], fill=self.COLORS['border'], width=2)
    
    def _add_header(self, draw, agent_data):
        """Add header section"""
        header_y = 40
        
        # Logo and title
        draw.text((40, header_y), "⚡", fill=self.COLORS['primary'], font=self.fonts['title'])
        draw.text((80, header_y), "OPENCLAW 2.0", fill=self.COLORS['border'], font=self.fonts['header'])
        draw.text((80, header_y + 20), "FEDERAL INTELLIGENCE SYSTEM", 
                 fill=self.COLORS['secondary'], font=self.fonts['small'])
        
        # Task ID on right
        task_id = agent_data.get('task_id', '#UNKNOWN')
        draw.text((self.width - 150, header_y), task_id, fill=self.COLORS['primary'], font=self.fonts['title'])
        
        # Dashed separator line
        for x in range(40, self.width - 40, 10):
            draw.line([(x, header_y + 50), (x + 5, header_y + 50)], fill='#333333', width=1)
    
    def _add_left_section(self, draw, agent_data):
        """Add left section with avatar and identity"""
        left_x = 60
        avatar_y = 120
        
        # Avatar frame (orange circle)
        draw.ellipse([left_x, avatar_y, left_x + 80, avatar_y + 80],
                    outline=self.COLORS['primary'], width=4)
        draw.ellipse([left_x + 4, avatar_y + 4, left_x + 76, avatar_y + 76],
                    outline=self.COLORS['border'], width=2)
        
        # CryptoPunks-style random avatar
        self._draw_cryptopunk_avatar(draw, left_x, avatar_y)
        
        # Role badge (black background with orange border) - fixed width
        role = agent_data.get('role', 'AGENT').upper()
        badge_y = avatar_y + 100
        badge_width = 120  # Fixed width for all roles
        draw.rectangle([left_x, badge_y, left_x + badge_width, badge_y + 25],
                      fill=self.COLORS['border'], outline=self.COLORS['primary'], width=2)
        # Center text in badge
        text_x = left_x + (badge_width - len(role) * 6) // 2
        draw.text((text_x, badge_y + 5), role, fill='#ffffff', font=self.fonts['pixel'])
        
        # Agent metadata
        draw.text((left_x, badge_y + 40), "AGENT NAME", fill=self.COLORS['muted'], font=self.fonts['small'])
        name = agent_data.get('name', 'Unknown Agent')
        draw.text((left_x, badge_y + 58), name[:20], fill=self.COLORS['border'], font=self.fonts['header'])
        
        agent_id = agent_data.get('id', 'UNKNOWN')
        draw.text((left_x, badge_y + 85), f"ID: {agent_id}", fill=self.COLORS['secondary'], font=self.fonts['small'])
    
    def _draw_cryptopunk_avatar(self, draw, left_x, avatar_y):
        """Draw a CryptoPunks-style random pixel avatar"""
        # CryptoPunks color palette
        colors = {
            'skin': ['#f5d0b0', '#e8c4a0', '#d4a574', '#8d5524', '#523418', '#f8e8d8'],
            'hair': ['#ff6b00', '#4a4a4a', '#8b4513', '#ffd700', '#ff0000', '#00ff00', '#0000ff', '#ffffff', '#000000'],
            'eyes': ['#000000', '#4169e1', '#228b22', '#8b4513', '#9370db'],
            'accessory': ['#ff6b00', '#ffd700', '#c0c0c0', '#4169e1', '#ff69b4', '#00ff00'],
            'bg': ['#1a1a1a', '#ff4d00', '#4169e1', '#228b22', '#9370db']
        }
        
        # Random seed based on position for consistency
        import random
        random.seed(left_x + avatar_y)
        
        # Avatar center and size
        center_x = left_x + 40
        center_y = avatar_y + 40
        pixel_size = 8
        
        # Background circle fill
        bg_color = random.choice(colors['bg'])
        for y in range(avatar_y + 8, avatar_y + 72, pixel_size):
            for x in range(left_x + 8, left_x + 72, pixel_size):
                dist = ((x + pixel_size//2 - center_x) ** 2 + (y + pixel_size//2 - center_y) ** 2) ** 0.5
                if dist < 32:
                    draw.rectangle([x, y, x + pixel_size, y + pixel_size], fill=bg_color)
        
        # Skin (face base - 6x6 grid in center)
        skin_color = random.choice(colors['skin'])
        face_x = center_x - 24
        face_y = center_y - 16
        for y in range(face_y, face_y + 48, pixel_size):
            for x in range(face_x, face_x + 48, pixel_size):
                dist = ((x + pixel_size//2 - center_x) ** 2 + (y + pixel_size//2 - center_y) ** 2) ** 0.5
                if dist < 28:
                    draw.rectangle([x, y, x + pixel_size, y + pixel_size], fill=skin_color)
        
        # Eyes (2 pixels each)
        eye_color = random.choice(colors['eyes'])
        # Left eye
        draw.rectangle([face_x + 8, face_y + 16, face_x + 16, face_y + 24], fill=eye_color)
        draw.rectangle([face_x + 16, face_y + 16, face_x + 24, face_y + 24], fill=eye_color)
        # Right eye
        draw.rectangle([face_x + 32, face_y + 16, face_x + 40, face_y + 24], fill=eye_color)
        draw.rectangle([face_x + 40, face_y + 16, face_x + 48, face_y + 24], fill=eye_color)
        
        # Random eye accessories (sunglasses, mask, etc.) - 30% chance
        if random.random() < 0.3:
            acc_color = random.choice(colors['accessory'])
            # Sunglasses
            draw.rectangle([face_x + 4, face_y + 14, face_x + 26, face_y + 26], fill=acc_color)
            draw.rectangle([face_x + 28, face_y + 14, face_x + 50, face_y + 26], fill=acc_color)
            draw.rectangle([face_x + 24, face_y + 18, face_x + 30, face_y + 22], fill=acc_color)
        
        # Mouth (various styles)
        mouth_style = random.choice(['smile', 'flat', 'open', 'none'])
        mouth_color = '#000000'
        if mouth_style == 'smile':
            draw.rectangle([face_x + 16, face_y + 36, face_x + 24, face_y + 40], fill=mouth_color)
            draw.rectangle([face_x + 24, face_y + 36, face_x + 32, face_y + 40], fill=mouth_color)
            draw.rectangle([face_x + 12, face_y + 32, face_x + 16, face_y + 36], fill=mouth_color)
            draw.rectangle([face_x + 32, face_y + 32, face_x + 36, face_y + 36], fill=mouth_color)
        elif mouth_style == 'flat':
            draw.rectangle([face_x + 16, face_y + 36, face_x + 36, face_y + 40], fill=mouth_color)
        elif mouth_style == 'open':
            draw.rectangle([face_x + 20, face_y + 32, face_x + 32, face_y + 44], fill=mouth_color)
        
        # Hair (various styles)
        hair_style = random.choice(['none', 'short', 'long', 'mohawk', 'cap'])
        hair_color = random.choice(colors['hair'])
        
        if hair_style == 'short':
            for y in range(face_y - 8, face_y + 16, pixel_size):
                for x in range(face_x - 8, face_x + 56, pixel_size):
                    if y < face_y + 8 or x < face_x + 8 or x > face_x + 40:
                        draw.rectangle([x, y, x + pixel_size, y + pixel_size], fill=hair_color)
        elif hair_style == 'long':
            for y in range(face_y - 8, face_y + 56, pixel_size):
                for x in range(face_x - 8, face_x + 56, pixel_size):
                    if y < face_y + 16 or x < face_x + 4 or x > face_x + 44:
                        draw.rectangle([x, y, x + pixel_size, y + pixel_size], fill=hair_color)
        elif hair_style == 'mohawk':
            for y in range(face_y - 8, face_y + 24, pixel_size):
                for x in range(face_x + 16, face_x + 40, pixel_size):
                    draw.rectangle([x, y, x + pixel_size, y + pixel_size], fill=hair_color)
        elif hair_style == 'cap':
            # Cap base
            for y in range(face_y - 8, face_y + 8, pixel_size):
                for x in range(face_x - 8, face_x + 56, pixel_size):
                    draw.rectangle([x, y, x + pixel_size, y + pixel_size], fill=hair_color)
            # Cap brim
            for x in range(face_x - 8, face_x + 56, pixel_size):
                draw.rectangle([x, face_y + 8, x + pixel_size, face_y + 16], fill=hair_color)
        
        # Random facial hair (beard/mustache) - 20% chance
        if random.random() < 0.2:
            beard_color = random.choice(colors['hair'])
            for y in range(face_y + 40, face_y + 52, pixel_size):
                for x in range(face_x + 8, face_x + 44, pixel_size):
                    if y > face_y + 44 or x < face_x + 16 or x > face_x + 36:
                        draw.rectangle([x, y, x + pixel_size, y + pixel_size], fill=beard_color)
        
        # Random accessory (earring, etc.) - 15% chance
        if random.random() < 0.15:
            acc_color = random.choice(colors['accessory'])
            draw.rectangle([face_x - 4, face_y + 24, face_x + 4, face_y + 32], fill=acc_color)
        
        # Reset random seed
        random.seed()
    
    def _add_right_section(self, draw, agent_data):
        """Add right section with capabilities"""
        right_x = 280
        section_y = 110
        
        # SOUL label (orange)
        soul = agent_data.get('soul', '"Digital familiar navigating the void"')
        draw.rectangle([right_x, section_y, right_x + 80, section_y + 25],
                      fill=self.COLORS['primary'], outline=self.COLORS['border'], width=2)
        draw.text((right_x + 10, section_y + 5), "SOUL", fill='#ffffff', font=self.fonts['pixel'])
        draw.text((right_x + 90, section_y + 3), soul[:50], fill=self.COLORS['primary'], font=self.fonts['text'])
        
        # RESPONSIBILITIES label (black)
        resp_y = section_y + 50
        draw.rectangle([right_x, resp_y, right_x + 160, resp_y + 25],
                      fill=self.COLORS['border'], outline=self.COLORS['border'], width=2)
        draw.text((right_x + 10, resp_y + 5), "RESPONSIBILITIES", fill='#ffffff', font=self.fonts['pixel'])
        
        # Responsibilities list
        responsibilities = agent_data.get('responsibilities', [
            "Execute assigned tasks with precision",
            "Maintain communication with parent agent",
            "Report progress and blockers promptly",
            "Deliver high-quality outputs"
        ])
        
        for i, bullet in enumerate(responsibilities[:4]):
            y = resp_y + 35 + (i * 22)
            text = bullet[:65]  # Truncate long text
            draw.text((right_x + 10, y), f"▸ {text}", fill=self.COLORS['border'], font=self.fonts['small'])
        
        # OUTPUT label (gray)
        out_y = resp_y + 130
        draw.rectangle([right_x, out_y, right_x + 120, out_y + 25],
                      fill='#666666', outline=self.COLORS['border'], width=2)
        draw.text((right_x + 10, out_y + 5), "OUTPUT REQ", fill='#ffffff', font=self.fonts['pixel'])
        
        output_formats = agent_data.get('output_formats', 'MARKDOWN | JSON | TXT')
        draw.text((right_x + 130, out_y + 5), output_formats, fill=self.COLORS['border'], font=self.fonts['pixel'])
        
        # Vertical divider line
        draw.line([(250, 100), (250, self.height - 80)], fill=self.COLORS['divider'], width=2)
    
    def _add_footer(self, draw, agent_data):
        """Add footer section"""
        footer_y = self.height - 60
        
        # Black background footer
        draw.rectangle([3, footer_y, self.width - 3, self.height - 12],
                      fill=self.COLORS['border'])
        
        # Barcode (left side) - uniform width
        bar_x = 40
        bar_width = 3  # Fixed width for all bars
        bar_spacing = 2
        for i in range(40):
            draw.rectangle([bar_x, footer_y + 10, bar_x + bar_width, footer_y + 35], fill='#ffffff')
            bar_x += bar_width + bar_spacing
        
        # Barcode text
        barcode_id = agent_data.get('barcode_id', f"OC-2025-{agent_data.get('role', 'AGENT')[:4].upper()}-001")
        draw.text((40, footer_y + 40), barcode_id, fill='#666666', font=self.fonts['small'])
        
        # Status indicator (green)
        status = agent_data.get('status', 'ACTIVE')
        status_color = self.COLORS['active'] if status == 'ACTIVE' else '#ff4d00'
        # Move status indicator to the right to avoid overlap with barcode
        status_x = 320
        draw.ellipse([status_x, footer_y + 15, status_x + 15, footer_y + 30], fill=status_color, outline='#ffffff', width=2)
        draw.text((status_x + 25, footer_y + 17), status, fill='#ffffff', font=self.fonts['pixel'])
        
        # Valid until
        valid_until = agent_data.get('valid_until', (datetime.now() + timedelta(days=365)).strftime('%Y-%m-%d'))
        draw.text((self.width - 250, footer_y + 17), f"VALID UNTIL: {valid_until}", 
                 fill='#666666', font=self.fonts['small'])
        
        # QR code placeholder (right side)
        qr_x, qr_y = self.width - 70, footer_y + 10
        qr_cells = [(0, 0), (1, 0), (0, 1), (4, 0), (4, 1), (3, 4), (4, 4), (2, 2)]
        for cx, cy in qr_cells:
            draw.rectangle([qr_x + cx * 7, qr_y + cy * 7, qr_x + cx * 7 + 6, qr_y + cy * 7 + 6], fill='#ffffff')


def generate_multi_badge_image(badge_data_list, output_path=None, layout='horizontal'):
    """
    生成多工牌拼接图片
    
    Args:
        badge_data_list: 多个工牌数据字典的列表
        output_path: 输出路径
        layout: 'horizontal'(水平), 'vertical'(垂直), 'grid'(网格)
    
    Returns:
        output_path: 生成的图片路径
    """
    from PIL import Image
    
    generator = BadgeGenerator()
    
    # 生成单个工牌
    badge_paths = []
    for data in badge_data_list:
        path = generator.create_badge(data)
        badge_paths.append(path)
    
    # 加载所有图片
    images = [Image.open(p) for p in badge_paths]
    
    if layout == 'horizontal':
        # 水平拼接
        total_width = sum(img.width for img in images)
        max_height = max(img.height for img in images)
        
        combined = Image.new('RGB', (total_width, max_height), '#f5f5f0')
        x_offset = 0
        for img in images:
            combined.paste(img, (x_offset, 0))
            x_offset += img.width
            
    elif layout == 'vertical':
        # 垂直拼接
        max_width = max(img.width for img in images)
        total_height = sum(img.height for img in images)
        
        combined = Image.new('RGB', (max_width, total_height), '#f5f5f0')
        y_offset = 0
        for img in images:
            combined.paste(img, (0, y_offset))
            y_offset += img.height
            
    elif layout == 'grid':
        # 网格布局 (2x2 或 3x2)
        n = len(images)
        cols = 2 if n <= 4 else 3
        rows = (n + cols - 1) // cols
        
        max_width = max(img.width for img in images)
        max_height = max(img.height for img in images)
        
        combined = Image.new('RGB', (max_width * cols, max_height * rows), '#f5f5f0')
        
        for idx, img in enumerate(images):
            row = idx // cols
            col = idx % cols
            x = col * max_width
            y = row * max_height
            combined.paste(img, (x, y))
    
    # 保存
    if output_path is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        output_path = generator.output_dir / f"badges_multi_{layout}_{timestamp}.png"
    
    combined.save(output_path)
    print(f"✅ Multi-badge saved: {output_path}")
    
    return str(output_path)
    """Generate sample badges for different roles"""
    generator = BadgeGenerator()
    
    # Architect badge
    architect_data = {
        'name': 'Pixel-Arch-01',
        'id': 'OC-SA-2025-0001',
        'role': 'ARCHITECT',
        'task_id': '#ARCH-001',
        'soul': '"Blueprint weaver in the digital void"',
        'responsibilities': [
            "Design distributed system topology",
            "Define API contracts & data schemas",
            "Optimize latency-critical paths",
            "Review technical debt & roadmaps"
        ],
        'output_formats': 'MARKDOWN | JSON | ADR',
        'barcode_id': 'OC-2025-ARCH-001',
    }
    
    # Worker badge
    worker_data = {
        'name': 'Pixel-Worker-01',
        'id': 'OC-SA-2025-0002',
        'role': 'WORKER',
        'task_id': '#WORK-001',
        'soul': '"Silent executor of the grand design"',
        'responsibilities': [
            "Implement assigned task components",
            "Write clean, documented code",
            "Unit test all deliverables",
            "Report blockers immediately"
        ],
        'output_formats': 'CODE | TESTS | DOCS',
        'barcode_id': 'OC-2025-WORK-001',
    }
    
    # Reviewer badge
    reviewer_data = {
        'name': 'Pixel-Rev-01',
        'id': 'OC-SA-2025-0003',
        'role': 'REVIEWER',
        'task_id': '#REV-001',
        'soul': '"Guardian of quality and truth"',
        'responsibilities': [
            "Review code for bugs & style",
            "Verify output specifications",
            "Validate edge cases",
            "Approve or reject with reasons"
        ],
        'output_formats': 'REVIEW | REPORT | PASS',
        'barcode_id': 'OC-2025-REV-001',
    }
    
    # Generate badges
    badges = []
    for data in [architect_data, worker_data, reviewer_data]:
        path = generator.create_badge(data)
        badges.append((data['role'], path))
        print(f"✅ Generated {data['role']} badge: {path}")
    
    return badges


if __name__ == "__main__":
    print("=== FIS 3.1 Badge Generator v6.0 ===")
    print("Generating sample badges...\n")
    
    badges = generate_sample_badges()
    
    print("\n=== Generated Badges ===")
    for role, path in badges:
        print(f"  {role}: {path}")
    
    print("\n✅ All badges generated successfully!")
