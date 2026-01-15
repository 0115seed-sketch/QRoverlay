# QR & Text Overlay - Python Version

항상 화면 위에 떠있는 QR 코드와 텍스트 표시 프로그램 (Python + PyQt5)

## 설치 및 실행

### 개발 환경에서 실행
```bash
pip install -r requirements.txt
python main.py
```

### 단일 실행 파일로 빌드
```bash
# 옵션 1: 단일 exe 파일
pyinstaller --onefile --windowed --name "QR-Text-Overlay" main.py

# 옵션 2: 폴더 방식 (시작 속도 빠름, 추천)
pyinstaller --onedir --windowed --name "QR-Text-Overlay" main.py
```

빌드 후 `dist/` 폴더에서 실행 파일 확인

## 특징

- ✅ Python이 없는 PC에서도 실행 가능 (PyInstaller 빌드 후)
- ✅ 단일 exe 파일 또는 간단한 폴더 구조
- ✅ Electron보다 가볍고 빠름 (약 30-50MB)
- ✅ QR 코드 생성 및 표시
- ✅ 텍스트 표시
- ✅ 항상 최상단 표시
- ✅ 드래그 및 크기 조절
- ✅ 투명 배경
