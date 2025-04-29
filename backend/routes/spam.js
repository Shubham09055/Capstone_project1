// spam.js
const express = require('express');
const { checkSpam } = require('../controllers/spam');
const { protect } = require('../middlewares/auth');

const router = express.Router();

router.post('/check', protect, checkSpam);

module.exports = router;
