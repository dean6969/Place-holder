from flask import Flask, request
import json, random
from datetime import date, datetime
from pytz import timezone
import pytz

app = Flask(__name__)
with open('food_nutrition.json', encoding='utf-8-sig') as f:
        data_nutrition = json.load(f)
with open('breakfast_lose_weight.json', encoding='utf-8-sig') as f:
        data_breakfast_lose_weight = json.load(f)
with open('breakfast_gain_weight.json', encoding='utf-8-sig') as f:
        data_breakfast_gain_weight = json.load(f)
with open('lunch_lose_weight.json', encoding='utf-8-sig') as f:
        data_lunch_lose_weight = json.load(f)
with open('lunch_gain_weight.json', encoding='utf-8-sig') as f:
        data_lunch_gain_weight = json.load(f)
with open('dinner_lose_weight.json', encoding='utf-8-sig') as f:
        data_dinner_lose_weight = json.load(f)
with open('dinner_gain_weight.json', encoding='utf-8-sig') as f:
        data_dinner_gain_weight = json.load(f) 

# time set
vietnam_timezone = timezone('Asia/Ho_Chi_Minh')
datetime = datetime.now(vietnam_timezone)
today = date.today()

date = today.strftime("%d")
month = today.strftime("%m")
year = today.strftime("%Y")
day = today.strftime("%A")
hour = datetime.strftime("%H")
minute = datetime.strftime("%M")

convertDay = {
  "Sunday": "Chủ Nhật",
  "Monday": "Thứ hai",
  "Tuesday": "Thứ ba",
  "Wednesday": "Thứ tư",
  "Thursday": "Thứ năm",
  "Friday": "Thứ sáu",
  "Saturday": "Thứ bảy",
}
day = convertDay[day]

@app.route('/') 
def hello(): 
    return "Các tính năng: \n * Tra cứu các chỉ số dinh dưỡng trong thực phẩm, đồ ăn, rau củ quả\n * Tính chỉ số BMI, BMR,... từ đó đưa ra lời khuyên về tình trạng sức khỏe \n * Cung cấp thực đơn tăng cân, giảm cân dựa vào chỉ số người dùng \n * Giải đáp thắc mắc những kiến thức dinh dưỡng, sức khỏe trong việc tăng cân, giảm cân, các chế độ ăn phổ biến"

