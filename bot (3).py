#!/usr/bin/env python3
import telebot
from telebot import types
import os
import sys

TOKEN = os.environ.get("TOKEN", "8870157388:AAHCLx2bA1FwvNaqsXHnPQ-OUxLTx0TwTu4")
PHONE = os.environ.get("PHONE", "+79337388939")
CARDS = {"Сбер": "2202208565750040", "Т-банк": "2200396117681599"}
PRICE = 399
ADMIN_CHAT_ID = int(os.environ.get("ADMIN_ID", "454371759"))

# Инструкция и готовый код скрипта для покупателя
CLEANER_SCRIPT_TEXT = """/**
 * 🧹 УМНЫЙ ЧИСТИЛЬЩИК ТАБЛИЦ (Google Apps Script)
 * Добавляет меню в Google Таблицы: удаление дубликатов, пробелов, пустых строк,
 * нормализация телефонов (+7), очистка email и ФИО.
 */
function onOpen() {
  SpreadsheetApp.getUi().createMenu('🧹 Умный Чистильщик')
    .addItem('⚡ Полная экспресс-очистка', 'fullCleanSheet')
    .addSeparator()
    .addItem('✂️ Удалить лишние пробелы', 'trimAllSpaces')
    .addItem('👥 Удалить дубликаты строк', 'removeDuplicateRows')
    .addItem('🗑️ Удалить пустые строки', 'deleteEmptyRows')
    .addSeparator()
    .addItem('📱 Привести телефоны к +7', 'formatPhoneNumbers')
    .addItem('📧 Очистить Email', 'cleanEmails')
    .addItem('👤 Очистить ФИО', 'capitalizeNames')
    .addToUi();
}

function fullCleanSheet() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const range = sheet.getDataRange();
  const values = range.getValues();
  if (values.length <= 1) return;
  for (let r = 0; r < values.length; r++) {
    for (let c = 0; c < values[r].length; c++) {
      if (typeof values[r][c] === 'string') values[r][c] = values[r][c].trim().replace(/\\s+/g, ' ');
    }
  }
  range.setValues(values);
  deleteEmptyRows();
  removeDuplicateRows();
  SpreadsheetApp.getActiveSpreadsheet().toast('✅ Экспресс-очистка завершена!', 'Готово', 4);
}

function trimAllSpaces() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const range = sheet.getDataRange();
  const values = range.getValues();
  for (let r = 0; r < values.length; r++) {
    for (let c = 0; c < values[r].length; c++) {
      if (typeof values[r][c] === 'string') values[r][c] = values[r][c].trim().replace(/\\s+/g, ' ');
    }
  }
  range.setValues(values);
  SpreadsheetApp.getActiveSpreadsheet().toast('Пробелы очищены!', 'Успех', 3);
}

function deleteEmptyRows() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const values = sheet.getDataRange().getValues();
  for (let r = values.length - 1; r >= 1; r--) {
    if (values[r].every(c => c === '' || c === null || c === undefined)) sheet.deleteRow(r + 1);
  }
}

function removeDuplicateRows() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const data = sheet.getDataRange().getValues();
  const seen = new Set();
  for (let r = data.length - 1; r >= 1; r--) {
    const s = JSON.stringify(data[r]);
    if (seen.has(s)) sheet.deleteRow(r + 1);
    else seen.add(s);
  }
}

function formatPhoneNumbers() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const range = sheet.getDataRange();
  const values = range.getValues();
  for (let r = 0; r < values.length; r++) {
    for (let c = 0; c < values[r].length; c++) {
      const d = String(values[r][c]).replace(/\\D/g, '');
      if (d.length === 11 && (d.startsWith('7') || d.startsWith('8'))) {
        const sub = d.slice(1);
        values[r][c] = `+7 (${sub.slice(0,3)}) ${sub.slice(3,6)}-${sub.slice(6,8)}-${sub.slice(8,10)}`;
      } else if (d.length === 10) {
        values[r][c] = `+7 (${d.slice(0,3)}) ${d.slice(3,6)}-${d.slice(6,8)}-${d.slice(8,10)}`;
      }
    }
  }
  range.setValues(values);
}

function cleanEmails() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const range = sheet.getDataRange();
  const values = range.getValues();
  for (let r = 0; r < values.length; r++) {
    for (let c = 0; c < values[r].length; c++) {
      if (typeof values[r][c] === 'string' && values[r][c].includes('@')) {
        values[r][c] = values[r][c].trim().toLowerCase();
      }
    }
  }
  range.setValues(values);
}

function capitalizeNames() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const range = sheet.getDataRange();
  const values = range.getValues();
  for (let r = 0; r < values.length; r++) {
    for (let c = 0; c < values[r].length; c++) {
      if (typeof values[r][c] === 'string' && values[r][c].length > 0) {
        values[r][c] = values[r][c].toLowerCase().replace(/(?:^|\\s|-)\\S/g, l => l.toUpperCase());
      }
    }
  }
  range.setValues(values);
}
"""

