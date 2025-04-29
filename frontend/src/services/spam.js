import axios from 'axios';

const API_URL = 'http://localhost:5000/api/spam';

// Check if text is spam
const checkSpam = async (text) => {
  const token = localStorage.getItem('token');
  const response = await axios.post(
    `${API_URL}/check`,
    { text },
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );
  return response.data;
};

export { checkSpam };