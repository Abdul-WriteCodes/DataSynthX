"use client";
import { useCallback, useState } from "react";
import { Upload, FileSpreadsheet, X } from "lucide-react";
import clsx from "clsx";

interface Props {
  onFileSelected: (file: File) => void;
  selectedFile: File | null;
  onClear: () => void;
}

export default function UploadBox({ onFileSelected, selectedFile, onClear }: Props) {
  const [dragging, setDragging] = useState(false);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const file = e.dataTransfer.files[0];
    if (file) onFileSelected(file);
  }, [onFileSelected]);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) onFileSelected(file);
  };

  if (selectedFile) {
    return (
      <div className="border border-emerald-200 bg-emerald-50 rounded-xl p-4 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <FileSpreadsheet size={20} className="text-emerald-600" />
          <div>
            <p className="text-sm font-medium text-slate-700">{selectedFile.name}</p>
            <p className="text-xs text-slate-500">
              {(selectedFile.size / 1024).toFixed(1)} KB
            </p>
          </div>
        </div>
        <button onClick={onClear} className="text-slate-400 hover:text-red-500 transition-colors">
          <X size={18} />
        </button>
      </div>
    );
  }

  return (
    <label
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      className={clsx(
        "border-2 border-dashed rounded-xl p-10 flex flex-col items-center gap-3 cursor-pointer transition-colors",
        dragging ? "border-brand-500 bg-brand-50" : "border-slate-200 hover:border-brand-300"
      )}
    >
      <Upload size={28} className={dragging ? "text-brand-500" : "text-slate-400"} />
      <div className="text-center">
        <p className="text-sm font-medium text-slate-700">Drop your dataset here</p>
        <p className="text-xs text-slate-400 mt-1">or click to browse — CSV or Excel, max 20 MB</p>
      </div>
      <input type="file" accept=".csv,.xlsx,.xls" onChange={handleChange} className="hidden" />
    </label>
  );
}
