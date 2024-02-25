# No Fine - Hostel Attendance Tracking Application

**No Fine** is an application designed for Christ University Hostel (K. E. Hall, Jonas Hall etc.) residents to track their attendance. It automates the attendance tracking process and notifies users to mark their attendance to avoid fines imposed for non-compliance. The Python backend script listens for HTTP POST requests from the Android frontend. The request payload includes the username, password, and a time-variable. Subsequently, the script logs into the user's Knowledge Pro profile and retrieves attendance data. Based on this data, the script responds with 'P' for 'Present' and 'A' for 'Absent'.

The backend functionality is summarized as follows:
1. Automated login and data extraction are facilitated through the use of the Selenium package.
2. An ML model, trained on Knowledge Pro Captchas, is employed for login authentication. (Refer to KP-Captcha-Solving-Model repository for more details)

## Deployment

A free-tier AWS VPS can be used for hosting this project. To deploy and run this project on your personal VPS, follow these steps:

1. Clone the repository:

    ```bash
    git clone https://github.com/anuragp787/No-Fine-Backend-Hostel-Attendance-Tracking-Application.git
    ```
    
3. Install the following python libraries:
   
    ```bash
    pip install Flask
    pip install selenium
    pip install pillow
    pip install opencv-python-headless
    pip install tensorflow
    pip install mltu
    pip install numpy
    ```
    
4. Run the main.py file. Subsequently, the script will run on http://localhost:5000/ , actively listening to incoming POST requests from the android frontend.

5. Download and authenticate ngrok from https://ngrok.com/ .

6. Run the ngrok.exe file and execute the following command:
   
   ```bash
    ngrok.exe http 5000
    ```

7. Paste the tunnel link provided by ngrok and substitute it for the 'url' variable in the MainActivity.kt file in the frontend.

   ```bash
    your_ngrok_link/login
    ```
   A sample link might look like: https://73a9-13-200-255-111.ngrok-free.app .

8. To test your backend, you can run the following command on Windows Powershell to mimic the POST requests:

   ```bash
    Invoke-RestMethod -Uri "your_ngrok_tunnel_link/login" -Method POST -ContentType "application/json" -Body '{"username": "your_kp_username", "password": "your_kp_password", "time": "1"}'
    ```

   In the request payload, setting the 'time' parameter to 0 corresponds to morning attendance tracking, while setting it to 1 corresponds to night attendance tracking.

## Screenshots

<p align="center"><img src="https://res.cloudinary.com/dgh9mcfxu/image/upload/v1708152556/Screenshot_263_gc7xhe.png" alt="Alt text" width="800" height="400">

<p align="center"><img src="https://res.cloudinary.com/dgh9mcfxu/image/upload/v1708012894/Screenshot_1_hlyag9.png" alt="Alt text" width="800" height="400"></p>

<p align="center"><img src="https://res.cloudinary.com/dgh9mcfxu/image/upload/v1708012895/Screenshot_3_lwqshc.png" alt="Alt text" width="800" height="400">

<p align="center"><img src="https://res.cloudinary.com/dgh9mcfxu/image/upload/v1708866724/Screenshot_261_ge7vkx_xq5qzu.png" alt="Alt text" width="800" height="150">

<p align="center"><img src="https://res.cloudinary.com/dgh9mcfxu/image/upload/v1708866887/Screenshot_262_hubj8k_hvzfwi.png" alt="Alt text" width="800" height="150">


