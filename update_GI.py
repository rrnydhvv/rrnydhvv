import base64
import os
import requests
import re
import datetime

UID = '826350117'

BROWSER_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36",
    "Accept-Language": "vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

API_HEADERS = {
    "User-Agent": BROWSER_HEADERS["User-Agent"],
    "Accept-Language": BROWSER_HEADERS["Accept-Language"],
    "Accept": "application/json,text/plain,*/*",
}

def get_base64_from_url(url):
    """Lấy ảnh từ URL và chuyển sang Base64 với Headers đầy đủ"""
    if not url:
        return ""
    try:
        # Sử dụng API_HEADERS để giả lập trình duyệt, tránh bị server chặn
        response = requests.get(url, headers=API_HEADERS, timeout=15)
        if response.status_code == 200:
            content_type = response.headers.get('content-type', 'image/png')
            encoded = base64.b64encode(response.content).decode('utf-8')
            return f"data:{content_type};base64,{encoded}"
        else:
            print(f"Lỗi {response.status_code} khi tải ảnh: {url}")
            return ""
    except Exception as e:
        print(f"Không thể tải ảnh từ URL: {e}")
        return ""

def get_base64_image(image_path):
    """Chuyển ảnh cục bộ trong assets sang Base64"""
    if not os.path.exists(image_path):
        print(f"Cảnh báo: Không tìm thấy file {image_path}")
        return ""
    try:
        with open(image_path, "rb") as img_file:
            # Xác định định dạng file để ghi đúng MIME type
            ext = os.path.splitext(image_path)[1].replace(".", "")
            mime = "image/webp" if ext == "webp" else f"image/{ext}"
            encoded = base64.b64encode(img_file.read()).decode('utf-8')
            return f"data:{mime};base64,{encoded}"
    except Exception as e:
        print(f"Lỗi khi đọc file local: {e}")
        return ""

def get_data():
    try:
        # 1.Gọi API để làm mới dữ liệu trên server của Akasha trước khi lấy thông tin
        refresh_api_url = f"https://akasha.cv/api/user/refresh/{UID}"
        curl = requests.get(refresh_api_url, headers=API_HEADERS)

        # 2. Lấy dữ liệu từ API cho các chỉ số AR, WL, Abyss...
        api_url = f"https://akasha.cv/api/user/{UID}"
        data = requests.get(api_url, headers=API_HEADERS).json()
        data = data.get("data", {}).get("account", {})
        
        avtUrl = data.get("profilePictureLink", "")
        nameCardUrl = data.get("nameCardLink", "")
        playerInfo = data.get("playerInfo", {})
        
        achievements = int(playerInfo.get("finishAchievementNum", 0))
        maxFriendshipCount = int(playerInfo.get("maxFriendshipCount", 0))
        region = playerInfo.get("region", "")
        
        spiralAbyssFloor = int(playerInfo.get("towerFloorIndex", 0))
        spiralAbyssLevel = int(playerInfo.get("towerLevelIndex", 0))
        spiralAbyssStar = int(playerInfo.get("towerStarIndex", 0))
        
        theater_data = playerInfo.get("theater", {})
        act = int(theater_data.get("act", 0))
        modeIndex = int(theater_data.get("modeIndex", 0))
        MODE_MAP = {
            95: {"index": 1,"name": "Easy", "total_act": 3},
            91: {"index": 2,"name": "Normal", "total_act": 6},
            97: {"index": 3,"name": "Hard", "total_act": 8},
            93: {"index": 4,"name": "Visionary", "total_act": 10},
            99: {"index": 5,"name": "Lunar", "total_act": 12}
        }
        mode = MODE_MAP.get(modeIndex, {"name": "Unknown", "total_act": 0})
        stars = int(theater_data.get("stars", 0))
        
        stygianIndex = int(playerInfo.get("stygianIndex", 0))
        stygianSeconds = int(playerInfo.get("stygianSeconds", 0))
        
        name = playerInfo.get("nickname", "")
        ar = int(playerInfo.get("level", 0))
        wl = int(playerInfo.get("worldLevel", 0))
        signature = playerInfo.get("signature", "")
        
        return {
            "name": name,
            "ar": ar,
            "wl": wl,
            "region": region,
            "achievements": achievements,
            "maxFriendshipCount": maxFriendshipCount,
            "spiralAbyssFloor": spiralAbyssFloor,
            "spiralAbyssLevel": spiralAbyssLevel,
            "spiralAbyssStar": spiralAbyssStar,
            "theaterAct": act,
            "theaterModeName": mode["name"],
            "theaterTotalActs": mode["total_act"],
            "theaterIndex": mode["index"],
            "theaterStars": stars,
            "stygianIndex": stygianIndex,
            "stygianSeconds": stygianSeconds,
            "signature": signature,
            "avatarUrl": avtUrl,
            "nameCardUrl": nameCardUrl
        }
    except Exception as e:
        print(f"{e}")

