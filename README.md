# Scissor - URL Shortening Service

Scissor is a simple yet powerful URL shortening service designed to make sharing links easier and more efficient. With its focus on brevity and customization, Scissor aims to disrupt the URL-shortening industry and provide users with a streamlined experience for creating, managing, and tracking shortened URLs.


## Features

1. **URL Shortening:** Easily shorten long URLs with a click of a button. Scissor automatically generates a shortened URL optimized for sharing on social media and other platforms.

2. **Custom URLs:** Personalize your shortened URLs by customizing the URL to align with your brand or content. Ideal for individuals and small businesses looking to create branded links.

3. **QR Code Generation:** Generate QR codes for your shortened URLs to use in promotional materials, websites, and more. Easily download the QR code image for offline use.

4. **Analytics:** Track the performance of your shortened URLs with basic analytics. Monitor the number of clicks received and the sources of those clicks to gain insights into your audience and campaign effectiveness. This feature utilizes a third-party location API to provide geolocation data for click events.

5. **Link History:** Access a comprehensive history of all the links you've created with Scissor. Easily find and reuse links for ongoing campaigns or reference purposes.


## Requirements

- Python 3.x
- FastAPI
- Third-party location API for analytics


## Installation

1. Clone the repository: `git clone https://github.com/your_username/scissor.git`
2. Navigate to the project directory: `cd scissor.io`
3. Install dependencies: `pip install -r requirements.txt`


## Usage

1. Run the FastAPI server: `uvicorn app.main:app --reload`
2. Access the Scissor.io.app via the URL (http://localhost:8000)
3.  Access the Scissor.io.app documentation via the URL (http://localhost:8000/docs)
4. Sign up for a new account or log in with existing credentials.
5. Paste a long URL into the input field and click "Shorten" to generate a shortened URL.
6. Optionally, customize the shortened URL..
7. Download the QR code image for your shortened URL.
8. Track the performance of your shortened URLs using the built-in analytics dashboard, which includes geolocation data for click events.
9. Access your link history to view and manage previously created links.


## Try it out

To try out the Scissor platform and start shortening URLs, visit the [Scissor.io App.](https://scissor-85zf.onrender.com/).


# Documentation

For detailed documentation on how to use Scissor and its features, please visit [Scissor Docs](https://scissor-85zf.onrender.com/docs).


## Acknowledgements

Special thanks to [FastAPI](https://fastapi.tiangolo.com/) for providing the foundation for building the Scissor platform.


## Contact

For questions, suggestions, or feedback, please contact [fminaseidiema26@gmail.com](mailto:fminaseidiema26@gmail.com).
	