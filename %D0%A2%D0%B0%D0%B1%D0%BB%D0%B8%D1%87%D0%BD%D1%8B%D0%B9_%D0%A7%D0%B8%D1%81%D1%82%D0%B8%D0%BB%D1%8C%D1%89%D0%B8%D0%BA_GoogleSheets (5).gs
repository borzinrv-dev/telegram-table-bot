/**
 * ═══════════════════════════════════════════════════════════════
 *            🧹 СКРИПТ: УМНЫЙ ЧИСТИЛЬЩИК ТАБЛИЦ (Google Apps Script)
 * ═══════════════════════════════════════════════════════════════
 * 
 * ИНСТРУКЦИЯ ПО УСТАНОВКЕ:
 * 1. Откройте вашу Google Таблицу.
 * 2. В верхнем меню выберите: «Расширения» -> «Apps Script».
 * 3. Удалите всё, что там написано, и вставьте этот код.
 * 4. Нажмите иконку дискеты (Сохранить) и обновите вкладку с таблицей (F5).
 * 5. В верхнем меню появится новый пункт «🧹 Умный Чистильщик»!
 * ═══════════════════════════════════════════════════════════════
 */

// Создание пользовательского меню при открытии таблицы
function onOpen() {
  const ui = SpreadsheetApp.getUi();
  ui.createMenu('🧹 Умный Чистильщик')
    .addItem('⚡ Полная экспресс-очистка (Все действия)', 'fullCleanSheet')
    .addSeparator()
    .addItem('✂️ Удалить лишние пробелы (Trim)', 'trimAllSpaces')
    .addItem('👥 Удалить полные дубликаты строк', 'removeDuplicateRows')
    .addItem('🗑️ Удалить пустые строки', 'deleteEmptyRows')
    .addSeparator()
    .addItem('📱 Привести телефоны к стандарту +7', 'formatPhoneNumbers')
    .addItem('📧 Очистить Email (нижний регистр)', 'cleanEmails')
    .addItem('👤 Очистить ФИО (Каждое Слово С Заглавной)', 'capitalizeNames')
    .addSeparator()
    .addItem('⚠️ Подсветить строки с ошибками (#N/A, #REF)', 'highlightErrors')
    .addToUi();
}

/**
 * 1. ПОЛНАЯ ЭКСПРЕСС-ОЧИСТКА В 1 КЛИК
 */
function fullCleanSheet() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const range = sheet.getDataRange();
  const values = range.getValues();
  
  if (values.length <= 1) {
    SpreadsheetApp.getUi().alert('Таблица пуста или содержит только заголовок.');
    return;
  }

  // Обрезка пробелов во всей таблице
  for (let r = 0; r < values.length; r++) {
    for (let c = 0; c < values[r].length; c++) {
      if (typeof values[r][c] === 'string') {
        values[r][c] = values[r][c].trim().replace(/\s+/g, ' ');
      }
    }
  }
  range.setValues(values);

  // Удаление дубликатов и пустых строк
  deleteEmptyRows();
  removeDuplicateRows();

  SpreadsheetApp.getActiveSpreadsheet().toast('✅ Полная экспресс-очистка успешно завершена!', 'Готово', 4);
}

/**
 * 2. УДАЛЕНИЕ ЛИШНИХ ПРОБЕЛОВ
 */
function trimAllSpaces() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const range = sheet.getDataRange();
  const values = range.getValues();
  let count = 0;

  for (let r = 0; r < values.length; r++) {
    for (let c = 0; c < values[r].length; c++) {
      if (typeof values[r][c] === 'string') {
        const cleaned = values[r][c].trim().replace(/\s+/g, ' ');
        if (cleaned !== values[r][c]) {
          values[r][c] = cleaned;
          count++;
        }
      }
    }
  }
  range.setValues(values);
  SpreadsheetApp.getActiveSpreadsheet().toast(`Очищено ячеек с пробелами: ${count}`, 'Успешно', 3);
}

/**
 * 3. УДАЛЕНИЕ ПУСТЫХ СТРОК
 */
function deleteEmptyRows() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const values = sheet.getDataRange().getValues();
  let deletedCount = 0;

  // Идем снизу вверх, чтобы не сбивать индексы строк
  for (let r = values.length - 1; r >= 1; r--) {
    const isRowEmpty = values[r].every(cell => cell === '' || cell === null || cell === undefined);
    if (isRowEmpty) {
      sheet.deleteRow(r + 1);
      deletedCount++;
    }
  }
  SpreadsheetApp.getActiveSpreadsheet().toast(`Удалено пустых строк: ${deletedCount}`, 'Очистка', 3);
}