@app.route('/webhook', methods=['POST'])
def webhook():
  req_dialog = request.get_json(silent=True, force=True) # Đọc JSON
  query_result = req_dialog.get('queryResult') # Lấy query result 
  query_text = query_result.get('queryText') # Lấy text của user
  action = query_result.get('action') # Lấy action 
  parameters = query_result.get('parameters') # Lấy parameter do user nhập vào ô chat
  outputContext = query_result.get('outputContexts') # Lấy context do user đã đăng kí

  if action == "input.welcome":
    parameters_context = outputContext[0].get('parameters')
    ten_user = parameters_context.get('ten')
    currentTime = datetime
    message = 'Chào bạn {}! '.format(ten_user)
    if currentTime.hour < 12:
      message += 'Chúc bạn có một ngày mới tốt lành!'
    elif 12 <= currentTime.hour < 18:
      message += 'Chúc bạn có một buổi chiều đầy niềm vui!'
    else:
      message += 'Chúc bạn có một buổi tối vui vẻ!'
    message += '\nMình là PhoTalk. Mình có thể giúp gì được cho bạn?'
    return {
    "fulfillmentMessages": [
        {
          "text": {
            "text": [message]
          }
        },
      ]
    }
  
  if action == "hoi.dap.thoi.gian":
    message = "Bây giờ là {} giờ {} phút theo giờ Việt Nam (UTC +7)".format(hour, minute)
    return {
    "fulfillmentMessages": [
        {
          "text": {
            "text": [message]
          }
        }
      ]
    }

  if action == "hoi.dap.ngay.thang":
    message = "Hôm nay là {}, ngày {} tháng {} năm {}".format(day, date, month, year)
    return {
    "fulfillmentMessages": [
        {
          "text": {
            "text": [message]
          }
        }
      ]
    }

  if action == "tra.cuu.dinh.duong":
    ten_thuc_pham = parameters.get('ten_thuc_pham')
    parameters_context = outputContext[0].get('parameters') # Lấy parameter trong context
    ten_thuc_pham_original = parameters_context.get('ten_thuc_pham.original')
    so_luong = parameters.get('so_luong')

    for food in data_nutrition:
        if (food['name'] == ten_thuc_pham): 
            image = food['image']
            if 'quantity' in food: # Vào bảng 2
              message = 'Trong ' + food['quantity'] + ' ' + ten_thuc_pham_original + ' có chứa ' + food["calories"] + ' calories bạn nha! '

            else: # Vào bảng 1 
                message = 'Trong 100g ' + ten_thuc_pham_original + ' có chứa ' + food["calories"] + ' calories, ' + food["fat"] + 'g chất béo (fat), và ' + food["carb"] + 'g carbohydrate bạn nha! '
            if len(str(so_luong)) != 0: message += 'Bạn có thể tham khảo số liệu này, từ đó bạn có thể tính được dinh dưỡng có trong ' + so_luong + ' ' + ten_thuc_pham_original + ' nha!'
    return {
    "fulfillmentMessages": [
        {
          "text": {
            "text": [message]
          }
        },
        {
          "payload": {
            "image": image
          }
        }
      ]
    }

  if action == "khach.hang.hoi.thuc.don":
    parameters_context = {}
    for output in range(len(outputContext)):
      parameters_context.update(outputContext[output].get('parameters'))# Lấy parameter trong context
    bmi = float(parameters_context.get("bmi"))
    phan_loai = parameters_context.get('phan_loai')
    yeu_cau_cua_user = parameters_context.get('yeu_cau_cua_user')
    message = 'Hiện tại, bạn đang có chỉ số BMI là {}. '.format(bmi) 

    message += 'Thể trạng của bạn hiện tại đang {}. '.format(phan_loai)
    if (bmi < 18.5): # gầy, thiếu cân 
      if (yeu_cau_cua_user == 'tăng cân'): 
        message += 'Mình sẽ đưa ra chế độ tăng cân phù hợp với cơ thể bạn. Bạn có đồng ý không nhỉ?'
      if (yeu_cau_cua_user == 'giảm cân'): 
        message += 'Nếu bạn tiếp tục giảm cân thì sẽ ảnh hưởng đến sức khỏe của bạn. Mình khuyên bạn nên theo chế độ tăng cân. Bạn có đồng ý không nhỉ?'
    elif (bmi >= 18.5) and (bmi <= 24.9): # người bình thường
      message += 'Mình sẽ đưa ra chế độ {} phù hợp với cơ thể bạn. Bạn có đồng ý không?'.format(yeu_cau_cua_user)

    else: # người béo 
      if (yeu_cau_cua_user == 'giảm cân'): 
        message += 'Mình sẽ đưa ra chế độ giảm cân phù hợp với cơ thể bạn. Bạn có đồng ý không nhỉ?'
      if (yeu_cau_cua_user == 'tăng cân'): 
        message += 'Nếu bạn tiếp tục tăng cân thì sẽ ảnh hưởng đến sức khỏe của bạn. Mình khuyên bạn nên theo chế độ giảm cân. Bạn có đồng ý không nhỉ?'

    return {
    "fulfillmentMessages": [
        {
          "text": {
            "text": [message]
          }
        }
      ]
    }
    

  if action == "hoi.thoi.gian.thuc.don":
    parameters_context = outputContext[1].get('parameters')
    yeu_cau_cua_user = parameters_context.get('yeu_cau_cua_user')
    phan_loai = parameters_context.get('phan_loai')
    bmi = float(parameters_context.get("bmi"))
    tdee = round(parameters_context.get("tdee"))
    if (phan_loai == 'bình thường'): 
      if (yeu_cau_cua_user == 'tăng cân'): 
        tdee += 1000
      else: 
        tdee -= 1000
    elif (phan_loai == 'gầy, thiếu cân'): tdee += 1000
    else: tdee -= 1000
    message = "Hiện tại bạn đang cần nạp {} calories/ngày.".format(tdee) + " Bạn muốn mình đưa ra thực đơn vào bữa nào trong ngày?"

    return {
      "fulfillmentMessages": [
        {
          "text": {
            "text": [message]
          }
        },
        {
          "payload": {
            "quickReplies": [
              {
                "title": "Sáng",
                "value": "Sáng",
              },
              {
                "title": "Trưa",
                "value": "Trưa",
              },
              {
                "title": "Tối",
                "value": "Tối",
              },
            ]
          }
        },
      ]
    }


  if action == "dua.ra.thuc.don.bua.sang":
    parameters_context_1 = outputContext[1].get('parameters') # Lấy parameter trong context
    parameters_context_2 = outputContext[2].get('parameters')
    yeu_cau_cua_user = parameters_context_2.get('yeu_cau_cua_user')
    if (yeu_cau_cua_user == 'giảm cân'):
      food_dict = random.choice(data_breakfast_lose_weight)
    else: food_dict = random.choice(data_breakfast_gain_weight)
    food_list = []
    message = 'Sau đây là thực đơn bữa sáng dành cho bạn:'
    food_list.append(
      {
        "text": {
          "text": [message]
        }
      }
    )
    for key, value in food_dict.items():
        if 'Name' in key: 
          food_list.append(
              {
              "text": {
                "text": [value]
              }
            }
          )
        else: 
          food_list.append(
            {
              "payload": {
                "image": value
              }
            }
          )
    return {
      "fulfillmentMessages": food_list
    }

  if action == "dua.ra.thuc.don.bua.trua":
    parameters_context_1 = outputContext[1].get('parameters') # Lấy parameter trong context
    parameters_context_2 = outputContext[2].get('parameters')
    yeu_cau_cua_user = parameters_context_2.get('yeu_cau_cua_user')
    if (yeu_cau_cua_user == 'giảm cân'):
      food_dict = random.choice(data_lunch_lose_weight)
    else: food_dict = random.choice(data_lunch_gain_weight)
    food_list = []
    message = 'Sau đây là thực đơn bữa trưa dành cho bạn:'
    food_list.append(
      {
        "text": {
          "text": [message]
        }
      }
    )
    for key, value in food_dict.items():
        if 'Name' in key: 
          food_list.append(
              {
              "text": {
                "text": [value]
              }
            }
          )
        else: 
          food_list.append(
            {
              "payload": {
                "image": value
              }
            }
          )
    return {
      "fulfillmentMessages": food_list
    }

  if action == "dua.ra.thuc.don.bua.toi":
    parameters_context_2 = outputContext[2].get('parameters')
    yeu_cau_cua_user = parameters_context_2.get('yeu_cau_cua_user')
    if (yeu_cau_cua_user == 'giảm cân'):
      food_dict = random.choice(data_dinner_lose_weight)
    else: food_dict = random.choice(data_dinner_gain_weight)
    food_list = []
    message = 'Sau đây là thực đơn bữa tối dành cho bạn:'
    food_list.append(
      {
        "text": {
          "text": [message]
        }
      }
    )
    for key, value in food_dict.items():
        if 'Name' in key: 
          food_list.append(
              {
              "text": {
                "text": [value]
              }
            }
          )
        else: 
          food_list.append(
            {
              "payload": {
                "image": value
              }
            }
          )
    return {
      "fulfillmentMessages": food_list
    }

if __name__ == '__main__':
  #app.run()
  app.run(host='0.0.0.0', port=8080)