# 運行以下程式需安裝模組: line-bot-sdk, flask, pyquery
# 安裝方式，輸入指令: pip install 模組名稱

# 引入flask模組
from flask import Flask, request, abort
# 引入linebot相關模組
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
import tempfile, os
import datetime
import openai
import time
import traceback

# 如需增加其他處理器請參閱以下網址的 Message objects 章節
# https://github.com/line/line-bot-sdk-python
from linebot.models import (
    MessageEvent,
    TextMessage,
    StickerMessage,
    TextSendMessage,
    StickerSendMessage,
    LocationSendMessage,
    ImageSendMessage,
    TemplateSendMessage,
    ButtonsTemplate,
    PostbackAction,
    MessageAction,
    URIAction,
    CarouselTemplate,
    CarouselColumn
)


from modules.reply import faq,menu
from modules.currency import get_exchange_table
from modules.app2023 import get_exchange_table2
from modules.app2024 import get_exchange_table3

table=get_exchange_table()
#print(table)

table2=get_exchange_table2()
# print(table2)

table3=get_exchange_table3()
# 定義應用程式是一個Flask類別產生的實例

app = Flask(__name__)
static_tmp_path = os.path.join(os.path.dirname(__file__), 'static', 'tmp')
# LINE的Webhook為了辨識開發者身份所需的資料
# 相關訊息進入網址(https://developers.line.me/console/)
#CHANNEL_ACCESS_TOKEN = 'B9PSwb+aYbK5UiFplp47lNzGm+UPMTKSGdar02wWfQZkXyF3jM7DHEOxM7bzq8SjEn83AA8iJxw59pojw5EBa2w6ELQNwenSD0QvCKXF7WXwUoObGCj3u8cwdTItnDWj1ugk8dmYjBqeV7guah58agdB04t89/1O/w1cDnyilFU='
#CHANNEL_SECRET = '207d15b8d40fa0c6d18cb8f20d717352'

# ********* 以下為 X-LINE-SIGNATURE 驗證程序 *********
line_bot_api = LineBotApi(os.getenv('CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('CHANNEL_SECRET'))
openai.api_key = os.getenv('OPENAI_API_KEY')


def GPT_response(text):
    # 接收回應
    response = openai.Completion.create(model="gpt-3.5-turbo-instruct", prompt=text, temperature=0.5, max_tokens=500)
    print(response)
    # 重組回應
    answer = response['choices'][0]['text'].replace('。','')
    return answer



@app.route("/callback", methods=['POST'])
def callback():
    # 當LINE發送訊息給機器人時，從header取得 X-Line-Signature
    # X-Line-Signature 用於驗證頻道是否合法
    signature = request.headers['X-Line-Signature']

    # 將取得到的body內容轉換為文字處理
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)
    print("[BODY]")
    print(body)

    # 一但驗證合法後，將body內容傳至handler
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'
# ********* 以上為 X-LINE-SIGNATURE 驗證程序 *********


# 文字訊息傳入時的處理器
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    # 當有文字訊息傳入時
    # event.message.text : 使用者輸入的訊息內容
    print('*'*30)
    print('[使用者傳入文字訊息]')
    print(str(event))
    # 取得使用者說的文字
    user_msg = event.message.text
    # 準備要回傳的文字訊息
    reply=menu

    if user_msg in faq:
        reply=faq[user_msg]
    elif user_msg in table:
        bid=table[user_msg]["bid"]
        offer=table[user_msg]["offer"]
        report=f"{user_msg} 買價{bid} 賣價{offer}"
        reply=TextSendMessage(text=report)
    elif user_msg in table2:
        bid=table2[user_msg]["bid2"]
        report=f"{user_msg} 現在價格{bid}"
        reply=TextSendMessage(text=report)
    elif user_msg in table3:
        bid=table3[user_msg]["bid3"]
        report=f"{user_msg} 現在價格{bid}"
        reply=TextSendMessage(text=report)
    else:
        try:
            GPT_answer = GPT_response(user_msg)
            print(GPT_answer)
            line_bot_api.reply_message(event.reply_token, TextSendMessage(GPT_answer))
        except:
            print(traceback.format_exc())
            line_bot_api.reply_message(event.reply_token, TextSendMessage('網路延遲,請五分鐘後再重發一次訊息'))
    




    # 回傳訊息
    # 若需要回覆多筆訊息可使用
    # line_bot_api.reply_message(token, [Object, Object, ...])
    line_bot_api.reply_message(
        event.reply_token,
        reply)


    



#@handler.add(MessageEvent, message=TextMessage)
#def handle_message(event):
#    msg = event.message.text
#    try:
#        GPT_answer = GPT_response(msg)
#        print(GPT_answer)
#        line_bot_api.reply_message(event.reply_token, TextSendMessage(GPT_answer))
#    except:
#        print(traceback.format_exc())
#        line_bot_api.reply_message(event.reply_token, TextSendMessage('你所使用的OPENAI API key額度可能已經超過，請於後台Log內確認錯誤訊息'))




#@handler.add(PostbackEvent)
#def handle_message(event):
#    print(event.postback.data)


#@handler.add(MemberJoinedEvent)
#def welcome(event):
#    uid = event.joined.members[0].user_id
#    gid = event.source.group_id
#    profile = line_bot_api.get_group_member_profile(gid, uid)
#    name = profile.display_name
#    message = TextSendMessage(text=f'{name}歡迎加入')
#    line_bot_api.reply_message(event.reply_token, message)


# 貼圖訊息傳入時的處理器 
@handler.add(MessageEvent, message=StickerMessage)
def handle_sticker_message(event):
    # 當有貼圖訊息傳入時
    print('*'*30)
    print('[使用者傳入貼圖訊息]')
    print(str(event))

    # 準備要回傳的貼圖訊息
    # HINT: 機器人可用的貼圖 https://devdocs.line.me/files/sticker_list.pdf
    #reply = StickerSendMessage(package_id='2', sticker_id='149')
    reply=menu



    # 回傳訊息
    line_bot_api.reply_message(
        event.reply_token,
        reply)


import os
if __name__ == "__main__":
    print('[伺服器開始運行]')
    # 取得遠端環境使用的連接端口，若是在本機端測試則預設開啟於port=5500
    port = int(os.environ.get('PORT', 5500))
    # 使app開始在此連接端口上運行
    print(f'[Flask運行於連接端口:{port}]')
    # 本機測試使用127.0.0.1, debug=True
    # Heroku部署使用 0.0.0.0
    app.run(host='0.0.0.0', port=port, debug=True)
