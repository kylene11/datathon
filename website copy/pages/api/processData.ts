import { NextApiRequest, NextApiResponse } from 'next';

// API handler for processing data
const processData = async (req: NextApiRequest, res: NextApiResponse) => {
  if (req.method === 'POST') {
    try {
      // Parse incoming JSON data
      const { selectedOption, userInput } = req.body;

      if (!selectedOption || !userInput) {
        return res.status(400).json({ error: 'Both selectedOption and userInput are required' });
      }

      // Here, you can process the data as needed
      // For example, if you need to do something with the selectedOption or userInput:
      console.log('Selected Option:', selectedOption);
      console.log('User Input:', userInput);

      // Do your processing logic (e.g., check the existence of a PDF, read the Excel file, etc.)

      // For now, we just send back a success message
      return res.status(200).json({ success: true, message: 'Data processed successfully' });
    } catch (error) {
      return res.status(500).json({ error: 'Error processing data' });
    }
  } else {
    return res.status(405).json({ error: 'Method Not Allowed' });
  }
};

export default processData;
