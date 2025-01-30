'use client';
import React, { useState } from 'react';
import axios from 'axios';

const Home: React.FC = () => {
  const [selectedOption, setSelectedOption] = useState<string>('wikileaks_parsed.xlsx');
  const [userInput, setUserInput] = useState<string>(''); // User input like '15.pdf'
  const [loading, setLoading] = useState<boolean>(false);
  const [message, setMessage] = useState<string | null>(null); // For success or error message
  const [result, setResult] = useState<string | null>(null); // To display result from the backend
  const [networkFilePath, setNetworkFilePath] = useState<string | null>(null); // To hold the network file path
  const [jsonDecodeError, setJsonDecodeError] = useState<boolean>(false); // To check for the specific JSON error

  const handleOptionChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedOption(e.target.value);
    setUserInput("")
  };

  const handleUserInputChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    setUserInput(e.target.value); // Update the filename the user enters
  };
  
  const handleSubmit = async () => {
    if (!userInput) {
      alert('Please fill in the input.');
      return;
    }
    setMessage(null); 
    setResult("")
    setJsonDecodeError(false); // Reset the error state
    setLoading(true);
    setNetworkFilePath(null)

    try {
      const form = { selectedOption, userInput };
      
      // Call the backend API
      const response = await axios.post('/api/analyze', form);
      console.log(response.data)
      console.log(response.data.error)
      if (response.data.result.includes('JSON Decode Error:')) {
        // If specific error found, set state to indicate the error
        setJsonDecodeError(true);
       
      }
      if (response.data.result.includes('Error: Selected data not found')) {
        setMessage('Error processing data, selected data not found.');
        
        
      }else if(response.data.result.includes('Error: Expected at least 3 keys')){
        setMessage('Error processing data, please try again later.');
      } 
       else {
        setMessage('Data processed successfully!');
        setResult(response.data.result); // Set the result data
        setNetworkFilePath(response.data.networkFile); // Set the file path for entity-network.html
      }
    } catch (error) {
      setMessage('Error processing the request');
      console.error(error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-8 bg-gray-50 rounded-lg shadow-md max-w-2xl mt-5">
      <h1 className="text-3xl font-semibold text-center text-gray-800 mb-6">Data Upload and Processing</h1>
      
      <div className="mb-4">
        <label htmlFor="option" className="block text-lg font-medium text-gray-700">Select Option:</label>
        <select
          id="option"
          value={selectedOption}
          onChange={handleOptionChange}
          className="w-full p-3 mt-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400 text-black"
        >
          <option value="wikileaks_parsed.xlsx" className="text-black">wikileaks_parsed.xlsx</option>
          <option value="news_excerpts_parsed.xlsx" className="text-black">news_excerpts_parsed.xlsx</option>
          <option value="test" className="text-black">Upload your own text</option>
        </select>
      </div>

      {selectedOption === 'wikileaks_parsed.xlsx' && (
        <div className="mb-4">
          <label htmlFor="userInput" className="block text-lg font-medium text-gray-700">Enter PDF filename:</label>
          <input
            type="text"
            id="userInput"
            value={userInput}
            onChange={handleUserInputChange}
            className="w-full p-3 mt-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400  text-black"
          />
        </div>
      )}
      {selectedOption === 'news_excerpts_parsed.xlsx' && (
        <div className="mb-4">
          <label htmlFor="userInput" className="block text-lg font-medium text-gray-700">Enter Link:</label>
          <input
            type="text"
            id="userInput"
            value={userInput}
            onChange={handleUserInputChange}
            className="w-full p-3 mt-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400  text-black"
          />
        </div>
      )}
      {selectedOption === 'test' && (
        <div className="mb-4">
          <label htmlFor="userInput" className="block text-lg font-medium text-gray-700">Enter text:</label>
          <textarea
            id="userInput"
            value={userInput}
            onChange={handleUserInputChange}
            
            className="w-full p-3 mt-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-blue-400  text-black"
          />
        </div>
      )}

      <div className="flex gap-4">
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="w-full p-3 bg-blue-600 text-white font-semibold rounded-md shadow-md hover:bg-blue-700 disabled:bg-gray-400 disabled:cursor-not-allowed flex justify-center items-center gap-2"
        >
          {loading && (
            <div className="w-5 h-5 border-4 border-white border-t-transparent rounded-full animate-spin"></div>
          )}
          {loading ? 'Processing...' : 'Submit'}
        </button>
      </div>


      {message && (
        <div className="mt-4 text-center text-gray-800">
          <p className={`p-4 rounded-md text-white ${message === 'Data processed successfully!' ? 'bg-green-600' : 'bg-red-600'}`}>
            {message}
          </p>
        </div>
      )}

      {result && (
        <div className="mt-4 p-6 bg-white shadow-lg rounded-lg">
          <h3 className="text-xl font-semibold text-gray-800 mb-4">Processed Result:</h3>
          <div className="bg-gray-100 p-4 rounded-md overflow-auto max-h-96">
            <pre className="text-left text-sm text-gray-800">{result}</pre>
          </div>
        </div>
      )}

{jsonDecodeError && (
        <div className="mt-4 text-center">
          <button
            className="p-3 bg-red-600 text-white font-semibold rounded-md hover:bg-red-700"
            disabled
          >
            Error Creating Entity Network Map, Please Try Again.
          </button>
        </div>
      )}

      {networkFilePath && !jsonDecodeError && (
        <div className="mt-4 text-center">
          <a
            href={networkFilePath}
            target="_blank"
            rel="noopener noreferrer"
            className="p-3 bg-green-600 text-white font-semibold rounded-md hover:bg-green-700"
          >
            View Entity Network Map
          </a>
        </div>
      )}
    </div>
  );
};

export default Home;