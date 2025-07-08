"""
Styled GUI Components Module

This module provides reusable styled components for the GUI.
Extracted from the monolithic main script to improve maintainability.
"""

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QPushButton, QFrame, QLabel

from config.settings import COLORS, GUI_CONFIG


class StyledButton(QPushButton):
    """Custom styled button with consistent appearance"""
    
    def __init__(self, text, color_key="primary"):
        """
        Initialize a styled button.
        
        Args:
            text (str): Button text
            color_key (str): Color scheme key from COLORS
        """
        super().__init__(text)
        self.setMinimumHeight(GUI_CONFIG["button_min_height"])
        self.setMinimumWidth(GUI_CONFIG["button_min_width"])
        
        # Apply the stylesheet based on the color key
        color = COLORS[color_key]
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 3px;
                padding: 6px 14px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {color}CC;
            }}
            QPushButton:pressed {{
                background-color: {color}77;
            }}
            QPushButton:disabled {{
                background-color: {COLORS["mid_gray"]};
                color: {COLORS["dark_gray"]};
            }}
        """)
        



class StyledFrame(QFrame):
    """Custom styled frame with consistent appearance"""
    
    def __init__(self, color_key="light_gray"):
        """
        Initialize a styled frame.
        
        Args:
            color_key (str): Color scheme key from COLORS
        """
        super().__init__()
        color = COLORS[color_key]
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 8px;
                padding: 10px;
            }}
        """)


class LogoLabel(QLabel):
    """Custom label for displaying logos with consistent styling"""
    
    def __init__(self, logo_path, logo_name="Logo", custom_size=None, custom_frame_size=None):
        """
        Initialize a logo label.
        
        Args:
            logo_path (str): Path to the logo image file
            logo_name (str): Alt text for the logo
            custom_size (tuple, optional): Custom size (width, height) for this logo
            custom_frame_size (tuple, optional): Custom frame size (width, height) for this logo
        """
        super().__init__()
        
        # Use custom sizes if provided, otherwise fall back to defaults
        if custom_size:
            logo_size = custom_size
            if custom_frame_size:
                frame_size = custom_frame_size
            else:
                frame_size = (custom_size[0] + 10, custom_size[1] + 10)  # Add padding
        else:
            logo_size = GUI_CONFIG.get("header_logo_size", (70, 70))  # Fallback
        frame_size = GUI_CONFIG["header_frame_size"]
        
        if logo_path and logo_path.exists():
            try:
                # Handle SVG files differently
                if str(logo_path).lower().endswith('.svg'):
                    # For SVG files, create a pixmap and render the SVG onto it
                    try:
                        from PySide6.QtSvg import QSvgRenderer
                        from PySide6.QtGui import QPainter
                        from PySide6.QtCore import QRectF, QSizeF
                        
                        svg_renderer = QSvgRenderer(str(logo_path))
                        
                        # Get the original SVG size
                        svg_size = svg_renderer.defaultSize()
                        
                        # Calculate scaled size while maintaining aspect ratio
                        target_width, target_height = logo_size
                        if svg_size.width() > 0 and svg_size.height() > 0:
                            aspect_ratio = svg_size.width() / svg_size.height()
                            
                            if aspect_ratio > 1:  # Wider than tall
                                scaled_width = target_width
                                scaled_height = int(target_width / aspect_ratio)
                            else:  # Taller than wide
                                scaled_height = target_height
                                scaled_width = int(target_height * aspect_ratio)
                            
                            # Ensure we don't exceed the target dimensions
                            if scaled_width > target_width:
                                scaled_width = target_width
                                scaled_height = int(target_width / aspect_ratio)
                            if scaled_height > target_height:
                                scaled_height = target_height
                                scaled_width = int(target_height * aspect_ratio)
                        else:
                            scaled_width, scaled_height = logo_size
                        
                        # Create pixmap with original target size and fill with transparent
                        logo_pixmap = QPixmap(target_width, target_height)
                        logo_pixmap.fill(Qt.transparent)
                        
                        # Calculate position to center the scaled SVG
                        x_offset = (target_width - scaled_width) // 2
                        y_offset = (target_height - scaled_height) // 2
                        
                        # Render SVG at calculated size and position
                        painter = QPainter(logo_pixmap)
                        painter.setRenderHint(QPainter.Antialiasing)
                        svg_renderer.render(painter, QRectF(x_offset, y_offset, scaled_width, scaled_height))
                        painter.end()
                        
                    except ImportError:
                        # Fallback to regular QPixmap if QtSvg is not available
                        logo_pixmap = QPixmap(str(logo_path))
                        logo_pixmap = logo_pixmap.scaled(
                            logo_size[0], logo_size[1], 
                            Qt.KeepAspectRatio, Qt.SmoothTransformation
                        )
                else:
                    # For regular image files (PNG, JPG, etc.)
                    logo_pixmap = QPixmap(str(logo_path))
                    logo_pixmap = logo_pixmap.scaled(
                        logo_size[0], logo_size[1], 
                        Qt.KeepAspectRatio, Qt.SmoothTransformation
                    )
                
                self.setPixmap(logo_pixmap)
                self.setStyleSheet("""
                    background-color: transparent; 
                    border: none;
                    padding: 0px;
                """)
                self.setFixedSize(frame_size[0], frame_size[1])
                self.setAlignment(Qt.AlignCenter)
            except Exception as e:
                # Fallback to text if image loading fails
                self.setText(logo_name)
                self._set_text_fallback_style()
        else:
            # Fallback to text if file doesn't exist
            self.setText(logo_name)
            self._set_text_fallback_style()
    
    def _set_text_fallback_style(self):
        """Set styling for text fallback when image can't be loaded."""
        frame_size = GUI_CONFIG["header_frame_size"]
        self.setStyleSheet(f"""
            background-color: {COLORS["light"]};
            border: 1px solid {COLORS["mid_gray"]};
            border-radius: 5px;
            padding: 3px;
            font-weight: bold;
            color: {COLORS["dark"]};
        """)
        self.setFixedSize(frame_size[0], frame_size[1])
        self.setAlignment(Qt.AlignCenter)


