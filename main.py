import queue
from flask import Flask, request, jsonify
from threading import Thread
from time import sleep
from functools import wraps
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from PIL import Image
from selenium.webdriver.common.by import By
import cv2
import numpy as np
from mltu.inferenceModel import OnnxInferenceModel
from mltu.utils.text_utils import ctc_decoder
from mltu.configs import BaseModelConfigs
from selenium.common.exceptions import NoSuchElementException

app = Flask(__name__)
login_queue = queue.Queue()
driver = None  # Global variable to store the Selenium WebDriver instance


def process_login_requests():
    while True:
        if not login_queue.empty():
            username, password, time, callback = login_queue.get()
            result = main(username, password, time)
            callback(result)
        else:
            sleep(1)  # Sleep for 1 second if the queue is empty


# Start a thread to continuously process login requests
login_thread = Thread(target=process_login_requests)
login_thread.daemon = True
login_thread.start()


def get_last_td_text1():
    try:
        # Locate the table by class name
        table = driver.find_element(By.CLASS_NAME, "table-striped")

        # Locate the last row (tr) in the table body
        last_row = table.find_element(By.CSS_SELECTOR, "tbody tr:last-child")

        # Locate all cells (td) in the last row
        tds_in_last_row = last_row.find_elements(By.TAG_NAME, "td")

        # Get the text from the last td in the row (considering there are four td elements in each row)
        last_td_text = tds_in_last_row[-2].text

        return last_td_text
    except NoSuchElementException:
        print("Table or elements not found.")
        return None


def get_last_td_text2():
    try:
        # Locate the table by class name
        table = driver.find_element(By.CLASS_NAME, "table-striped")

        # Locate the last row (tr) in the table body
        last_row = table.find_element(By.CSS_SELECTOR, "tbody tr:last-child")

        # Locate all cells (td) in the last row
        tds_in_last_row = last_row.find_elements(By.TAG_NAME, "td")

        # Get the text from the last td in the row (considering there are four td elements in each row)
        last_td_text = tds_in_last_row[-1].text

        return last_td_text
    except NoSuchElementException:
        print("Table or elements not found.")
        return None


def check_element_after_login(username, password, time):
    try:
        driver.find_element(By.ID, "att")
    except NoSuchElementException:
        main(username, password, time)


class ImageToWordModel(OnnxInferenceModel):
    def __init__(self, char_list, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.char_list = char_list

    def predict(self, image):
        image = cv2.resize(image, self.input_shape[:2][::-1])
        image_pred = np.expand_dims(image, axis=0).astype(np.float32)
        preds = self.model.run(None, {self.input_name: image_pred})[0]
        text = ctc_decoder(preds, self.char_list)[0]
        return text


def capture_page_screenshot(url, output_directory="captured_images", crop_params=None):
    global driver

    if driver is None:
        driver = webdriver.Chrome()

    driver.get(url)
    driver.implicitly_wait(10)

    try:
        os.makedirs(output_directory, exist_ok=True)
        screenshot_path = os.path.join(output_directory, "captcha.png")
        driver.save_screenshot(screenshot_path)

        if crop_params:
            captcha_value = crop_and_save_image(driver, screenshot_path, crop_params)
            os.remove(screenshot_path)
            return captcha_value  # Return only captcha_value

    except Exception as e:
        print(f"Error: {e}")
    finally:
        pass


def crop_and_save_image(driver, image_path, crop_params):
    image = Image.open(image_path)
    cropped_image = image.crop(crop_params)

    # Save the cropped image
    cropped_path = image_path.replace(".png", "_cropped.png")
    cropped_image.save(cropped_path)

    # Load model configurations
    configs = BaseModelConfigs.load(
        "Models/02_captcha_to_text/202401211802/configs.yaml"
    )

    # Initialize the model
    model = ImageToWordModel(model_path=configs.model_path, char_list=configs.vocab)

    # Load an image for testing
    image_path = "captured_images/captcha_cropped.png"
    image = cv2.imread(image_path)

    # Perform prediction on the single image
    captcha_value = model.predict(image)
    return captcha_value


def submit_login_form(username, password, captcha_value):
    username_field = driver.find_element(By.NAME, "userName")
    password_field = driver.find_element(By.NAME, "password")
    captcha_field = driver.find_element(By.NAME, "enteredCaptcha")

    username_field.send_keys(username)
    password_field.send_keys(password)
    captcha_field.send_keys(captcha_value)

    captcha_field.send_keys(Keys.RETURN)


def main(username, password, time):
    url = "https://kp.christuniversity.in/KnowledgePro/StudentLoginAction.do?method=studentLogoutAction"
    crop_params = (338, 370, 465, 415)  # (left, top, right, bottom)

    captcha_value = capture_page_screenshot(url, crop_params=crop_params)

    submit_login_form(username, password, captcha_value)

    check_element_after_login(username, password, time)

    additional_link = "https://kp.christuniversity.in/KnowledgePro/StudentLoginNewAction.do?method=getHostelStudentsAttendanceSummary"
    driver.get(additional_link)

    if time == "0":
        last_td_text = get_last_td_text1()
    else:
        last_td_text = get_last_td_text2()

    if last_td_text == "Absent":
        return "A"
    else:
        return "P"


@app.route("/login", methods=["POST"])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    time = data.get("time")

    result_queue = queue.Queue()
    login_queue.put((username, password, time, result_queue.put))
    result = result_queue.get()
    return result


if __name__ == "__main__":
    app.run(port=5000)
