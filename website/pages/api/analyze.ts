import type { NextApiRequest, NextApiResponse } from 'next';
import { spawn } from 'child_process';
import path from 'path';

const analyzeData = (req: NextApiRequest, res: NextApiResponse) => {
  try {
    const { selectedOption, userInput } = req.body;

    // Check if required fields are present
    if (!selectedOption || !userInput) {
      return res.status(400).json({ error: 'Missing required fields' });
    }

    // Set the file paths based on the selected option and user input
    let filePath = '';
    if (selectedOption === 'wikileaks_parsed.xlsx') {
      filePath = path.resolve('data', 'wikileaks_parsed.xlsx');
    } else if (selectedOption === 'news_excerpts_parsed.xlsx') {
      filePath = path.resolve('data', 'news_excerpts_parsed.xlsx');
    } else if (selectedOption === 'test') {
      // Handle text input directly
      console.log(userInput); // You can process this directly in Python or elsewhere
      filePath = ""
      
    } else {
      return res.status(400).json({ error: 'Invalid option selected' });
    }

    // Run the Python script with the provided file and user input
    const pythonCmd = process.platform === "win32" ? "python" : "python3";
    const pythonProcess = spawn(pythonCmd, ['process_data.py', filePath, userInput]);

    let result = '';
    pythonProcess.stdout.on('data', (data) => {
      result += data.toString();
    });

    pythonProcess.stderr.on('data', (data) => {
      console.error('stderr: ' + data.toString());
    });

    pythonProcess.on('close', (code) => {
      if (code !== 0) {
        return res.status(500).json({ error: 'Error executing Python script' });
      }

      // Assuming the network HTML is saved in the public directory
      const networkFilePath = '/entity_network.html'; // Correct path for static file in Next.js

      res.status(200).json({
        result,
        networkFile: networkFilePath,
      });
    });
  } catch (error) {
    console.error(error);
    res.status(500).json({ error: 'An error occurred while processing the request.' });
  }
};

export default analyzeData;
