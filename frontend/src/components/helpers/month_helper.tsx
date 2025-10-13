'use client';

import React from 'react';

interface MonthDropdownProps {
  currentMonth: Date;
  onChange: (monthIndex: number) => void;
}

export default function MonthDropdown({ currentMonth, onChange }: MonthDropdownProps) {
  const months = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
  ];

  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const monthIndex = months.indexOf(e.target.value);
    onChange(monthIndex);
  };

  return (
    <select
      value={months[currentMonth.getMonth()]}
      onChange={handleChange}
      className="bg-[var(--color-bg)] text-[var(--color-text-primary)] text-sm px-3 py-1 rounded border border-[var(--color-card)]"
    >
      {months.map((month) => (
        <option key={month} value={month}>
          {month}
        </option>
      ))}
    </select>
  );
}
