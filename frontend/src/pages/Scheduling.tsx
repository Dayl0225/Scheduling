import React, { useState } from 'react';

const Scheduling: React.FC = () => {
  const [confirmText, setConfirmText] = useState('');
  const [showReset, setShowReset] = useState(false);

  const handleReset = () => {
    if (confirmText === 'CONFIRM RESET') {
      // Perform reset
      alert('System reset performed');
      setConfirmText('');
      setShowReset(false);
    } else {
      alert('Type "CONFIRM RESET" to proceed');
    }
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Scheduling</h1>
      
      <div className="bg-white p-6 rounded shadow-md mb-4">
        <h2 className="text-xl mb-2">Run Solver</h2>
        <button className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600">
          Generate Schedule
        </button>
      </div>
      
      <div className="bg-white p-6 rounded shadow-md">
        <h2 className="text-xl mb-2">Hidden Reset (Admin Only)</h2>
        {!showReset ? (
          <button 
            onClick={() => setShowReset(true)} 
            className="bg-red-500 text-white px-4 py-2 rounded hover:bg-red-600"
          >
            Show Reset Option
          </button>
        ) : (
          <div>
            <p className="mb-2">Type "CONFIRM RESET" to proceed:</p>
            <input
              type="text"
              value={confirmText}
              onChange={(e) => setConfirmText(e.target.value)}
              className="w-full p-2 border border-gray-300 rounded mb-2"
            />
            <button 
              onClick={handleReset} 
              className="bg-red-700 text-white px-4 py-2 rounded hover:bg-red-800"
            >
              Reset System
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default Scheduling;