/**
 * 4. УДАЛЕНИЕ ДУБЛИКАТОВ
 */
function removeDuplicateRows() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const data = sheet.getDataRange().getValues();
  if (data.length <= 1) return;

  const uniqueRows = new Set();
  let deletedCount = 0;

  for (let r = data.length - 1; r >= 1; r--) {
    const rowString = JSON.stringify(data[r]);
    if (uniqueRows.has(rowString)) {
      sheet.deleteRow(r + 1);
      deletedCount++;
    } else {
      uniqueRows.add(rowString);
    }
  }
  SpreadsheetApp.getActiveSpreadsheet().toast(`Удалено строк-дубликатов: ${deletedCount}`, 'Дубликаты', 3);
}

/**
 * 5. ФОРМАТИРОВАНИЕ ТЕЛЕФОННЫХ НОМЕРОВ В +7 (XXX) XXX-XX-XX
 */
function formatPhoneNumbers() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const range = sheet.getActiveRange() || sheet.getDataRange();
  const values = range.getValues();
  let updated = 0;

  for (let r = 0; r < values.length; r++) {
    for (let c = 0; c < values[r].length; c++) {
      const val = String(values[r][c]).replace(/[^\d+]/g, '');
      const digits = val.replace(/\D/g, '');
      
      // Если это российский номер из 11 цифр (начинается с 7 или 8) или 10 цифр
      if (digits.length === 11 && (digits.startsWith('7') || digits.startsWith('8'))) {
        const d = digits.slice(1);
        values[r][c] = `+7 (${d.slice(0,3)}) ${d.slice(3,6)}-${d.slice(6,8)}-${d.slice(8,10)}`;
        updated++;
      } else if (digits.length === 10) {
        values[r][c] = `+7 (${digits.slice(0,3)}) ${digits.slice(3,6)}-${digits.slice(6,8)}-${digits.slice(8,10)}`;
        updated++;
      }
    }
  }
  range.setValues(values);
  SpreadsheetApp.getActiveSpreadsheet().toast(`Нормализовано номеров: ${updated}`, 'Телефоны', 3);
}

/**
 * 6. ОЧИСТКА И НОРМАЛИЗАЦИЯ EMAIL
 */
function cleanEmails() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const range = sheet.getDataRange();
  const values = range.getValues();
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  let updated = 0;

  for (let r = 0; r < values.length; r++) {
    for (let c = 0; c < values[r].length; c++) {
      const str = String(values[r][c]).trim().toLowerCase();
      if (emailRegex.test(str)) {
        if (values[r][c] !== str) {
          values[r][c] = str;
          updated++;
        }
      }
    }
  }
  range.setValues(values);
  SpreadsheetApp.getActiveSpreadsheet().toast(`Очищено email-адресов: ${updated}`, 'Email', 3);
}

/**
 * 7. ПРИВЕДЕНИЕ ФИО К СТАНДАРТУ (С Заглавной Буквы)
 */
function capitalizeNames() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const range = sheet.getActiveRange() || sheet.getDataRange();
  const values = range.getValues();

  for (let r = 0; r < values.length; r++) {
    for (let c = 0; c < values[r].length; c++) {
      if (typeof values[r][c] === 'string' && values[r][c].length > 0) {
        values[r][c] = values[r][c].toLowerCase().replace(/(?:^|\s|-)\S/g, function(letter) {
          return letter.toUpperCase();
        });
      }
    }
  }
  range.setValues(values);
  SpreadsheetApp.getActiveSpreadsheet().toast('ФИО успешно отформатированы', 'ФИО', 3);
}

/**
 * 8. ПОДСВЕТКА СТРОК С ОШИБКАМИ
 */
function highlightErrors() {
  const sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  const range = sheet.getDataRange();
  const values = range.getValues();
  let errorCount = 0;

  for (let r = 0; r < values.length; r++) {
    for (let c = 0; c < values[r].length; c++) {
      const val = String(values[r][c]);
      if (val.startsWith('#') || val === '#N/A' || val === '#VALUE!' || val === '#REF!' || val === '#DIV/0!') {
        sheet.getRange(r + 1, c + 1).setBackground('#F8D7DA'); // Мягкий красный цвет
        errorCount++;
      }
    }
  }
  SpreadsheetApp.getActiveSpreadsheet().toast(`Найдено и подсвечено ошибок: ${errorCount}`, 'Ошибки', 3);
}
