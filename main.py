#!/usr/bin/env python3
"""
Almaviva Egypt - Visa Appointment Checker Bot
بوت مراقبة مواعيد التأشيرة الإيطالية
"""

import requests
import time
import logging
from datetime import datetime

# ==================== الإعدادات ====================
TELEGRAM_TOKEN = "8772964692:AAFZ_0a-4CadXiUA7vivvETppSLyqMuU3zA"
CHAT_ID = "724260577"
CHECK_INTERVAL = 60  # فحص كل 60 ثانية

# رابط صفحة الحجز
ALMAVIVA_URL = "https://egy.almaviva-visa.it/appointments"

# ==================== إعداد اللوج ====================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def send_telegram_message(message: str) -> bool:
    """إرسال رسالة على تيليجرام"""
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "HTML"
    }
    try:
        response = requests.post(url, json=payload, timeout=10)
        return response.status_code == 200
    except Exception as e:
        logger.error(f"خطأ في إرسال الرسالة: {e}")
        return False


def check_appointments() -> bool:
    """فحص الموقع للمواعيد المتاحة"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept-Language": "ar,en;q=0.9",
    }
    try:
        response = requests.get(ALMAVIVA_URL, headers=headers, timeout=15)
        page_content = response.text.lower()

        # كلمات تدل على وجود مواعيد
        available_keywords = [
            "available", "متاح", "book now", "احجز", 
            "appointment available", "select date"
        ]

        # كلمات تدل على عدم وجود مواعيد
        unavailable_keywords = [
            "no appointment", "no available", "لا يوجد",
            "not available", "fully booked", "محجوز"
        ]

        # فحص الكلمات
        for keyword in unavailable_keywords:
            if keyword in page_content:
                logger.info(f"لا توجد مواعيد متاحة حالياً")
                return False

        for keyword in available_keywords:
            if keyword in page_content:
                return True

        # لو مش لاقي حاجة واضحة
        logger.info("الصفحة اتحملت — مش واضح في المواعيد")
        return False

    except requests.exceptions.ConnectionError:
        logger.warning("مش قادر يوصل للموقع")
        return False
    except Exception as e:
        logger.error(f"خطأ غير متوقع: {e}")
        return False


def main():
    """الدالة الرئيسية"""
    logger.info("=" * 50)
    logger.info("🤖 بوت مراقبة مواعيد Almaviva شغال!")
    logger.info(f"⏱️ هيفحص كل {CHECK_INTERVAL} ثانية")
    logger.info("=" * 50)

    # رسالة ترحيب
    send_telegram_message(
        "🤖 <b>بوت مراقبة مواعيد Almaviva</b>\n\n"
        "✅ البوت شغال دلوقتي!\n"
        f"⏱️ بيفحص كل {CHECK_INTERVAL} ثانية\n"
        "🔔 هيبعتلك نوتيفيكيشن فور ما يلاقي ميعاد متاح\n\n"
        f"🕐 بدأ: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )

    last_status = None
    check_count = 0

    while True:
        try:
            check_count += 1
            logger.info(f"فحص رقم {check_count}...")

            available = check_appointments()

            # لو الحالة اتغيرت
            if available != last_status:
                if available:
                    # 🎉 في مواعيد!
                    message = (
                        "🎉 <b>في مواعيد متاحة دلوقتي!</b>\n\n"
                        "⚡ احجز بسرعة قبل ما تخلص!\n\n"
                        "🔗 <a href='https://egy.almaviva-visa.it/appointments'>اضغط هنا للحجز</a>\n\n"
                        f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    )
                    send_telegram_message(message)
                    logger.info("✅ تم إرسال إشعار — في مواعيد!")
                else:
                    if last_status is not None:  # مش أول فحص
                        send_telegram_message(
                            "😔 <b>خلصت المواعيد مرة تانية</b>\n"
                            "هفضل أراقب وأبعتلك لما تيجي تاني 👀"
                        )

            last_status = available

            # كل 10 فحصات بعت تقرير
            if check_count % 10 == 0:
                status_emoji = "✅" if available else "❌"
                send_telegram_message(
                    f"📊 <b>تقرير دوري</b>\n\n"
                    f"🔢 عدد الفحصات: {check_count}\n"
                    f"{status_emoji} الحالة: {'في مواعيد!' if available else 'لا توجد مواعيد'}\n"
                    f"🕐 {datetime.now().strftime('%H:%M:%S')}"
                )

            time.sleep(CHECK_INTERVAL)

        except KeyboardInterrupt:
            logger.info("تم إيقاف البوت")
            send_telegram_message("⛔ البوت اتوقف.")
            break
        except Exception as e:
            logger.error(f"خطأ: {e}")
            time.sleep(30)


if __name__ == "__main__":
    main()
