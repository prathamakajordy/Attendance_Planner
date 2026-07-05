import React, { useState } from 'react';
import { FiUploadCloud, FiFileText } from 'react-icons/fi';
import { importAPI } from '../../api/client';
import ReviewCorrectionTable from '../../components/forms/ReviewCorrectionTable';

const ImportWizard = ({ semesterId, onComplete, onCancel }) => {
  const [file, setFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [error, setError] = useState('');
  const [sessionData, setSessionData] = useState(null); // stores the ImportSessionResponse

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      setFile(e.target.files[0]);
      setError('');
    }
  };

  const handleUpload = async () => {
    if (!file) return;
    setIsUploading(true);
    setError('');
    try {
      const response = await importAPI.uploadTimetable(semesterId, file);
      setSessionData(response.data);
    } catch (err) {
      if (err.response?.status === 501 && err.response?.data?.detail === "OCR_UNAVAILABLE") {
        setError("Image OCR is currently disabled on this server. Please upload a PDF or use Manual Entry.");
      } else {
        setError(err.response?.data?.detail || "Upload failed. Please ensure it is a valid document.");
      }
    } finally {
      setIsUploading(false);
    }
  };

  const handleConfirm = async (finalPayload) => {
    try {
      if (semesterId === 'wizard') {
        await importAPI.deleteSession(sessionData.id);
        onComplete(finalPayload);
      } else {
        await importAPI.confirmSession(sessionData.id, finalPayload);
        onComplete(finalPayload);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Failed to save timetable.");
    }
  };

  const handleCancelSession = async () => {
    try {
      if (sessionData) {
        await importAPI.deleteSession(sessionData.id);
      }
    } catch (err) {
      console.error(err);
    }
    setSessionData(null);
    setFile(null);
    onCancel();
  };

  if (sessionData) {
    const payload = sessionData.extracted_payload || [];
    const numSlots = payload.length;
    const uniqueSubjects = new Set(payload.map(s => s.subject_name.trim().toLowerCase()).filter(Boolean)).size;
    
    const weekdaysMap = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"];
    const uniqueDaysInts = [...new Set(payload.map(s => s.weekday))].sort((a,b) => a-b);
    const coveredWeekdays = uniqueDaysInts.map(d => weekdaysMap[d]).join(", ") || "None";
    
    const avgConfidence = payload.length > 0 
      ? (payload.reduce((acc, curr) => acc + curr.confidence, 0) / payload.length * 100).toFixed(0) + "%"
      : "N/A";

    return (
      <div className="space-y-6 animate-fade-in">
        <div className="text-center space-y-2">
          <h2 className="text-2xl font-bold text-white">Review Extraction</h2>
          <p className="text-gray-400">
            Please review the extracted slots below. <br />
            <span className="inline-block w-3 h-3 rounded-full bg-green-500 mr-1"></span> High confidence
            <span className="inline-block w-3 h-3 rounded-full bg-yellow-500 ml-4 mr-1"></span> Review Recommended
            <span className="inline-block w-3 h-3 rounded-full bg-red-500 ml-4 mr-1"></span> Review Required
          </p>
        </div>

        {/* Import Summary Card */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 bg-gray-800/50 p-4 rounded-2xl border border-gray-700/50">
          <div className="text-center">
            <div className="text-2xl font-semibold text-white">{numSlots}</div>
            <div className="text-xs text-gray-400 uppercase tracking-wider mt-1">Slots</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-semibold text-white">{uniqueSubjects}</div>
            <div className="text-xs text-gray-400 uppercase tracking-wider mt-1">Subjects</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-semibold text-white">{avgConfidence}</div>
            <div className="text-xs text-gray-400 uppercase tracking-wider mt-1">Confidence</div>
          </div>
          <div className="text-center flex flex-col justify-center">
            <div className="text-sm font-medium text-white truncate px-2" title={coveredWeekdays}>{coveredWeekdays}</div>
            <div className="text-xs text-gray-400 uppercase tracking-wider mt-1">Days</div>
          </div>
        </div>

        {error && <div className="p-4 bg-red-500/10 text-red-400 rounded-xl">{error}</div>}
        
        <ReviewCorrectionTable 
          initialPayload={sessionData.extracted_payload}
          onConfirm={handleConfirm}
          onCancel={handleCancelSession}
        />
      </div>
    );
  }

  return (
    <div className="max-w-xl mx-auto space-y-8 animate-fade-in">
      <div className="text-center space-y-2">
        <h2 className="text-2xl font-bold text-white">Smart Import</h2>
        <p className="text-gray-400">Upload your timetable document to extract slots automatically.</p>
      </div>

      <div 
        className={`relative border-2 border-dashed rounded-3xl p-12 text-center transition-all ${
          file ? 'border-brand-500 bg-brand-500/5' : 'border-gray-700 hover:border-gray-600 bg-gray-800/50'
        }`}
      >
        <input 
          type="file" 
          accept="application/pdf,image/png,image/jpeg,image/jpg,image/webp"
          onChange={handleFileChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        
        <div className="flex flex-col items-center justify-center space-y-4">
          <div className={`p-4 rounded-full ${file ? 'bg-brand-500/20 text-brand-400' : 'bg-gray-800 text-gray-400'}`}>
            {file ? <FiFileText size={32} /> : <FiUploadCloud size={32} />}
          </div>
          <div>
            <p className="text-lg font-medium text-white">
              {file ? file.name : "Click or drag document here"}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              {file ? `${(file.size / 1024 / 1024).toFixed(2)} MB` : "PDF, PNG, JPG, WEBP (max 5MB)"}
            </p>
          </div>
        </div>
      </div>

      {error && (
        <div className="p-4 bg-red-500/10 text-red-400 text-sm rounded-xl text-center">
          {error}
        </div>
      )}

      <div className="flex gap-4">
        <button
          onClick={onCancel}
          className="flex-1 py-3.5 text-sm font-semibold text-gray-300 bg-gray-800 hover:bg-gray-700 rounded-xl transition-all"
        >
          Back to Manual
        </button>
        <button
          onClick={handleUpload}
          disabled={!file || isUploading}
          className="flex-1 py-3.5 text-sm font-semibold text-white bg-brand-600 hover:bg-brand-500 disabled:opacity-50 disabled:cursor-not-allowed rounded-xl shadow-lg shadow-brand-500/25 transition-all"
        >
          {isUploading ? "Extracting..." : "Extract Timetable"}
        </button>
      </div>
    </div>
  );
};

export default ImportWizard;
