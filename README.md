# Steganography Encoder/Decoder

A simple Python-based steganography tool that allows users to hide secret messages within images and retrieve them securely. The tool provides both encoding and decoding functionalities through a user-friendly graphical interface (GUI) built using the `Tkinter` library.

## Features
- **Encode Secret Message**: Hide a secret message inside an image using the least significant bit (LSB) method.
- **Decode Hidden Message**: Retrieve the hidden message from an image by entering the correct passcode.
- **Passcode Protection**: Encrypt the message with a passcode, ensuring only authorized users can decode the message.
- **Graphical User Interface**: A simple and intuitive GUI built using `Tkinter`, allowing users to easily interact with the application.
- **User Feedback**: The application provides dynamic feedback, such as success and error messages, displayed directly in the GUI.

## Requirements
- Python 3.x
- `Tkinter` (usually comes pre-installed with Python)
- `OpenCV` for image manipulation
- `NumPy` for efficient handling of image data

You can install the required dependencies using `pip`:

```bash
pip install opencv-python numpy
How It Works
Encoding:
Select an Image: Choose an image file (JPG, PNG, or JPEG) where you want to hide the secret message.
Enter a Secret Message: Type the message you want to hide in the image.
Set a Passcode: Set a passcode to protect the message. The message will only be accessible to those with the correct passcode.
Generate Encoded Image: The image is modified using the LSB method to hide the message, and the modified image is saved with a new name (e.g., encryptedImage.png).
Decoding:
Select the Encoded Image: Choose the image that contains the hidden message.
Enter the Passcode: Provide the passcode used during encoding.
Retrieve the Hidden Message: The hidden message will be extracted from the image and displayed in the GUI.
Installation
Clone the repository or download the project files.
bash
Copy
Edit
git clone https://github.com/your-username/steganography-project.git
Install the required dependencies:
bash
Copy
Edit
pip install opencv-python numpy
Run the main.py file:
bash
Copy
Edit
python main.py
Usage
Open the Application: When you run the program, a window will open.
Select Mode: Choose whether you want to encode or decode a message using the radio buttons.
For Encoding:
Select an image using the "Browse" button.
Enter the secret message and passcode.
Click the "Encode Message" button to encode the message in the image.
For Decoding:
Select the encoded image.
Enter the passcode used during encoding.
Click the "Decode Message" button to extract the hidden message.
Example
Encoding
Select an image file image.jpg.
Enter the secret message: Hello World!
Enter a passcode: 1234
Click "Encode Message".
The program generates encryptedImage.png with the hidden message.
Decoding
Select the encoded image encryptedImage.png.
Enter the passcode: 1234.
Click "Decode Message".
The message Hello World! is extracted and displayed.
Project Structure
bash
Copy
Edit
steganography-project/
├── main.py               # Main Python file with the application logic
├── README.md             # Project description and instructions
├── requirements.txt      # List of Python dependencies
├── encryptedImage.png    # Example encoded image (generated at runtime)
Contributing
Feel free to contribute to the project by submitting bug fixes, feature requests, or improvements. Fork the repository and create a pull request with your changes.

License
This project is licensed under the MIT License - see the LICENSE file for details.

Acknowledgments
OpenCV for image processing.
Tkinter for building the GUI.
NumPy for efficient data handling.
