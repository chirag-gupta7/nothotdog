# Hot Dog or Not Hot Dog

This project is a web-based application that uses a machine learning model to determine whether an uploaded image contains a hot dog or not. The application is built using HTML, CSS, JavaScript, and integrates with the Hugging Face API for image classification.

## Features
- Drag-and-drop image upload functionality.
- Real-time image preview.
- Integration with Hugging Face API for image analysis.
- Displays results with confidence scores and visual progress bars.
- Dark mode toggle for better user experience.
- Confetti animation for hot dog results.

## How It Works
1. **Frontend**: The user interface is built using HTML, CSS, and JavaScript. It provides a drag-and-drop area for uploading images, displays results, and includes animations for better user engagement.
2. **Backend**: The backend (not included in this repository) is expected to handle the `/upload` endpoint. It should process the uploaded image and send it to the Hugging Face API for classification.
3. **Hugging Face API**: The application uses the Hugging Face API to classify images. The API returns a list of labels and confidence scores, which are displayed to the user.

## Project Structure
```
web.py
templates/
    index.html
```
- `index.html`: Contains the frontend code for the application.
- `web.py`: (Placeholder) Expected to handle backend logic and API integration.

## Modules and Packages Used
### Frontend
- **Font Awesome**: Used for icons in the user interface.
- **Google Fonts**: Provides the Poppins font for consistent typography.
- **Animate.css**: Adds animations to various elements for a dynamic user experience.

### Backend (Expected)
- **Flask**: A lightweight Python web framework to handle HTTP requests and serve the frontend.
- **Requests**: To interact with the Hugging Face API.

### Hugging Face API
The Hugging Face API is used for image classification. It requires an API key for authentication. The API processes the uploaded image and returns a JSON response with labels and confidence scores.

## How to Use
1. Clone the repository.
2. Set up a backend server to handle the `/upload` endpoint.
3. Obtain an API key from Hugging Face and configure it in the backend.
4. Run the server and open `index.html` in a browser.
5. Upload an image to see the results.

## API Integration
The backend should:
1. Accept an image file from the frontend.
2. Send the image to the Hugging Face API using a POST request.
3. Parse the JSON response and return it to the frontend.

Example API Request:
```python
import requests

API_URL = "https://api-inference.huggingface.co/models/<model-name>"
HEADERS = {"Authorization": "Bearer <your-api-key>"}

def query(image_path):
    with open(image_path, "rb") as f:
        data = f.read()
    response = requests.post(API_URL, headers=HEADERS, data=data)
    return response.json()
```

## Future Enhancements
- Add support for multiple image uploads.
- Improve error handling and user feedback.
- Deploy the application to a cloud platform.

## Credits
- **Hugging Face**: For providing the image classification model.
- **Font Awesome**: For icons.
- **Animate.css**: For animations.

## License
This project is licensed under the MIT License.