import sys
import io
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                             QTextEdit, QTabWidget)
from PyQt5.QtCore import Qt, QPoint, QRect
from PyQt5.QtGui import QPixmap, QImage, QPainter, QColor
import qrcode


class QRTextOverlay(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.display_mode = False
        self.resizing = False
        self.resize_start_pos = None
        self.resize_start_geometry = None
        
    def init_ui(self):
        # 윈도우 설정
        self.setWindowTitle('QR & Text Overlay')
        self.setGeometry(100, 100, 500, 600)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        # 메인 위젯
        main_widget = QWidget()
        main_widget.setObjectName("mainWidget")
        main_widget.setStyleSheet("""
            #mainWidget {
                background-color: white;
                border-radius: 12px;
            }
        """)
        self.setCentralWidget(main_widget)
        
        # 메인 레이아웃
        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # 헤더
        self.header = self.create_header()
        layout.addWidget(self.header)
        
        # 탭 위젯
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: none;
                background: white;
            }
            QTabBar {
                padding-left: 40px;
            }
            QTabBar::tab {
                background: #f0f0f0;
                padding: 10px 30px;
                margin-right: 5px;
                margin-left: 5px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background: white;
                font-weight: bold;
            }
        """)
        
        # QR 탭
        qr_tab = self.create_qr_tab()
        self.tabs.addTab(qr_tab, " QR 코드 ")
        
        # 텍스트 탭
        text_tab = self.create_text_tab()
        self.tabs.addTab(text_tab, " 텍스트 ")
        
        # 탭바 설정
        tab_bar = self.tabs.tabBar()
        tab_bar.setExpanding(False)
        
        layout.addWidget(self.tabs)
        
        # 표시 영역 (처음엔 숨김)
        self.display_widget = QWidget()
        self.display_widget.setStyleSheet("background: transparent;")
        display_layout = QVBoxLayout(self.display_widget)
        
        # QR 표시
        self.qr_display_label = QLabel()
        self.qr_display_label.setAlignment(Qt.AlignCenter)
        self.qr_display_label.hide()
        display_layout.addWidget(self.qr_display_label)
        
        # 텍스트 표시
        self.text_display_label = QLabel()
        self.text_display_label.setAlignment(Qt.AlignCenter)
        self.text_display_label.setStyleSheet("""
            font-size: 24px;
            font-weight: bold;
            color: black;
            background: white;
            padding: 20px;
            border-radius: 8px;
        """)
        self.text_display_label.hide()
        display_layout.addWidget(self.text_display_label)
        
        self.display_widget.hide()
        layout.addWidget(self.display_widget)
        
        # 디스플레이 모드 버튼
        self.display_btn = QPushButton("디스플레이 모드로 전환")
        self.display_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                color: white;
                border: none;
                border-radius: 8px;
                padding: 15px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #7c8ff0, stop:1 #8c5bb2);
            }
        """)
        self.display_btn.clicked.connect(self.toggle_display_mode)
        layout.addWidget(self.display_btn)
        
        # 커스텀 크기 조절 핸들 (오른쪽 아래)
        self.resize_handle = QLabel(main_widget)
        self.resize_handle.setFixedSize(20, 20)
        self.resize_handle.setStyleSheet("""
            background: rgba(102, 126, 234, 0.6);
            border-radius: 3px;
        """)
        self.resize_handle.setCursor(Qt.SizeFDiagCursor)
        self.update_resize_handle_position()
        
    def create_header(self):
        header = QWidget()
        header.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #667eea, stop:1 #764ba2);
            border-top-left-radius: 12px;
            border-top-right-radius: 12px;
        """)
        header_layout = QHBoxLayout(header)
        
        title_layout = QVBoxLayout()
        title = QLabel("QR & Text Overlay")
        title.setStyleSheet("color: white; font-size: 18px; font-weight: bold; margin-bottom: 3px;")
        title_layout.addWidget(title)
        
        usage = QLabel("💡 사용법: QR/텍스트 입력 → 생성/설정 → 디스플레이 모드 | 더블클릭=편집모드")
        usage.setStyleSheet("color: rgba(255, 255, 255, 0.9); font-size: 11px;")
        title_layout.addWidget(usage)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        close_btn = QPushButton("×")
        close_btn.setFixedSize(30, 30)
        close_btn.setStyleSheet("""
            QPushButton {
                background: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                border-radius: 15px;
                font-size: 20px;
            }
            QPushButton:hover {
                background: rgba(255, 255, 255, 0.3);
            }
        """)
        close_btn.clicked.connect(self.close)
        header_layout.addWidget(close_btn)
        
        return header
        
    def create_qr_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # QR 입력
        qr_label = QLabel("QR 코드로 만들 텍스트:")
        qr_label.setStyleSheet("font-weight: bold; margin-bottom: 5px; padding-left: 5px;")
        qr_label.setWordWrap(True)
        qr_label.setMinimumWidth(180)
        layout.addWidget(qr_label)
        
        self.qr_input = QLineEdit()
        self.qr_input.setPlaceholderText("URL 또는 텍스트 입력...")
        self.qr_input.setStyleSheet("""
            QLineEdit {
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border-color: #667eea;
            }
        """)
        layout.addWidget(self.qr_input)
        
        # QR 생성 버튼 (중앙 정렬)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        qr_btn = QPushButton("QR 코드 생성")
        qr_btn.setFixedWidth(200)
        qr_btn.setStyleSheet("""
            QPushButton {
                background: #667eea;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #7c8ff0;
            }
        """)
        qr_btn.clicked.connect(self.generate_qr)
        btn_layout.addWidget(qr_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        # QR 미리보기
        self.qr_preview = QLabel()
        self.qr_preview.setAlignment(Qt.AlignCenter)
        self.qr_preview.setStyleSheet("margin-top: 20px;")
        layout.addWidget(self.qr_preview)
        
        layout.addStretch()
        return tab
        
    def create_text_tab(self):
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(30, 20, 30, 20)
        
        # 텍스트 입력
        text_label = QLabel("표시할 텍스트:")
        text_label.setStyleSheet("font-weight: bold; margin-bottom: 5px;")
        layout.addWidget(text_label)
        
        self.text_input = QTextEdit()
        self.text_input.setPlaceholderText("여기에 텍스트를 입력하세요...")
        self.text_input.setStyleSheet("""
            QTextEdit {
                padding: 10px;
                border: 2px solid #e0e0e0;
                border-radius: 6px;
                font-size: 14px;
            }
            QTextEdit:focus {
                border-color: #667eea;
            }
        """)
        layout.addWidget(self.text_input)
        
        # 상태 메시지
        self.text_status = QLabel()
        self.text_status.setStyleSheet("""
            color: #667eea;
            font-size: 12px;
            padding: 5px;
            text-align: center;
        """)
        self.text_status.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.text_status)
        
        # 텍스트 설정 버튼 (중앙 정렬)
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        text_btn = QPushButton("텍스트 설정")
        text_btn.setFixedWidth(200)
        text_btn.setStyleSheet("""
            QPushButton {
                background: #667eea;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 12px;
                font-size: 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #7c8ff0;
            }
        """)
        text_btn.clicked.connect(self.set_text)
        btn_layout.addWidget(text_btn)
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        layout.addStretch()
        return tab
        
    def generate_qr(self):
        text = self.qr_input.text().strip()
        if not text:
            return
            
        # QR 코드 생성 (box_size를 작게 하여 크기 축소)
        qr = qrcode.QRCode(version=1, box_size=5, border=1)
        qr.add_data(text)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        
        # PIL Image를 QPixmap으로 변환
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        buffer.seek(0)
        
        qimage = QImage.fromData(buffer.read())
        pixmap = QPixmap.fromImage(qimage)
        
        # 미리보기 표시 (더 작게)
        self.qr_preview.setPixmap(pixmap.scaled(180, 180, Qt.KeepAspectRatio))
        
        # 표시용 저장 (더 작게)
        self.qr_display_label.setPixmap(pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        
        # 텍스트 표시 제거 (QR과 텍스트 중 하나만 표시)
        self.text_display_label.clear()
        
    def set_text(self):
        text = self.text_input.toPlainText().strip()
        if not text:
            self.text_status.setText("⚠️ 텍스트를 입력하세요")
            return
        self.text_display_label.setText(text)
        # QR 미리보기 제거 (텍스트와 QR 중 하나만 표시)
        self.qr_preview.clear()
        self.text_status.setText("✅ 텍스트가 설정되었습니다!")
            
    def toggle_display_mode(self):
        if self.display_mode:
            # 디스플레이 모드에서 편집 모드로
            self.display_mode = False
            self.header.show()
            self.tabs.show()
            self.display_btn.show()
            self.display_widget.hide()
            self.resize_handle.show()
            self.centralWidget().setStyleSheet("""
                #mainWidget { 
                    background-color: white;
                    border-radius: 12px;
                }
            """)
            self.display_btn.setText("디스플레이 모드로 전환")
        else:
            # 편집 모드에서 디스플레이 모드로
            # 표시할 항목 확인 먼저
            has_qr = self.qr_preview.pixmap() and not self.qr_preview.pixmap().isNull()
            has_text = bool(self.text_display_label.text())
            
            if not has_qr and not has_text:
                # 표시할 내용이 없으면 전환하지 않음
                return
            
            self.display_mode = True
            self.header.hide()
            self.tabs.hide()
            self.display_btn.hide()
            self.display_widget.show()
            self.resize_handle.show()
            
            if has_qr:
                self.qr_display_label.show()
                self.text_display_label.hide()
            elif has_text:
                self.text_display_label.show()
                self.qr_display_label.hide()
                
            self.centralWidget().setStyleSheet("""
                #mainWidget { background: transparent; }
            """)
            self.display_btn.setText("편집 모드로 전환")
    
    def update_resize_handle_position(self):
        # 크기 조절 핸들을 오른쪽 아래 코너에 배치
        main_widget = self.centralWidget()
        handle_x = main_widget.width() - self.resize_handle.width() - 5
        handle_y = main_widget.height() - self.resize_handle.height() - 5
        self.resize_handle.move(handle_x, handle_y)
    
    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.update_resize_handle_position()
            
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            # 크기 조절 핸들 영역 클릭 확인
            handle_rect = QRect(
                self.width() - 25,
                self.height() - 25,
                25, 25
            )
            if handle_rect.contains(event.pos()):
                self.resizing = True
                self.resize_start_pos = event.globalPos()
                self.resize_start_geometry = self.geometry()
                event.accept()
                return
            
            # 일반 드래그
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if self.resizing:
            # 크기 조절 중
            delta = event.globalPos() - self.resize_start_pos
            # QR은 최소 200x240, 텍스트는 200x50
            min_width = 200
            min_height = 50 if self.text_display_label.isVisible() else 240
            new_width = max(min_width, self.resize_start_geometry.width() + delta.x())
            new_height = max(min_height, self.resize_start_geometry.height() + delta.y())
            self.resize(new_width, new_height)
            event.accept()
        elif event.buttons() == Qt.LeftButton and self.drag_position is not None:
            # 창 이동
            self.move(event.globalPos() - self.drag_position)
            event.accept()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.resizing = False
            event.accept()
            
    def mouseDoubleClickEvent(self, event):
        if self.display_mode:
            self.toggle_display_mode()


def main():
    app = QApplication(sys.argv)
    window = QRTextOverlay()
    window.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
