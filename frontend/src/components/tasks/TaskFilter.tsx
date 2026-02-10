'use client';

import React from 'react';
import { FilterType } from '@/types/components';

interface TaskFilterProps {
  activeFilter: FilterType;
  onChange: (filter: FilterType) => void;
}

export function TaskFilter({ activeFilter, onChange }: TaskFilterProps) {
  const filters: { value: FilterType; label: string }[] = [
    { value: 'all', label: 'All' },
    { value: 'pending', label: 'Pending' },
    { value: 'completed', label: 'Completed' },
  ];

  return (
    <div className="flex gap-2">
      {filters.map((filter) => (
        <button
          key={filter.value}
          onClick={() => onChange(filter.value)}
          className={`px-4 py-2 rounded-lg font-medium transition-colors ${
            activeFilter === filter.value
              ? 'bg-blue-600 text-white'
              : 'bg-blue-100 text-blue-700 hover:bg-blue-200'
          }`}
        >
          {filter.label}
        </button>
      ))}
    </div>
  );
}
