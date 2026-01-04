
const express = require('express');
const bodyParser = require('body-parser');
const axios = require('axios');
const path = require('path');

const app = express();
const PORT = 3000;
const BACKEND_URL = 'http://localhost:8000';

// Middleware
app.use(bodyParser.json());
app.use(express.static(path.join(__dirname, 'public')));
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, 'views'));

// Routes
app.get('/', (req, res) => {
    res.render('index', {
        title: 'MediBo',
        initialModules: {
            perception: 20,
            cognitive: 10,
            action: 5,
            security: 100
        }
    });
});

// Proxy route to avoid CORS issues if any, or just to keep logic encapsulated
app.post('/api/chat', async (req, res) => {
    try {
        const { patient_id, message } = req.body;
        // Forward to Python Backend
        const response = await axios.post(`${BACKEND_URL}/chat`, {
            patient_id,
            message
        });
        res.json(response.data);
    } catch (error) {
        console.error("Error communicating with backend:", error.message);
        res.status(500).json({
            response: "Error: Could not connect to MediBo Brain.",
            action_taken: "Connection Failed"
        });
    }
});

app.listen(PORT, '0.0.0.0', () => {
    console.log(`MediBo Frontend running at http://0.0.0.0:${PORT}`);
});
