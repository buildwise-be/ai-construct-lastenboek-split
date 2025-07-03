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
    
    def __init__(self, text, color_key="primary", icon=None):
        """
        Initialize a styled button.
        
        Args:
            text (str): Button text
            color_key (str): Color scheme key from COLORS
            icon: Optional icon for the button
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
        
        # Set icon if provided
        if icon:
            self.setIcon(icon)


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
    
    def __init__(self, logo_path, logo_name="Logo"):
        """
        Initialize a logo label.
        
        Args:
            logo_path (str): Path to the logo image file
            logo_name (str): Alt text for the logo
        """
        super().__init__()
        
        logo_size = GUI_CONFIG["header_logo_size"]
        frame_size = GUI_CONFIG["header_frame_size"]
        
        if logo_path and logo_path.exists():
            try:
                logo_pixmap = QPixmap(str(logo_path))
                logo_pixmap = logo_pixmap.scaled(
                    logo_size[0], logo_size[1], 
                    Qt.KeepAspectRatio, Qt.SmoothTransformation
                )
                self.setPixmap(logo_pixmap)
                self.setStyleSheet("""
                    background-color: white; 
                    border-radius: 5px; 
                    padding: 3px;
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
            "idle": {"color": COLORS["dark_gray"], "text": "●", "tooltip": "Ready"},
            "running": {"color": COLORS["secondary"], "text": "●", "tooltip": "Processing..."},
            "success": {"color": "#28a745", "text": "●", "tooltip": "Completed successfully"},
            "error": {"color": "#dc3545", "text": "●", "tooltip": "Error occurred"},
            "warning": {"color": COLORS["accent"], "text": "●", "tooltip": "Warning"}
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
        super().__init__("primary")
        self._setup_header(title, subtitle, bw_logo_path, aico_logo_path)
    
    def _setup_header(self, title, subtitle, bw_logo_path, aico_logo_path):
        """Setup the header layout and components."""
        from PySide6.QtWidgets import QGridLayout
        
        # Use a grid layout for flexible positioning
        header_layout = QGridLayout(self)
        header_layout.setContentsMargins(10, 5, 10, 5)
        header_layout.setSpacing(0)
        
        # Left logo
        bw_logo_label = LogoLabel(bw_logo_path, "BW Logo")
        
        # Right logo
        aico_logo_label = LogoLabel(aico_logo_path, "AICO Logo")
        
        # Title and subtitle
        title_label = TitleLabel(title, "large", "light")
        subtitle_label = TitleLabel(subtitle, "small", "light")
        
        # Add components to layout
        header_layout.addWidget(bw_logo_label, 0, 0, 2, 1, Qt.AlignLeft | Qt.AlignVCenter)
        header_layout.addWidget(title_label, 0, 1, Qt.AlignCenter)
        header_layout.addWidget(subtitle_label, 1, 1, Qt.AlignCenter)
        header_layout.addWidget(aico_logo_label, 0, 2, 2, 1, Qt.AlignRight | Qt.AlignVCenter)
        
        # Make the middle column stretch
        header_layout.setColumnStretch(1, 1)


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
            step_label = QLabel(f"{step_config['icon']} {step_config['name']}")
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