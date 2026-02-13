'use client';

import React, { useState } from 'react';
import { Task } from '@/types/components';
import { Checkbox } from '../ui/Checkbox';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';

interface TaskItemProps {
  task: Task;
  onToggle: (taskId: string, completed: boolean) => void;
  onDelete: (taskId: string) => void;
  onEdit: (taskId: string, title: string, description: string | null) => void;
}

export function TaskItem({ task, onToggle, onDelete, onEdit }: TaskItemProps) {
  const [isEditing, setIsEditing] = useState(false);
  const [editTitle, setEditTitle] = useState(task.title);
  const [editDescription, setEditDescription] = useState(task.description || '');

  const handleSave = () => {
    if (editTitle.trim()) {
      onEdit(task.id, editTitle.trim(), editDescription.trim() || null);
      setIsEditing(false);
    }
  };

  const handleCancel = () => {
    setEditTitle(task.title);
    setEditDescription(task.description || '');
    setIsEditing(false);
  };

  const handleDeleteClick = () => {
    if (confirm('Are you sure you want to delete this task?')) {
      onDelete(task.id);
    }
  };

  if (isEditing) {
    return (
      <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm space-y-3">
        <Input
          value={editTitle}
          onChange={(e) => setEditTitle(e.target.value)}
          placeholder="Task title"
        />
        <Input
          value={editDescription}
          onChange={(e) => setEditDescription(e.target.value)}
          placeholder="Description (optional)"
        />
        <div className="flex gap-2">
          <Button onClick={handleSave} variant="primary" className="text-sm">
            Save
          </Button>
          <Button onClick={handleCancel} variant="secondary" className="text-sm">
            Cancel
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 bg-white border border-gray-200 rounded-lg shadow-sm hover:shadow-md transition-shadow">
      <div className="flex items-start gap-3">
        <Checkbox
          checked={task.completed}
          onChange={(checked) => onToggle(task.id, checked)}
        />
        <div className="flex-1 min-w-0">
          <h3
            className={`text-lg font-medium ${
              task.completed ? 'line-through text-gray-400' : 'text-gray-900'
            }`}
          >
            {task.title}
          </h3>
          {task.description && (
            <p
              className={`mt-1 text-sm ${
                task.completed ? 'text-gray-400' : 'text-gray-600'
              }`}
            >
              {task.description}
            </p>
          )}
        </div>
        <div className="flex gap-2">
          <Button
            onClick={() => setIsEditing(true)}
            variant="secondary"
            className="text-sm px-3 py-1"
          >
            Edit
          </Button>
          <Button
            onClick={handleDeleteClick}
            variant="danger"
            className="text-sm px-3 py-1"
          >
            Delete
          </Button>
        </div>
      </div>
    </div>
  );
}
