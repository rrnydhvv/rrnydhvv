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

def update_readme():
    player_data = get_data()
    stygian_icon_index = min(max(player_data["stygianIndex"], 1), 6)
    if stygian_icon_index == 6:
            stygian_icon_suffix = "6a" if player_data["stygianSeconds"] > 180 else "6b"
    else:
            stygian_icon_suffix = str(stygian_icon_index)
            
    achievements_icon = "assets/Achievement_Wonders_of_the_World.webp"
    progress_header_icon = "assets/Achievement_Challenger_Series_X.webp"
    general_info_icon = "assets/Genshin_Impact_HoYoLAB.webp"
    abyss_icon = "assets/Achievement_Domains_and_Spiral_Abyss_Series_I.webp"
    theater_icon = f"assets/Imaginarium_Theater_Medal_{player_data['theaterIndex']}.webp"
    stygian_icon = f"assets/Icon_Stygian_Onslaught_Medal_{stygian_icon_suffix}.webp"
    companionship_icon = "assets/Item_Companionship_EXP.webp"
    
    markdown_content = f"""
<div align="center">
  <p><img src="{player_data['avatarUrl']}" width="120" height="120" alt="Avatar"></p>
  <h2>🌠 {player_data['name']}</h2>
  <p><em>"{player_data.get('signature', '') or 'Chưa có chữ ký'}"</em></p>

  <table align="center">
    <a href="#">
      <img src="{player_data['nameCardUrl']}" width="600" alt="Namecard Banner" style="border-radius: 10px;">
    </a>
    <tr>
      <th><img src="{general_info_icon}" width="20" height="20" alt="Genshin Impact"> Thông tin chung</th>
      <th><img src="{progress_header_icon}" width="20" height="20" alt="Progress"> Tiến độ thử thách</th>
    </tr>
    <tr>
      <td><strong>UID:</strong> {UID}</td>
      <td><img src="{achievements_icon}" width="24" height="24" alt="Achievements"> <strong>Thành tựu:</strong> {player_data['achievements']}</td>
    </tr>
    <tr>
      <td><strong>Cấp độ:</strong> AR {player_data['ar']} / WL {player_data['wl']}</td>
      <td><img src="{abyss_icon}" width="24" height="24" alt="Spiral Abyss"> <strong>La Hoàn:</strong> Tầng {player_data['spiralAbyssFloor']}-{player_data['spiralAbyssLevel']} ({player_data['spiralAbyssStar']}★)</td>
    </tr>
    <tr>
      <td><strong>Server:</strong> 🌏 {player_data['region']}</td>
      <td><img src="{theater_icon}" width="24" height="24" alt="Imaginarium Theater"> <strong>Nhà hát:</strong> Màn {player_data['theaterAct']} ({player_data['theaterStars']}★)</td>
    </tr>
    <tr>
      <td><img src="{companionship_icon}" width="24" height="24" alt="Companionship"> <strong>Thân thiết:</strong> ❤️ Max {player_data['maxFriendshipCount']}</td>
      <td><img src="{stygian_icon}" width="24" height="24" alt="Stygian Onslaught"> <strong>Ảo Cảnh:</strong> Cấp {player_data['stygianIndex']} (⏱️ {player_data['stygianSeconds']}s)</td>
    </tr>
  </table>

  <p><sub>Cập nhật: {datetime.datetime.now().strftime('%H:%M - %d/%m/%Y')}</sub></p>
</div>
"""
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
    print("Cập nhật Profile thành công!")

if __name__ == "__main__":
    update_readme()