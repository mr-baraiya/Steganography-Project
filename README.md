# Steganography Encoder/Decoder

This Python-based Steganography tool allows users to encode a secret message into an image and decode it using a passcode. The application uses the **Least Significant Bit (LSB)** method for encoding the message into the image. The user interface is built using `Tkinter` to make the process simple and intuitive.

## Features

- **Encode Message**: Hide a secret message within an image file.
- **Decode Message**: Retrieve the hidden message from an encoded image using the correct passcode.
- **Passcode Protection**: The hidden message is encrypted with a passcode for secure access.
- **Graphical User Interface**: Simple GUI using `Tkinter` for easy interaction.
- **Supports Various Image Formats**: Works with JPG, PNG, and other standard image formats.

## Requirements

To run this project, you need to have the following dependencies installed:

- Python 3.x
- `Tkinter` (usually comes pre-installed with Python)
- `opencv-python` for image manipulation
- `numpy` for efficient array handling

Install the necessary dependencies using `pip`:

```bash
pip install opencv-python numpy
```

## How It Works

### Encode a Secret Message:
1. **Select an Image**: Choose an image to hide the secret message.
2. **Enter the Message**: Type in the message you want to hide inside the image.
3. **Set a Passcode**: Set a passcode to protect the message. Only those with the passcode can decode the message.
4. **Encode the Message**: Click on the "Encode Message" button, and the secret message will be encoded into the image using the Least Significant Bit method.

### Decode a Secret Message:
1. **Select the Encoded Image**: Choose the image where the message was encoded.
2. **Enter the Passcode**: Provide the passcode used during encoding.
3. **Extract the Message**: Click the "Decode Message" button to reveal the hidden message from the image.

## Installation

1. Clone the repository to your local machine:
   ```bash
   git clone https://github.com/your-username/steganography-project.git
   ```
2. Install the required dependencies:
   ```bash
   pip install opencv-python numpy
   ```
3. Run the application:
   ```bash
   python main.py
   ```

## Usage

1. **Launch the Application**: Once you run `main.py`, the GUI will open.
2. **Select the Mode**: Choose either "Encode" or "Decode" mode using the radio buttons.
3. **For Encoding**:
   - Browse and select an image.
   - Enter the secret message and passcode.
   - Click the "Encode Message" button.
4. **For Decoding**:
   - Browse and select the encoded image.
   - Enter the passcode used for encoding.
   - Click "Decode Message" to extract the hidden message.

## Example

### Encoding Example:
1. Choose an image (`image.jpg`).
2. Enter the message: `This is a secret message!`.
3. Enter a passcode: `1234`.
4. Click "Encode Message" and the encoded image (`encryptedImage.png`) will be generated.

### Decoding Example:
1. Choose the encoded image (`encryptedImage.png`).
2. Enter the passcode: `1234`.
3. Click "Decode Message" and the hidden message `This is a secret message!` will be displayed.

## Project Structure

```
steganography-project/
├── main.py               # The main Python file for the application
├── README.md             # The project documentation
├── requirements.txt      # List of dependencies for the project
├── encryptedImage.png    # Encoded image (generated at runtime)
```

## Contributing

Contributions are welcome! You can fork this repository, make improvements, or submit bug fixes. Please feel free to create a pull request with your changes.

## License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **OpenCV**: For image manipulation.
- **Tkinter**: For building the graphical user interface.
- **NumPy**: For efficient data handling and manipulation.
```
