from flask import Flask, render_template, request
from selenium import webdriver
from selenium.webdriver.support.ui import Select
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import selenium.webdriver.support.ui as UI
import pandas as pd 
import time



app = Flask(__name__, template_folder='templates', static_folder='staticFiles')


car_link_df = pd.read_csv("csv_files/car_links.csv")

driver = ""

def scrape_data(st_index, to_index):
    global driver
    driver = webdriver.Chrome(ChromeDriverManager().install())
    all_car_info = []

    for link in car_link_df.car_links[st_index:to_index]:  
        car_data = {}  
        feature_data = []
        driver.get(link.format())

        try:
            try:
                WebDriverWait(driver, 20).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,'//*[@id="gdpr-consent-notice"]')))
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="save"]'))).click()
            except:
                pass
            car_image, new_data = [], []
            carname = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#__next > div > div > main > div.StageArea_container__YuNIp > div.StageArea_informationContainer__VaFP8 > div.StageArea_titleAndActionBarContainer__soRpp > div.StageTitle_container__vP9Cw > h1"))).text
            carname = " ".join(carname.lower().split("\n"))
            car_data["name"] = carname
            carprice = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, "#__next > div > div > main > div.StageArea_container__YuNIp > div.StageArea_informationContainer__VaFP8 > div.Price_mainPriceContainer__syzQE > div:nth-child(1) > div.PriceInfo_styledPriceRow__2fvRD > div > span"))).text
            car_data["price"], car_data["VAT"] = carprice.split("-")

            
            time.sleep(5)
            imgs_div = driver.find_elements(By.CSS_SELECTOR, "#__next > div > div > main > div.StageArea_container__YuNIp > div.Gallery_gallery__MDr8S > div > div > div.image-gallery-thumbnails-wrapper.bottom.thumbnails-swipe-horizontal > div > div > button > img")
            for elem in imgs_div:
                car_ind_link = elem.get_attribute("src") 
                car_image.append(car_ind_link)
            
            car_data["image"] = car_image

            time.sleep(5)
            WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, f"#__next > div > div > main > div.DetailPage_slicesContainer__wHHae > div > div > div.DetailsSection_childrenSection__NQLD7 > button"))).click()
            equipment_value = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, f"#__next > div > div > main > div.DetailPage_slicesContainer__wHHae > div > div > div.DetailsSection_childrenSection__NQLD7 > div > dl > dd > ul"))).text
            car_data["equipment"] = equipment_value.lower()
            

            contactName = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, f"#__next > div > div > main > div.DetailPage_slicesContainer__wHHae > div.VendorAndCtaSection_container__ivfyv > div > div.VendorData_mainContainer__AWyih > div.VendorData_bodyContainer__sJZZC > div.Contact_container__TYO5v > span.Contact_contactName__MFXhS"))).text
            contactNumber = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, f"#__next > div > div > main > div.DetailPage_slicesContainer__wHHae > div.VendorAndCtaSection_container__ivfyv > div > div.VendorData_mainContainer__AWyih > div.VendorData_bodyContainer__sJZZC > div.Contact_container__TYO5v > div > a"))).text
            contactAddress = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, f"#__next > div > div > main > div.DetailPage_slicesContainer__wHHae > div.VendorAndCtaSection_container__ivfyv > div > div.VendorData_mainContainer__AWyih > div.VendorData_bodyContainer__sJZZC > div.Department_openingHoursContainer__VP9fd > div.Department_departmentContainer__uYING > a > div"))).text
            companyName = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, f"#__next > div > div > main > div.DetailPage_slicesContainer__wHHae > div.VendorAndCtaSection_container__ivfyv > div > div.VendorData_mainContainer__AWyih > div.VendorData_bodyContainer__sJZZC > div.RatingsAndCompanyName_container__9_HA4 > div.RatingsAndCompanyName_dealer__HTXk_ > div:nth-child(1)"))).text
            

            car_data["contact_name"] = contactName.lower()
            car_data["contact_number"] = contactNumber.lower()
            car_data["contact_address"] = contactAddress.lower()
            car_data["company_name"] = companyName.lower()

            for i in range(0, 11):
                try:
                    basic_data = WebDriverWait(driver, 20).until(EC.visibility_of_element_located((By.CSS_SELECTOR, f"#__next > div > div > main > div.DetailPage_slicesContainer__wHHae > div:nth-child({i}) > div"))).text
                    feature_data.append(basic_data)
                except:
                    pass
            

            for data in feature_data:
                if data != "":
                    data = data.lower().split("\n")
                    data.pop(0)
                    for key, val in zip(data[::2], data[1::2]):
                        car_data[key] = val
                    
        except:
            pass
        
        if car_data != "":
            all_car_info.append(car_data)
    
    driver.quit()

    _df = pd.DataFrame(all_car_info) 
    read_df = _df.copy()
    read_df = read_df[read_df["name"].notnull()]

    read_df['price'] = read_df['price'].str.replace(r'€', '')
    read_df['price'] = read_df['price'].str.replace(r',', '')
    read_df['price'] = read_df['price'].str.replace(r'.', '')
    read_df['price'] = read_df['price'].str.replace(r' ', '')

    kw_power = []
    for power in read_df["power"]:
        if power != "":
            if isinstance(power, str):
                p, _, _, _= power.split(" ")
                kw_power.append(p)
            else:
                kw_power.append(power)
        else:
            kw_power.append("")

    read_df["power"] = kw_power

    read_df['mileage'] = read_df['mileage'].str.replace(r'km', '')
    read_df['mileage'] = read_df['mileage'].str.replace(r',', '')
    read_df['mileage'] = read_df['mileage'].str.replace(r' ', '')

    fr_year = []
    for year in read_df["first registration"]:
        if isinstance(year, str):
            _, p = year.split("/")
            fr_year.append(p)
        else:
            fr_year.append(year)
    read_df["first registration"] = fr_year

    read_df['equipment'] = read_df['equipment'].str.split('\n')

    read_df.to_csv(f"csv_files/data({st_index}_{to_index}).csv")
    return read_df


@app.route("/")
def index():
    return render_template('index.html')


@app.route("/fetching-data/", methods=['GET', 'POST'])
def fetch_data():
    try:
        if request.method == 'POST':
            start_index = int(request.form.get("st_index"))
            end_index = int(request.form.get("to_index"))
            _df = scrape_data(start_index, end_index)
            msg = "Data has been saved into csv file"
        return render_template('index.html', msg=msg)
    except Exception as e:
        return render_template('index.html', msg=e.args[0])


@app.route("/stop/")
def stop_execution():
    try:
        global driver
        driver.quit()
        msg = "Execution has been stopped"
        return render_template('index.html', msg=msg)
    except Exception as e:
        return render_template('index.html', msg=e.args[0])





if __name__ == '__main__':
    app.run(host="0.0.0.0", debug=False, port=5006)