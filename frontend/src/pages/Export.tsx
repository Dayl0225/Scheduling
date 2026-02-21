import React from 'react';

const Export: React.FC = () => {
  const handleExport = () => {
    // Trigger download
    window.open('http://localhost:8001/api/export/1', '_blank');
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Export Schedule</h1>
      
      <div className="bg-white p-6 rounded shadow-md">
        <p className="mb-4">Export the generated schedule to Excel with color coding.</p>
        <button 
          onClick={handleExport} 
          className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600"
        >
          Download Excel
        </button>
      </div>
    </div>
  );
};

export default Export;