class TitleLabel(QLabel):
    """Custom label for titles with consistent styling"""
    
    def __init__(self, text, size="large", color_key="light"):
        """
        Initialize a title label.
        
        Args:
            text (str): Title text
            size (str): Size variant ("large", "medium", "small")
            color_key (str): Color scheme key from COLORS
        """
        super().__init__(text)
        color = COLORS[color_key]
        
        # Define size styles
        size_styles = {
            "large": {"font-size": "22px", "font-weight": "bold", "padding": "0px"},
            "medium": {"font-size": "16px", "font-weight": "bold", "padding": "0px"},
            "small": {"font-size": "14px", "font-weight": "normal", "padding": "0px"}
        }
        
        style = size_styles.get(size, size_styles["medium"])
        
        self.setStyleSheet(f"""
            color: {color};
            font-size: {style["font-size"]};
            font-weight: {style["font-weight"]};
            padding: {style["padding"]};
            border: none;
            background-color: transparent;
        """)
        self.setAlignment(Qt.AlignHCenter)


class StatusIndicator(QLabel):
    """Status indicator with color-coded states"""
    
    def __init__(self, initial_status="idle"):
        """
        Initialize a status indicator.
        
        Args:
            initial_status (str): Initial status ("idle", "running", "success", "error")
        """
        super().__init__()
        self.status_styles = {
            "idle": {"color": COLORS["dark_gray"], "text": "●", "tooltip": "Gereed"},
            "running": {"color": COLORS["secondary"], "text": "●", "tooltip": "Bezig met verwerken..."},
            "success": {"color": "#28a745", "text": "●", "tooltip": "Succesvol voltooid"},
            "error": {"color": "#dc3545", "text": "●", "tooltip": "Fout opgetreden"},
            "warning": {"color": COLORS["accent"], "text": "●", "tooltip": "Waarschuwing"}
        }
        self.set_status(initial_status)
    
    def set_status(self, status):
        """
        Set the status indicator state.
        
        Args:
            status (str): Status to set
        """
        if status in self.status_styles:
            style = self.status_styles[status]
            self.setText(style["text"])
            self.setStyleSheet(f"""
                color: {style["color"]};
                font-size: 16px;
                font-weight: bold;
            """)
            self.setToolTip(style["tooltip"])


