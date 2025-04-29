const axios = require('axios');

exports.checkSpam = async (req, res) => {
  try {
    const { text } = req.body;
    
    const response = await axios.post('http://localhost:5001/predict', { text });
    
    res.json({
      success: true,
      isSpam: response.data.isSpam,
      confidence: response.data.confidence
    });
  } catch (err) {
    console.error(err);
    res.status(500).json({ 
      success: false, 
      error: 'Error contacting the prediction service' 
    });
  }
};