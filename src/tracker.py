from datetime import date, datetime, timedelta
import os
from typing import Any, Dict, List
import requests

LINE_MULTICAST_URL = "https://api.line.me/v2/bot/message/multicast"
LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_IDS = os.getenv("LINE_USER_ID", "")

# กำหนดเมืองเป้าหมายในญี่ปุ่น (บินตรงจาก BKK / DMK)
DESTINATIONS = {
    "NGO": {"name": "Nagoya", "icon": "🗾", "color": "#1DB446"},
    "KIX": {"name": "Osaka", "icon": "🏯", "color": "#FF9800"},
    "NRT": {"name": "Tokyo", "icon": "🗼", "color": "#2196F3"},
    "FUK": {"name": "Fukuoka", "icon": "🍜", "color": "#9C27B0"},
}


def get_target_date_pairs() -> List[Dict[str, Any]]:
    """สร้างช่วงวันเดินทาง พ.ย. - ธ.ค. 2026 (7-8 วัน)"""
    date_pairs = []
    curr = date(2026, 11, 1)
    end_limit = date(2026, 12, 31)

    while curr <= end_limit:
        for total_days in [7, 8]:
            ret = curr + timedelta(days=total_days - 1)
            if ret <= end_limit:
                date_pairs.append(
                    {
                        "depart": curr.strftime("%Y-%m-%d"),
                        "return": ret.strftime("%Y-%m-%d"),
                        "total_days": total_days,
                        "net_vacation_days": total_days - 2,
                    }
                )
        curr += timedelta(days=1)
    return date_pairs


def fetch_multi_city_deals() -> Dict[str, List[Dict[str, Any]]]:
    """Mock/Real Flight Offers แบ่งตามปลายทาง (Direct Flight Only)"""
    return {
        "NGO": [
            {
                "airline": "Thai AirAsia X",
                "origin": "DMK",
                "dest": "NGO",
                "depart": "2026-11-10",
                "return": "2026-11-17",
                "total_days": 8,
                "net_days": 6,
                "price": 12450,
            },
            {
                "airline": "Thai Airways",
                "origin": "BKK",
                "dest": "NGO",
                "depart": "2026-11-24",
                "return": "2026-11-30",
                "total_days": 7,
                "net_days": 5,
                "price": 21800,
            },
        ],
        "KIX": [
            {
                "airline": "Peach Aviation",
                "origin": "BKK",
                "dest": "KIX",
                "depart": "2026-11-12",
                "return": "2026-11-19",
                "total_days": 8,
                "net_days": 6,
                "price": 11900,
            },
            {
                "airline": "Thai AirAsia X",
                "origin": "DMK",
                "dest": "KIX",
                "depart": "2026-12-02",
                "return": "2026-12-09",
                "total_days": 8,
                "net_days": 6,
                "price": 13500,
            },
        ],
        "NRT": [
            {
                "airline": "Thai AirAsia X",
                "origin": "DMK",
                "dest": "NRT",
                "depart": "2026-11-15",
                "return": "2026-11-22",
                "total_days": 8,
                "net_days": 6,
                "price": 13800,
            },
            {
                "airline": "ZIPAIR",
                "origin": "BKK",
                "dest": "NRT",
                "depart": "2026-12-05",
                "return": "2026-12-12",
                "total_days": 8,
                "net_days": 6,
                "price": 14200,
            },
        ],
        "FUK": [
            {
                "airline": "Thai Vietjet",
                "origin": "BKK",
                "dest": "FUK",
                "depart": "2026-11-18",
                "return": "2026-11-25",
                "total_days": 8,
                "net_days": 6,
                "price": 9800,
            },
            {
                "airline": "Thai AirAsia",
                "origin": "DMK",
                "dest": "FUK",
                "depart": "2026-12-08",
                "return": "2026-12-15",
                "total_days": 8,
                "net_days": 6,
                "price": 10500,
            },
        ],
    }