class HeaderFrame(StyledFrame):
    """Specialized frame for the application header"""
    
    def __init__(self, title, subtitle, bw_logo_path=None, aico_logo_path=None):
        """
        Initialize the header frame.
        
        Args:
            title (str): Main title
            subtitle (str): Subtitle
            bw_logo_path: Path to BW logo
            aico_logo_path: Path to AICO logo
        """
        super().__init__("off_white")
        # Override with same border style as file input fields
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {COLORS["off_white"]};
                border: 1px solid {COLORS["mid_gray"]};
                border-radius: 5px;
                padding: 10px;
            }}
        """)
        self._setup_header(title, subtitle, bw_logo_path, aico_logo_path)
    
    def _setup_header(self, title, subtitle, bw_logo_path, aico_logo_path):
        """Setup the header layout and components."""
        from PySide6.QtWidgets import QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy
        
        # Use an overlay approach for proper centering
        # Main horizontal layout
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(10, 5, 10, 5)
        main_layout.setSpacing(0)
        
        # Left logo (70x70 in 80x80 frame)
        bw_logo_label = LogoLabel(bw_logo_path, "BW Logo", 
                                 GUI_CONFIG["bw_logo_size"], GUI_CONFIG["bw_logo_frame_size"])
        
        # Right logo (120x35 in 130x40 frame - minimal vertical padding)
        aico_logo_label = LogoLabel(aico_logo_path, "AICO Logo", 
                                   GUI_CONFIG["aico_logo_size"], GUI_CONFIG["aico_logo_frame_size"])
        
        # Title and subtitle container - centered independently
        center_container = QFrame()
        center_container.setStyleSheet("background-color: transparent; border: none;")
        center_layout = QVBoxLayout(center_container)
        center_layout.setContentsMargins(0, 0, 0, 0)
        center_layout.setSpacing(0)
        
        title_label = TitleLabel(title, "large", "dark")
        subtitle_label = TitleLabel(subtitle, "small", "dark")
        
        center_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        center_layout.addWidget(subtitle_label, alignment=Qt.AlignCenter)
        
        # Add to main layout with proper spacing
        main_layout.addWidget(bw_logo_label, alignment=Qt.AlignLeft | Qt.AlignVCenter)
        main_layout.addStretch(1)  # Push center content to actual center
        main_layout.addWidget(center_container, alignment=Qt.AlignCenter)
        main_layout.addStretch(1)  # Balance the left stretch
        main_layout.addWidget(aico_logo_label, alignment=Qt.AlignRight | Qt.AlignVCenter)


class ProgressSection(QFrame):
    """Section containing progress bar and step indicators"""
    
    def __init__(self):
        """Initialize the progress section."""
        super().__init__()
        self._setup_progress_section()
    
    def _setup_progress_section(self):
        """Setup the progress section layout and components."""
        from PySide6.QtWidgets import QVBoxLayout, QHBoxLayout, QProgressBar
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMinimum(0)
        self.progress_bar.setMaximum(100)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid {COLORS["mid_gray"]};
                border-radius: 5px;
                text-align: center;
                background-color: {COLORS["light_gray"]};
                height: 25px;
            }}
            QProgressBar::chunk {{
                background-color: {COLORS["primary"]};
                border-radius: 4px;
            }}
        """)
        
        # Step indicators
        steps_layout = QHBoxLayout()
        self.step_indicators = {}
        
        from config.settings import STEPS_CONFIG
        
        for step_key, step_config in STEPS_CONFIG.items():
            # Step container
            step_frame = QFrame()
            step_frame.setFixedWidth(150)
            step_layout = QVBoxLayout(step_frame)
            step_layout.setContentsMargins(5, 5, 5, 5)
            step_layout.setSpacing(2)
            
            # Step status indicator
            status_indicator = StatusIndicator("idle")
            
            # Step label
            step_label = QLabel(step_config['name'])
            step_label.setAlignment(Qt.AlignCenter)
            step_label.setStyleSheet("font-size: 10px; font-weight: bold;")
            
            step_layout.addWidget(status_indicator, alignment=Qt.AlignCenter)
            step_layout.addWidget(step_label)
            
            self.step_indicators[step_key] = {
                'frame': step_frame,
                'indicator': status_indicator,
                'label': step_label
            }
            
            steps_layout.addWidget(step_frame)
        
        # Add to main layout
        layout.addWidget(self.progress_bar)
        layout.addLayout(steps_layout)
    
    def update_progress(self, value, message=""):
        """Update the progress bar."""
        self.progress_bar.setValue(value)
        if message:
            self.progress_bar.setFormat(f"{value}% - {message}")
        else:
            self.progress_bar.setFormat(f"{value}%")
    
    def update_step_status(self, step_key, status):
        """Update a step's status indicator."""
        if step_key in self.step_indicators:
            self.step_indicators[step_key]['indicator'].set_status(status)
    
    def reset_progress(self):
        """Reset progress bar and all step indicators."""
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat("0%")
        for step_key in self.step_indicators:
            self.update_step_status(step_key, "idle")