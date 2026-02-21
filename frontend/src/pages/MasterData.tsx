import React, { useState } from 'react';

const MasterData: React.FC = () => {
  const [teacher, setTeacher] = useState({
    full_name: '',
    title: '',
    status: '',
    workload: '',
    is_senior_old: false,
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Submit to API
    console.log(teacher);
  };

  return (
    <div className="container mx-auto p-4">
      <h1 className="text-2xl font-bold mb-4">Master Data Management</h1>
      
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded shadow-md">
        <div className="mb-4">
          <label className="block text-gray-700">Full Name</label>
          <input
            type="text"
            value={teacher.full_name}
            onChange={(e) => setTeacher({...teacher, full_name: e.target.value})}
            className="w-full p-2 border border-gray-300 rounded"
            required
          />
        </div>
        <div className="mb-4">
          <label className="block text-gray-700">Title</label>
          <select
            value={teacher.title}
            onChange={(e) => setTeacher({...teacher, title: e.target.value})}
            className="w-full p-2 border border-gray-300 rounded"
            required
          >
            <option value="">Select Title</option>
            <option value="INSTRUCTOR_I">Instructor I</option>
            <option value="INSTRUCTOR_II">Instructor II</option>
            <option value="ASST_PROF_III">Assistant Professor III</option>
            <option value="ASST_PROF_IV">Assistant Professor IV</option>
            <option value="ASSOC_PROF_V">Associate Professor V</option>
          </select>
        </div>
        <div className="mb-4">
          <label className="block text-gray-700">Status</label>
          <select
            value={teacher.status}
            onChange={(e) => setTeacher({...teacher, status: e.target.value})}
            className="w-full p-2 border border-gray-300 rounded"
            required
          >
            <option value="">Select Status</option>
            <option value="CONTRACT_OF_SERVICE">Contract of Service</option>
            <option value="PERMANENT">Permanent</option>
          </select>
        </div>
        <div className="mb-4">
          <label className="block text-gray-700">Workload</label>
          <select
            value={teacher.workload}
            onChange={(e) => setTeacher({...teacher, workload: e.target.value})}
            className="w-full p-2 border border-gray-300 rounded"
            required
          >
            <option value="">Select Workload</option>
            <option value="FULL_TIME">Full Time</option>
            <option value="PART_TIME">Part Time</option>
            <option value="VISITING">Visiting</option>
          </select>
        </div>
        <div className="mb-4">
          <label className="flex items-center">
            <input
              type="checkbox"
              checked={teacher.is_senior_old}
              onChange={(e) => setTeacher({...teacher, is_senior_old: e.target.checked})}
              className="mr-2"
            />
            Senior/Old
          </label>
        </div>
        <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
          Add Teacher
        </button>
      </form>
    </div>
  );
};

export default MasterData;