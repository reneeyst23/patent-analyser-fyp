import { useState } from 'react';
import { Upload } from 'lucide-react';

export default function UploadSection() {
  const [isDragging, setIsDragging] = useState(false);

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    // Handle file upload logic here
  };

  return (
    <div
      onDragOver={handleDragOver}
      onDragLeave={handleDragLeave}
      onDrop={handleDrop}
      className={`mt-12 p-12 border-2 border-dashed rounded-lg text-center transition-colors duration-200 max-w-4xl mx-auto
                ${isDragging ? 'border-emerald-500 bg-emerald-50' : 'border-gray-300 hover:border-emerald-400'}`}
    >
      <Upload className="mx-auto h-16 w-16 text-gray-400" />
      <h3 className="mt-4 text-xl font-medium text-gray-900">Upload Patent Documents</h3>
      <p className="mt-2 text-lg text-gray-500">
        Drag and drop your files here, or{' '}
        <button className="text-emerald-600 hover:text-emerald-500 font-medium">
          browse
        </button>
      </p>
      <p className="mt-3 text-sm text-gray-500">PDF, DOC up to 10MB</p>
    </div>
  );
}