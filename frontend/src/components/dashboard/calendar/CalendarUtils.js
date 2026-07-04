/**
 * Utility functions for generating calendar grid data.
 */

// Generate a grid of days (weeks * 7) for a given month/year
// Each cell will have: date (YYYY-MM-DD), isPadding, isCurrentMonth
export function generateMonthGrid(year, month) {
  // Month is 0-indexed in JS Date (0 = Jan, 11 = Dec)
  const firstDayOfMonth = new Date(year, month, 1);
  const lastDayOfMonth = new Date(year, month + 1, 0);

  const startDayOfWeek = firstDayOfMonth.getDay(); // 0 = Sunday, 6 = Saturday
  const totalDaysInMonth = lastDayOfMonth.getDate();

  // We usually display 6 rows (42 days) to guarantee any month fits cleanly
  const grid = [];

  // Previous month padding
  const prevMonthLastDay = new Date(year, month, 0).getDate();
  for (let i = startDayOfWeek - 1; i >= 0; i--) {
    const d = prevMonthLastDay - i;
    const dateObj = new Date(year, month - 1, d);
    grid.push({
      dateStr: formatDateStr(dateObj),
      dateObj,
      isPadding: true,
      isCurrentMonth: false,
    });
  }

  // Current month days
  for (let d = 1; d <= totalDaysInMonth; d++) {
    const dateObj = new Date(year, month, d);
    grid.push({
      dateStr: formatDateStr(dateObj),
      dateObj,
      isPadding: false,
      isCurrentMonth: true,
    });
  }

  // Next month padding to fill exactly 42 cells
  const remaining = 42 - grid.length;
  for (let d = 1; d <= remaining; d++) {
    const dateObj = new Date(year, month + 1, d);
    grid.push({
      dateStr: formatDateStr(dateObj),
      dateObj,
      isPadding: true,
      isCurrentMonth: false,
    });
  }

  return grid;
}

// Convert JS Date to YYYY-MM-DD string handling local timezone properly
export function formatDateStr(dateObj) {
  const y = dateObj.getFullYear();
  const m = String(dateObj.getMonth() + 1).padStart(2, '0');
  const d = String(dateObj.getDate()).padStart(2, '0');
  return `${y}-${m}-${d}`;
}
