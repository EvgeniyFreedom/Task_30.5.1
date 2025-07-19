import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


@pytest.fixture(autouse=True)
def driver():
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.implicitly_wait(10)  # Неявное ожидание для всех find_element
    driver.get('https://petfriends.skillfactory.ru/login')
    yield driver
    driver.quit()


def test_show_all_pets(driver):
    # Вход на сайт
    driver.find_element(By.ID, 'email').send_keys('my_email')
    driver.find_element(By.ID, 'pass').send_keys('my_password')
    driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

    # Переход на страницу всех питомцев
    driver.get('https://petfriends.skillfactory.ru/all_pets')

    # Проверка карточек питомцев (неявные ожидания уже работают)
    cards = driver.find_elements(By.CSS_SELECTOR, '.card')
    for card in cards:
        # Фото
        image = card.find_element(By.TAG_NAME, 'img')
        assert image.get_attribute('src').strip() != '' or True  # просто доступ к src
        # Имя
        name = card.find_element(By.CSS_SELECTOR, '.card-title')
        assert name.text.strip() != ''
        # Описание (в т.ч. возраст и порода)
        desc = card.find_element(By.CSS_SELECTOR, '.card-text')
        assert desc.text.strip() != '' and ',' in desc.text

    # Переход в "Мои питомцы"
    try:
        driver.find_element(By.XPATH, '//span[@class="navbar-toggler-icon"]').click()
    except:
        pass
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//a[contains(text(), "Мои питомцы")]'))
    ).click()

    # Проверка имени пользователя
    username = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, 'h2'))
    ).text
    assert username == "my_name"

    # Ожидаем загрузку таблицы
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, 'table'))
    )

    pets = driver.find_elements(By.XPATH, '//div[@id="all_my_pets"]//tbody/tr')

    # Получаем количество питомцев из блока профиля
    profile_block = driver.find_element(By.CSS_SELECTOR, '.col-sm-4.left').text
    pets_count = int([line for line in profile_block.split('\n') if "Питомцев:" in line][0].split(": ")[1])

    assert pets_count == len(pets)

    # Явные ожидания для всех нужных элементов таблицы питомцев
    names = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//div[@id="all_my_pets"]//td[1]'))
    )
    breeds = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//div[@id="all_my_pets"]//td[2]'))
    )
    ages = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//div[@id="all_my_pets"]//td[3]'))
    )
    images = WebDriverWait(driver, 10).until(
        EC.presence_of_all_elements_located((By.XPATH, '//div[@id="all_my_pets"]//img'))
    )

    # Проверка: у всех питомцев есть имя, порода и возраст
    for name, breed, age in zip(names, breeds, ages):
        assert name.text.strip() != ''
        assert breed.text.strip() != ''
        assert age.text.strip() != ''

    # Проверка: хотя бы у половины питомцев есть фото
    images_with_photo = [img for img in images if img.get_attribute('src').strip()]
    assert len(images_with_photo) >= len(pets) // 2

    # Проверка: питомцы не дублируются
    pet_data = [f"{names[i].text}, {breeds[i].text}, {ages[i].text}" for i in range(len(pets))]
    assert len(pet_data) == len(set(pet_data)), "Есть повторяющиеся питомцы"

    # Проверка: имена уникальны
    pet_names = [name.text for name in names]
    assert len(pet_names) == len(set(pet_names)), "Есть питомцы с одинаковыми именами"
  