user_data = {}
bot = telebot.TeleBot(TOKEN, threaded=False)

@bot.message_handler(commands=['start'])
def start(m):
    chat_id = m.chat.id
    user_data[chat_id] = {"step": "waiting_name"}
    bot.send_message(chat_id, "👋 Привет! Для оформления заказа введите ваше **ФИО**:", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.chat.id in user_data and user_data[m.chat.id].get("step") == "waiting_name")
def get_name(m):
    chat_id = m.chat.id
    user_data[chat_id]["name"] = m.text.strip()
    user_data[chat_id]["step"] = "waiting_email"
    bot.send_message(chat_id, "📧 Введите ваш **Email**:", parse_mode="Markdown")

@bot.message_handler(func=lambda m: m.chat.id in user_data and user_data[m.chat.id].get("step") == "waiting_email")
def get_email(m):
    chat_id = m.chat.id
    user_data[chat_id]["email"] = m.text.strip()
    user_data[chat_id]["step"] = "waiting_payment"
    
    mk = types.InlineKeyboardMarkup()
    mk.add(types.InlineKeyboardButton("✅ Я перевел 399 ₽", callback_data="paid"))
    
    text = (
        f"💳 **Реквизиты для оплаты:**\n\n"
        f"📱 СБП: `{PHONE}`\n"
        f"💳 Сбер: `{CARDS['Сбер']}`\n"
        f"💳 Т-банк: `{CARDS['Т-банк']}`\n\n"
        f"💰 **Сумма:** {PRICE} ₽\n\n"
        f"После перевода нажмите кнопку ниже:"
    )
    bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=mk)

@bot.callback_query_handler(func=lambda c: c.data == "paid")
def paid(c):
    chat_id = c.message.chat.id
    info = user_data.get(chat_id, {})
    name = info.get("name", "Покупатель")
    email = info.get("email", "Не указан")
    
    bot.answer_callback_query(c.id, "✅ Оплата принята!")
    
    # 1. Мгновенно отправляем продукт покупателю (без ожидания)
    success_text = (
        f"🎉 **Спасибо за покупку, {name}!**\n\n"
        f"Ваш заказ на скрипт **«Умный Чистильщик Таблиц»** успешно выполнен.\n\n"
        f"📌 **Инструкция по установке в Google Таблицу:**\n"
        f"1. Откройте нужную Google Таблицу.\n"
        f"2. В верхнем меню выберите **«Расширения» -> «Apps Script»**.\n"
        f"3. Сотрите всё и вставьте код ниже.\n"
        f"4. Нажмите **Сохранить** (иконка дискеты) и обновите таблицу (F5).\n"
        f"5. В меню таблицы появится пункт **«🧹 Умный Чистильщик»**!\n\n"
        f"👇 **Код скрипта (скопируйте в Apps Script):**"
    )
    bot.send_message(chat_id, success_text, parse_mode="Markdown")
    bot.send_message(chat_id, f"```javascript\n{CLEANER_SCRIPT_TEXT}\n```", parse_mode="Markdown")
    
    # 2. Уведомляем администратора (только для истории/логов)
    admin_log = (
        f"🔔 **Новая покупка (выдано автоматически)!**\n\n"
        f"👤 **Клиент:** {name}\n"
        f"📧 **Email:** {email}\n"
        f"💬 **Telegram ID:** `{chat_id}`\n"
        f"💰 **Сумма:** {PRICE} ₽"
    )
    try:
        bot.send_message(ADMIN_CHAT_ID, admin_log, parse_mode="Markdown")
    except Exception as e:
        print(f"Log sending error: {e}")
        
    if chat_id in user_data:
        del user_data[chat_id]

if __name__ == "__main__":
    try:
        print("BOT STARTED")
        bot.infinity_polling(timeout=10, long_polling_timeout=5, skip_pending=True)
    except Exception as e:
        print(f"ERROR: {e}")
        sys.exit(1)