def create_city_bubble(
    dest_code: str,
    city_info: Dict[str, str],
    deals: List[Dict[str, Any]],
    timestamp: str,
) -> Dict[str, Any]:
    """สร้าง Bubble สำหรับ 1 เมือง"""
    best_price = min([d["price"] for d in deals]) if deals else 0

    contents: List[Dict[str, Any]] = [
        {
            "type": "text",
            "text": f"{city_info['icon']} {city_info['name'].upper()} ({dest_code})",
            "weight": "bold",
            "size": "lg",
            "color": city_info["color"],
        },
        {
            "type": "text",
            "text": f"เริ่มต้น ฿{best_price:,} • บินตรง 7-8 วัน",
            "size": "xs",
            "color": "#666666",
            "margin": "xs",
        },
        {"type": "separator", "margin": "md"},
    ]

    for d in deals[:3]:
        booking_url = (
            f"https://www.google.com/travel/flights?q=Flights%20to%20{d['dest']}%20"
            f"from%20{d['origin']}%20on%20{d['depart']}%20through%20{d['return']}%20nonstop"
        )

        item_box = {
            "type": "box",
            "layout": "vertical",
            "margin": "md",
            "spacing": "xs",
            "action": {
                "type": "uri",
                "label": "View Flight",
                "uri": booking_url,
            },
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"฿{d['price']:,}",
                            "weight": "bold",
                            "size": "md",
                            "color": "#E53935",
                        },
                        {
                            "type": "text",
                            "text": f"{d['airline']}",
                            "size": "xxs",
                            "align": "end",
                            "color": "#555555",
                        },
                    ],
                },
                {
                    "type": "text",
                    "text": f"📅 {d['depart']} ถึง {d['return']}",
                    "size": "xs",
                    "color": "#333333",
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"⏳ {d['total_days']} วัน (เที่ยว ~{d['net_days']} วัน) | {d['origin']}",
                            "size": "xxs",
                            "color": "#777777",
                            "flex": 4,
                        },
                        {
                            "type": "text",
                            "text": "ดูตั๋ว ➔",
                            "size": "xxs",
                            "color": city_info["color"],
                            "align": "end",
                            "weight": "bold",
                            "flex": 2,
                        },
                    ],
                },
                {"type": "separator", "margin": "sm"},
            ],
        }
        contents.append(item_box)

    return {
        "type": "bubble",
        "size": "kilo",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": contents,
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": f"อัปเดตเมื่อ {timestamp}",
                    "size": "xxs",
                    "color": "#AAAAAA",
                    "align": "center",
                }
            ],
        },
    }


def build_flex_carousel(
    multi_city_deals: Dict[str, List[Dict[str, Any]]],
) -> Dict[str, Any]:
    now_bkk = (datetime.utcnow() + timedelta(hours=7)).strftime(
        "%d/%m/%Y %H:%M"
    )
    bubbles = []

    for code, info in DESTINATIONS.items():
        deals = multi_city_deals.get(code, [])
        if deals:
            sorted_deals = sorted(deals, key=lambda x: x["price"])
            bubble = create_city_bubble(code, info, sorted_deals, now_bkk)
            bubbles.append(bubble)

    return {
        "type": "flex",
        "altText": "✈️ สรุปเปรียบเทียบราคาตั๋วบินตรงไปญี่ปุ่น (พ.ย. - ธ.ค.)",
        "contents": {"type": "carousel", "contents": bubbles},
    }


def send_line_push(flex_message: Dict[str, Any]) -> None:
    if not LINE_TOKEN or not LINE_USER_IDS:
        raise ValueError("Missing LINE_CHANNEL_ACCESS_TOKEN or LINE_USER_ID")

    recipient_list = [
        uid.strip() for uid in LINE_USER_IDS.split(",") if uid.strip()
    ]
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}",
    }
    payload = {"to": recipient_list, "messages": [flex_message]}

    res = requests.post(
        LINE_MULTICAST_URL, headers=headers, json=payload, timeout=10
    )
    res.raise_for_status()


if __name__ == "__main__":
    multi_city_deals = fetch_multi_city_deals()
    message = build_flex_carousel(multi_city_deals)
    send_line_push(message)
