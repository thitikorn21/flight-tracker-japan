from datetime import date, datetime, timedelta
import os
from typing import Any, Dict, List
import requests

LINE_PUSH_URL = "https://api.line.me/v2/bot/message/push"
LINE_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
LINE_USER_ID = os.getenv("LINE_USER_ID")


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


def fetch_best_deals() -> List[Dict[str, Any]]:
    """Mock/Real Flight Offers (Direct Flight Only)"""
    return [
        {
            "airline": "Thai AirAsia X (XJ)",
            "origin": "DMK",
            "depart": "2026-11-10",
            "return": "2026-11-17",
            "total_days": 8,
            "net_days": 6,
            "price": 12450,
        },
        {
            "airline": "Thai AirAsia X (XJ)",
            "origin": "DMK",
            "depart": "2026-12-01",
            "return": "2026-12-08",
            "total_days": 8,
            "net_days": 6,
            "price": 13200,
        },
        {
            "airline": "Thai Airways (TG)",
            "origin": "BKK",
            "depart": "2026-11-24",
            "return": "2026-11-30",
            "total_days": 7,
            "net_days": 5,
            "price": 21800,
        },
    ]


def build_flex_bubble(deals: List[Dict[str, Any]]) -> Dict[str, Any]:
    now_bkk = (datetime.utcnow() + timedelta(hours=7)).strftime(
        "%d/%m/%Y %H:%M"
    )

    contents = [
        {
            "type": "text",
            "text": "✈️ NGO DIRECT FLIGHT DEALS",
            "weight": "bold",
            "size": "md",
            "color": "#1DB446",
        },
        {
            "type": "text",
            "text": f"BKK/DMK ➔ NGO | อัปเดต {now_bkk}",
            "size": "xs",
            "color": "#888888",
            "margin": "xs",
        },
        {"type": "separator", "margin": "md"},
    ]

    for d in deals[:5]:
        contents.append(
            {
                "type": "box",
                "layout": "vertical",
                "margin": "md",
                "spacing": "xs",
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
                                "size": "xs",
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
                        "type": "text",
                        "text": f"⏳ รวม {d['total_days']} วัน (เที่ยวจริง ~{d['net_days']} วัน) | {d['origin']} ➔ NGO",
                        "size": "xxs",
                        "color": "#777777",
                    },
                    {"type": "separator", "margin": "sm"},
                ],
            }
        )

    return {
        "type": "flex",
        "altText": "อัปเดตราคาตั๋วบินตรงไปนาโกย่า (NGO)",
        "contents": {
            "type": "bubble",
            "body": {
                "type": "box",
                "layout": "vertical",
                "contents": contents,
            },
        },
    }


def send_line_push(flex_message: Dict[str, Any]) -> None:
    if not LINE_TOKEN or not LINE_USER_ID:
        raise ValueError("Missing LINE_CHANNEL_ACCESS_TOKEN or LINE_USER_ID")

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_TOKEN}",
    }
    payload = {"to": LINE_USER_ID, "messages": [flex_message]}

    res = requests.post(
        LINE_PUSH_URL, headers=headers, json=payload, timeout=10
    )
    res.raise_for_status()


if __name__ == "__main__":
    deals = fetch_best_deals()
    deals_sorted = sorted(deals, key=lambda x: x["price"])
    message = build_flex_bubble(deals_sorted)
    send_line_push(message)
