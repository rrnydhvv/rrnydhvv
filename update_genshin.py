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

def get_live_avatar(uid):
    url = f"https://enka.network/u/{uid}/?info"
    headers = BROWSER_HEADERS
    
    # Thử lại tối đa 3 lần nếu bị timeout
    for i in range(3):
        try:
            # Tăng timeout lên 20 giây để bù đắp mạng chậm
            response = requests.get(url, headers=headers, timeout=20)
            if response.status_code == 200:
                matches = re.findall(r'UI_AvatarIcon_[a-zA-Z0-9_]+', response.text)
                if matches:
                    main_icons = [m for m in matches if "Side" not in m]
                    return main_icons[0] if main_icons else matches[0]
            break # Thoát vòng lặp nếu thành công nhưng không có icon
        except requests.exceptions.Timeout:
            print(f"⚠️ Lần {i+1}: Server phản hồi chậm, đang thử lại...")
            continue 
        except Exception as e:
            print(f"❌ Lỗi: {e}")
            break
            
    return "UI_AvatarIcon_PlayerGirl"

def update_readme():
    try:
        # 1. Lấy dữ liệu thô từ API cho các chỉ số AR, WL, Abyss...
        api_url = f"https://enka.network/api/uid/{UID}?info"
        api_res = requests.get(api_url, headers=API_HEADERS, timeout=10)
        if api_res.status_code != 200:
            print(f"❌ API trả về mã lỗi: {api_res.status_code}")
            return

        data = api_res.json()
        player = data.get("playerInfo", {})

        # 2. Lấy Avatar bằng phương pháp "Đào HTML" vừa test thành công
        icon_name = get_live_avatar(UID)
        avatar_url = f"https://enka.network/ui/{icon_name}.png"

        # 3. Trích xuất các thông số khác
        name = player.get("nickname", "Lumine❤️")
        ar = player.get("level", 0)
        wl = player.get("worldLevel", 0)
        region = data.get("region", "ASIA")
        achievements = player.get("finishAchievementNum", 0)
        fetter_count = player.get("fetterCount", 0)
        tower_floor = player.get("towerFloorIndex", 0)
        tower_level = player.get("towerLevelIndex", 0)
        tower_star = player.get("towerStarIndex", 0)
        theater_act = player.get("theaterActIndex", 0)
        theater_star = player.get("theaterStarIndex", 0)

        if theater_star >= 11:
            theater_icon_index = 5
        elif theater_act > 8:
            theater_icon_index = 4
        elif theater_act > 6:
            theater_icon_index = 3
        elif theater_act > 3:
            theater_icon_index = 2
        else:
            theater_icon_index = 1

        # Ảo cảnh & La hoàn
        stygian_sec = player.get("stygianSeconds", 0)

        stygian_index = player.get("stygianIndex", 0)
        stygian_icon_index = min(max(stygian_index, 1), 6)
        if stygian_icon_index == 6:
            stygian_icon_suffix = "6a" if stygian_sec > 180 else "6b"
        else:
            stygian_icon_suffix = str(stygian_icon_index)

        achievements_icon = "assets/Achievement_Wonders_of_the_World.webp"
        progress_header_icon = "assets/Achievement_Challenger_Series_X.webp"
        abyss_icon = "assets/Achievement_Domains_and_Spiral_Abyss_Series_I.webp"
        theater_icon = f"assets/Imaginarium_Theater_Medal_{theater_icon_index}.webp"
        stygian_icon = f"assets/Icon_Stygian_Onslaught_Medal_{stygian_icon_suffix}.webp"
        companionship_icon = "assets/Item_Companionship_EXP.webp"

        # 4. Render HTML an toàn cho GitHub README
        markdown_content = f"""
<div align="center">
  <p><img src="{avatar_url}" width="120" height="120" alt="Avatar"></p>
  <h2>🌠 {name}</h2>
  <p><em>"{player.get('signature', '') or 'Chưa có chữ ký'}"</em></p>

  <table align="center">
    <tr>
      <th>📊 Thông tin chung</th>
      <th><img src="{progress_header_icon}" width="20" height="20" alt="Progress"> Tiến độ thử thách</th>
    </tr>
    <tr>
      <td><strong>UID:</strong> {UID}</td>
      <td><img src="{achievements_icon}" width="24" height="24" alt="Achievements"> <strong>Thành tựu:</strong> {achievements}</td>
    </tr>
    <tr>
      <td><strong>Cấp độ:</strong> AR {ar} / WL {wl}</td>
      <td><img src="{abyss_icon}" width="24" height="24" alt="Spiral Abyss"> <strong>La Hoàn:</strong> Tầng {tower_floor}-{tower_level} ({tower_star}★)</td>
    </tr>
    <tr>
      <td><strong>Server:</strong> 🌏 {region}</td>
      <td><img src="{theater_icon}" width="24" height="24" alt="Imaginarium Theater"> <strong>Nhà hát:</strong> Màn {theater_act} ({theater_star}★)</td>
    </tr>
    <tr>
      <td><img src="{companionship_icon}" width="24" height="24" alt="Companionship"> <strong>Thân thiết:</strong> ❤️ Max {fetter_count}</td>
      <td><img src="{stygian_icon}" width="24" height="24" alt="Stygian Onslaught"> <strong>Ảo Cảnh:</strong> Cấp {stygian_index} (⏱️ {stygian_sec}s)</td>
    </tr>
  </table>

  <p><sub>Cập nhật: {datetime.datetime.now().strftime('%H:%M - %d/%m/%Y')}</sub></p>
</div>
"""

        # --- GHI VÀO README THEO MỐC START/END ---
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
            # Nếu chưa có mốc thì khởi tạo block ở cuối file.
            base = content.rstrip()
            new_content = f"{base}\n\n{block}\n" if base else f"{block}\n"

        with open("README.md", "w", encoding="utf-8") as f:
            f.write(new_content)
        print("✅ Cập nhật Profile thành công!")

    except Exception as e:
        print(f"Lỗi hệ thống: {e}")

if __name__ == "__main__":
    update_readme()