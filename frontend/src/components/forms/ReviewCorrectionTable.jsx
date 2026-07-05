import React, { useState } from 'react';
import { FiTrash2, FiPlus, FiAlertTriangle, FiCheckCircle } from 'react-icons/fi';

const ReviewCorrectionTable = ({ initialPayload, onConfirm, onCancel }) => {
  const [rows, setRows] = useState(initialPayload || []);

  const handleRowChange = (index, field, value) => {
    const newRows = [...rows];
    newRows[index][field] = value;
    setRows(newRows);
  };

  const handleDelete = (index) => {
    const newRows = [...rows];
    newRows.splice(index, 1);
    setRows(newRows);
  };

  const handleAdd = () => {
    setRows([
      ...rows,
      {
        weekday: 0,
        start_time: '09:00',
        end_time: '10:00',
        subject_name: '',
        confidence: 1.0, // Human entered
      }
    ]);
  };

  const getRowClass = (confidence) => {
    if (confidence >= 0.8) return 'bg-green-50/10 border-green-200/20';
    if (confidence >= 0.5) return 'bg-yellow-50/10 border-yellow-200/20';
    return 'bg-red-50/10 border-red-200/20';
  };

  const getConfidenceIcon = (confidence) => {
    if (confidence >= 0.8) return <FiCheckCircle className="text-green-500" />;
    if (confidence >= 0.5) return <FiAlertTriangle className="text-yellow-500" title="Review Recommended" />;
    return <FiAlertTriangle className="text-red-500" title="Review Required" />;
  };

  const weekdays = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];

  return (
    <div className="space-y-4">
      <div className="bg-gray-800 rounded-xl overflow-hidden border border-gray-700">
        <table className="w-full text-left text-sm">
          <thead className="bg-gray-900 text-gray-400">
            <tr>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Weekday</th>
              <th className="px-4 py-3 font-medium">Start Time</th>
              <th className="px-4 py-3 font-medium">End Time</th>
              <th className="px-4 py-3 font-medium">Subject</th>
              <th className="px-4 py-3 font-medium text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-700/50">
            {rows.map((row, idx) => (
              <tr key={idx} className={`transition-colors ${getRowClass(row.confidence)}`}>
                <td className="px-4 py-3 text-center w-12">
                  {getConfidenceIcon(row.confidence)}
                </td>
                <td className="px-4 py-3">
                  <select
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-2 py-1.5 text-white outline-none focus:border-brand-500"
                    value={row.weekday}
                    onChange={(e) => handleRowChange(idx, 'weekday', parseInt(e.target.value))}
                  >
                    {weekdays.map((d, i) => (
                      <option key={i} value={i}>{d}</option>
                    ))}
                  </select>
                </td>
                <td className="px-4 py-3">
                  <input
                    type="time"
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-2 py-1.5 text-white outline-none focus:border-brand-500"
                    value={row.start_time.substring(0, 5)}
                    onChange={(e) => handleRowChange(idx, 'start_time', e.target.value + ":00")}
                  />
                </td>
                <td className="px-4 py-3">
                  <input
                    type="time"
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-2 py-1.5 text-white outline-none focus:border-brand-500"
                    value={row.end_time.substring(0, 5)}
                    onChange={(e) => handleRowChange(idx, 'end_time', e.target.value + ":00")}
                  />
                </td>
                <td className="px-4 py-3">
                  <input
                    type="text"
                    className="w-full bg-gray-900 border border-gray-700 rounded-lg px-3 py-1.5 text-white outline-none focus:border-brand-500"
                    value={row.subject_name}
                    onChange={(e) => handleRowChange(idx, 'subject_name', e.target.value)}
                    placeholder="Subject Name"
                  />
                </td>
                <td className="px-4 py-3 text-right">
                  <button
                    onClick={() => handleDelete(idx)}
                    className="p-1.5 text-gray-400 hover:text-red-400 hover:bg-red-400/10 rounded-lg transition-colors"
                    title="Delete row"
                  >
                    <FiTrash2 size={16} />
                  </button>
                </td>
              </tr>
            ))}
            {rows.length === 0 && (
              <tr>
                <td colSpan="6" className="px-4 py-8 text-center text-gray-500">
                  No data found. You can add rows manually.
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      <div className="flex items-center justify-between">
        <button
          onClick={handleAdd}
          className="flex items-center gap-2 px-4 py-2 text-sm font-medium text-brand-400 bg-brand-500/10 hover:bg-brand-500/20 rounded-xl transition-colors"
        >
          <FiPlus size={16} /> Add Row
        </button>

        <div className="flex gap-3">
          <button
            onClick={onCancel}
            className="px-6 py-2.5 text-sm font-medium text-gray-300 hover:text-white bg-gray-800 hover:bg-gray-700 rounded-xl transition-all"
          >
            Cancel
          </button>
          <button
            onClick={() => onConfirm(rows)}
            className="px-6 py-2.5 text-sm font-medium text-white bg-brand-600 hover:bg-brand-500 rounded-xl shadow-lg shadow-brand-500/20 transition-all"
          >
            Confirm & Save
          </button>
        </div>
      </div>
    </div>
  );
};

export default ReviewCorrectionTable;