def generate_svg(player_data):
    # Xử lý Logic Stygian Icon
    stygian_icon_index = min(max(player_data["stygianIndex"], 1), 6)
    if stygian_icon_index == 6:
        stygian_icon_suffix = "6a" if player_data["stygianSeconds"] > 180 else "6b"
    else:
        stygian_icon_suffix = str(stygian_icon_index)
        
    # Chuyển toàn bộ icon sang Base64
    achievements_icon = get_base64_image("assets/Achievement_Wonders_of_the_World.webp")
    progress_header_icon = get_base64_image("assets/Achievement_Challenger_Series_X.webp")
    general_info_icon = get_base64_image("assets/Genshin_Impact_HoYoLAB.webp")
    abyss_icon = get_base64_image("assets/Achievement_Domains_and_Spiral_Abyss_Series_I.webp")
    theater_icon = get_base64_image(f"assets/Imaginarium_Theater_Medal_{player_data['theaterIndex']}.webp")
    stygian_icon = get_base64_image(f"assets/Icon_Stygian_Onslaught_Medal_{stygian_icon_suffix}.webp")
    companionship_icon = get_base64_image("assets/Item_Companionship_EXP.webp")
    
    # Lấy Base64 cho Namecard và Avatar để tránh lỗi CORS của GitHub
    namecard_b64 = get_base64_from_url(player_data['nameCardUrl'])
    avatar_b64 = get_base64_from_url(player_data['avatarUrl'])

    # Code SVG với tọa độ mô phỏng bảng
    FONT_MAIN = "'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif"
    svg_content = f"""
    <svg width="800" height="480" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
        <defs>
            <clipPath id="avatar-clip">
                <circle cx="400" cy="80" r="60" />
            </clipPath>
            <clipPath id="card-clip">
                <rect x="0" y="0" width="800" height="480" rx="15" ry="15" />
            </clipPath>
        </defs>

        <g clip-path="url(#card-clip)">
            <image href="{namecard_b64}" x="0" y="0" width="800" height="480" preserveAspectRatio="xMidYMid slice" />
            <rect x="0" y="0" width="800" height="480" fill="#1c1c24" opacity="0.4" />
        </g>

        <image href="{avatar_b64}" x="340" y="20" width="120" height="120" clip-path="url(#avatar-clip)" />
        <text x="400" y="175" font-family="{FONT_MAIN}" font-size="24" font-weight="bold" fill="#ffffff" text-anchor="middle" letter-spacing="1">
            🌠 {player_data['name']}
        </text>
        <text x="400" y="205" font-family="{FONT_MAIN}" font-size="16" fill="#cccccc" text-anchor="middle" font-style="italic" letter-spacing="0.5">
            "{player_data.get('signature', '') or 'Chưa có chữ ký'}"
        </text>

        <image href="{general_info_icon}" x="90" y="245" width="24" height="24" />
        <text x="125" y="264" font-family="{FONT_MAIN}" font-size="18" font-weight="bold" fill="#ffffff">Thông tin chung</text>

        <text x="90" y="310" font-family="{FONT_MAIN}" font-size="16" fill="#ffffff"><tspan font-weight="bold">UID:</tspan> {UID}</text>
        <text x="90" y="350" font-family="{FONT_MAIN}" font-size="16" fill="#ffffff"><tspan font-weight="bold">Cấp độ:</tspan> AR {player_data['ar']} / WL {player_data['wl']}</text>
        <text x="90" y="390" font-family="{FONT_MAIN}" font-size="16" fill="#ffffff"><tspan font-weight="bold">Server:</tspan> 🌏 {player_data['region']}</text>

        <image href="{companionship_icon}" x="90" y="415" width="24" height="24" />
        <text x="125" y="433" font-family="{FONT_MAIN}" font-size="16" fill="#ffffff"><tspan font-weight="bold">Thân thiết:</tspan> ❤️ Max {player_data['maxFriendshipCount']}</text>

        <image href="{progress_header_icon}" x="450" y="245" width="24" height="24" />
        <text x="485" y="264" font-family="{FONT_MAIN}" font-size="18" font-weight="bold" fill="#ffffff">Tiến độ thử thách</text>

        <image href="{achievements_icon}" x="450" y="292" width="24" height="24" />
        <text x="485" y="310" font-family="{FONT_MAIN}" font-size="16" fill="#ffffff"><tspan font-weight="bold">Thành tựu:</tspan> {player_data['achievements']}</text>

        <image href="{abyss_icon}" x="450" y="332" width="24" height="24" />
        <text x="485" y="350" font-family="{FONT_MAIN}" font-size="16" fill="#ffffff"><tspan font-weight="bold">La Hoàn:</tspan> Tầng {player_data['spiralAbyssFloor']}-{player_data['spiralAbyssLevel']} ({player_data['spiralAbyssStar']}★)</text>

        <image href="{theater_icon}" x="450" y="372" width="24" height="24" />
        <text x="485" y="390" font-family="{FONT_MAIN}" font-size="16" fill="#ffffff"><tspan font-weight="bold">Nhà hát:</tspan> Màn {player_data['theaterAct']} ({player_data['theaterStars']}★)</text>

        <image href="{stygian_icon}" x="450" y="412" width="24" height="24" />
        <text x="485" y="430" font-family="{FONT_MAIN}" font-size="16" fill="#ffffff"><tspan font-weight="bold">Ảo Cảnh:</tspan> Cấp {player_data['stygianIndex']} (⏱️ {player_data['stygianSeconds']}s)</text>
        
        <text x="400" y="465" font-family="{FONT_MAIN}" font-size="12" fill="#888888" text-anchor="middle">
            Cập nhật: {datetime.datetime.now().strftime('%H:%M - %d/%m/%Y')}
        </text>
    </svg>
    """
    with open("profile.svg", "w", encoding="utf-8") as f:
        f.write(svg_content.strip())
    print("Đã tạo file profile.svg thành công!")

def update_readme():
    player_data = get_data()
    if not player_data:
        return
        
    generate_svg(player_data)

    # Thay vì chèn code HTML dài dòng, giờ chỉ cần gọi đúng file SVG
    markdown_content = f"""
<div align="center">
  <img src="./profile.svg" alt="Genshin Profile">
</div>
"""
    # Logic update_readme bên dưới của bạn giữ nguyên...
    start_tag = "<!-- GENSHIN_PROFILE_START -->"
    end_tag = "<!-- GENSHIN_PROFILE_END -->"

    with open("README.md", "r", encoding="utf-8") as f:
        content = f.read()

    block = f"{start_tag}\n{markdown_content.strip()}\n{end_tag}"
    start_idx = content.find(start_tag)
    end_idx = content.find(end_tag)

    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
        end_idx += len(end_tag)
        new_content = f"{content[:start_idx]}{block}{content[end_idx:]}"
    else:
        base = content.rstrip()
        new_content = f"{base}\n\n{block}\n" if base else f"{block}\n"

    with open("README.md", "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Cập nhật README thành công!")

if __name__ == "__main__":
    update_readme()
 