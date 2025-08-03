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

def calculate_viral_score(views, likes, comments, reposts):
    """
    Принимает views, likes, comments, reposts как int или str (с запятыми),
    возвращает float в диапазоне 0–10.
    """
    try:
        # Приводим к int (удаляем запятые, пробелы)
        P = int(str(views).replace(",", "").replace(" ", ""))
        L = int(str(likes).replace(",", "").replace(" ", ""))
        C = int(str(comments).replace(",", "").replace(" ", ""))
        R = int(str(reposts).replace(",", "").replace(" ", ""))
    except ValueError:
        # Если не смогли преобразовать — возвращаем 0
        return 0.0

    if P == 0:
        return 0.0  # защита от деления на ноль

    # Доли
    like_ratio    = L / P
    comment_ratio = C / P
    repost_ratio  = R / P

    # Взвешенная сумма
    raw_score = (
        like_ratio    * 0.35 +
        comment_ratio * 0.15 +
        repost_ratio  * 0.5
    )

    # Нелинейное масштабирование + подгонка под 10-балльную шкалу
    viral_score = 10 * (raw_score ** 0.55) * 6.5

    # Округляем и ограничиваем максимумом 10
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
