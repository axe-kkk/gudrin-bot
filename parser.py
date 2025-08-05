import math
import re
import requests
import random
import string

def generate_fake_user():
    response = requests.get("https://randomuser.me/api/")
    response.raise_for_status()
    data = response.json()["results"][0]

    first = data["name"]["first"].capitalize()
    last = data["name"]["last"].capitalize()
    name = f"{first} {last}"
    email = data["email"]
    phone_raw = data["phone"]

    phone_digits = ''.join(filter(str.isdigit, phone_raw))
    phone = "380" + phone_digits[-9:] if len(phone_digits) >= 9 else "38096" + ''.join(random.choices("0123456789", k=7))

    password = ''.join([
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        *random.choices(string.ascii_letters + string.digits, k=7)
    ])

    return {
        "name": name,
        "email": email,
        "phone": phone,
        "password": password
    }
import math


def calculate_viral_score(views, likes, comments, reposts):
    try:
        V = int(str(views).replace(",", "").replace(" ", ""))
        L = int(str(likes).replace(",", "").replace(" ", ""))
        C = int(str(comments).replace(",", "").replace(" ", ""))
        R = int(str(reposts).replace(",", "").replace(" ", ""))
    except ValueError:
        return 0.0

    if V < 100:
        return 0.0

    # ER и CR
    ER = (L + C + R) / V * 100
    CR = R / V * 100

    # Сглаженные репосты
    R_adj = math.log10(R + 1) * 10

    # Весы
    weight_likes = 0.03
    weight_comments = 0.3
    weight_reposts = 0.45

    engagement_score = (L * weight_likes + C * weight_comments + R_adj * weight_reposts)
    scale_factor = math.log10(V + 1) ** 0.5
    raw_score = engagement_score * scale_factor

    # Ограниченный буст от ER/CR
    er_boost = min(ER / 2, 2)
    cr_boost = min(CR * 10, 2)

    viral_score = (raw_score / 20000) + er_boost + cr_boost

    # 🔻 Штраф за маленькую базу просмотров
    if V < 500:
        viral_score *= 0.5
    if V < 200:
        viral_score *= 0.2

    return round(min(viral_score, 10), 2)

    return round(min(viral_score, 10), 2)




def register_and_extract(request: str):
    session = requests.Session()
    user = generate_fake_user()
    print("👤 Пользователь:", user)

    login_page = session.get("https://web.recreate.video/register")
    token = login_page.text.split('name="_token" value="')[1].split('"')[0]

    reg_data = {
        "_token": token,
        "name": user["name"],
        "email": user["email"],
        "phone_number": user["phone"],
        "password": user["password"],
        "password_confirmation": user["password"],
    }

    resp = session.post("https://web.recreate.video/register", data=reg_data, allow_redirects=True)
    print("✅ Регистрация статус:", resp.status_code)

    ban_symbols = set(r"""./\,:;'"!?@#$%^&*()[]{}<>~`+=|""")
    cleaned = ''.join(char for char in request if char not in ban_symbols)
    words = cleaned.split()
    formatted = ''.join(word.capitalize() for word in words)

    html = session.get(f"https://web.recreate.video/library/{formatted}").text

    start = 0
    i = 0
    res = []

    while True:
        start = html.find('onClick="showVideo(', start)
        if start == -1:
            return res

        start_args = html.find("(", start) + 1
        end_args = html.find(")", start_args)
        args_raw = html[start_args:end_args]
        args = [x.strip().strip("'").strip('"') for x in args_raw.split(",")]

        if len(args) < 12:
            start = end_args + 1
            continue

        views = args[-8]
        likes = args[-7]
        comments = args[-6]
        reposts = args[-5]
        saves = args[-4]
        er = args[-2]
        cr = args[-1]
        short_id = args[-3]

        viral_score = calculate_viral_score(views, likes, comments, reposts)

        if viral_score < 1:
            start = end_args + 1
            continue

        start = html.find('<span class="text-white opacity-30">', start)
        if start == -1:
            break

        start_args = html.find(">", start) + 1
        end_args = html.find("<", start_args)
        args_raw = html[start_args:end_args]
        args_ = args_raw.split(" ")

        if len(args_) >= 2 and args_[1] == "m":
            if int(args_[0]) > 1:
                print(False)
            else:

                i += 1
                print(f"\n🎞️ Видео #{i}")
                print(f"👁️ Views: {views}, ❤️ Likes: {likes}, 💬 Comments: {comments}")
                print(f"🔁 Reposts: {reposts}, 💾 Saves: {saves}")
                print(f"🧠 ER/View: {er}, 📈 CR/View: {cr}")
                print(f"📊 Viral Score: {viral_score}/10")
                print(f"📎 Instagram: https://www.instagram.com/reel/{short_id}")

                res.append({
                    "views": views,
                    "likes": likes,
                    "comments": comments,
                    "reposts": reposts,
                    "saves": saves,
                    "er": er,
                    "cr": cr,
                    "short_id": short_id,
                    "viral_score": viral_score
                })

        start = end_args + 1

if __name__ == "__main__":
    register_and_extract("Veo }| 3")
