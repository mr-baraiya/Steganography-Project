# CELATUS

> **Hide. Secure. Reveal.**

**CELATUS** is a sleek, modern desktop application designed for secure image steganography using **Least Significant Bit (LSB)** encoding. Built with **CustomTkinter**, CELATUS provides a dark-themed, responsive user interface with strict input validation, custom modal dialogs, and flexible output save location controls.

---

## Etymology & Meaning

The name **Celatus** originates from Latin (the perfect passive participle of *cēlō*, meaning *"to hide"*, *"to conceal"*, or *"to keep secret"*). It signifies something that has been hidden from view, perfectly reflecting the application's core purpose: concealing sensitive data undetected inside carrier images.

---

## Key Features

- **LSB Steganography**: Encode UTF-8 text payload streams directly into image pixels.
- **Passcode Security**: Protect payloads with a required 4-character minimum passcode key.
- **Modern Dark UI**: Designed with `#0B0F17` minimalist palette and clean header action bar.
- **Custom Square Popups**: Auto-fitting, scroll-free dark modal popups with 1-click clipboard copy.
- **Custom Save Picker**: Select exact destination folder and custom filename when saving encrypted images.
- **Responsive Layout**: Seamless switching between wide dual-panel and narrow single-column responsive views.
- **Best-Fit Preview**: Maintains aspect ratios without distortion for uploaded carrier images.

---

## Installation & Setup

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/mr-baraiya/Steganography-Project.git
   cd Steganography-Project
   ```

2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Launch CELATUS**:
   ```bash
   python main.py
   ```

---

## Project Structure

```
Steganography-Project/
├── main.py                     # App entry point
├── steganography/              # Core steganography logic package
│   ├── __init__.py             # Exports
│   ├── lsb.py                  # LSB encoding/decoding engine
│   └── validator.py            # Input validation & capacity logic
├── ui/                         # User interface package
│   ├── app.py                  # SteganographyApp CustomTkinter window
│   └── dialogs.py              # Custom modal popups & copy-to-clipboard
├── downloads/                  # Native executable installer packages
│   ├── celatus_setup.exe       # Windows 10/11 standalone executable
│   ├── celatus_macOS.dmg       # macOS Universal installation package
│   └── celatus_mobile.apk      # Android / Mobile application package
├── LICENSE                     # MIT License file
├── index.html                  # Public website landing page & downloads
├── requirements.txt            # Project dependencies
└── README.md                   # Project documentation
```

---

## Requirements

- Python 3.8+
- `customtkinter`
- `pillow`
- `opencv-python`
- `numpy`

---

## Repository & Contact

- **GitHub Repository**: [https://github.com/mr-baraiya/Steganography-Project](https://github.com/mr-baraiya/Steganography-Project)
- **Contact Email**: [baraiyavishalbhai32@gmail.com](mailto:baraiyavishalbhai32@gmail.com)

---

## License

Distributed under the MIT License. See [LICENSE](file:///d:/VS_CODES/Projects/Steganography-Project/LICENSE) for full details.


