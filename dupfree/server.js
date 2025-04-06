// server.js
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const axios = require('axios');
const app = express();
const port = 5000;

app.use(cors());
app.use(bodyParser.json());

// Store the Colab notebook URL - you'll need to get this from your Colab notebook
// This is the public URL when you click "Share" -> "Copy Link" in Colab
const COLAB_URL = 'https://colab.research.google.com/drive/1ZsEupuxP_gQMY2rYPJC0EFV4wp73xNML?usp=sharing'; 

// Temporary storage for user sessions
const userSessions = {};

// Authenticate route - just stores basic info from login
app.post('/authenticate', (req, res) => {
  const { accessToken, photoCount } = req.body;
  const sessionId = Math.random().toString(36).substring(2, 15);
  
  userSessions[sessionId] = {
    accessToken,
    photoCount,
    timestamp: Date.now()
  };
  
  console.log(`User authenticated with ${photoCount} photos`);
  res.json({ success: true, sessionId });
});

// Process photos through Colab
app.post('/process-photos', async (req, res) => {
  try {
    const { photos } = req.body;
    
    if (!photos || !Array.isArray(photos)) {
      return res.status(400).json({ error: 'Invalid photo data' });
    }
    
    console.log(`Processing ${photos.length} photos`);
    
    // Extract just the URLs and filenames to send to Colab
    const photoData = photos.map(photo => ({
      url: photo.url,
      filename: photo.filename,
      id: photo.id
    }));
    
    // Here, you'd normally send the data to your Colab notebook via its exposed endpoint
    // For demo purposes, we'll generate mock results if Colab URL isn't configured
    let duplicateResults;
    
    try {
      if (COLAB_URL.includes('YOUR-COLAB-NOTEBOOK-URL')) {
        // Generate mock results for testing
        console.log('Using mock data (Colab URL not configured)');
        duplicateResults = generateMockResults(photoData);
      } else {
        // Send to actual Colab notebook
        const colabResponse = await axios.post(`${COLAB_URL}/process`, {
          photos: photoData
        });
        duplicateResults = colabResponse.data;
      }
    } catch (colabError) {
      console.error('Error connecting to Colab:', colabError);
      // Fall back to mock data if Colab is unavailable
      duplicateResults = generateMockResults(photoData);
    }
    
    // Return the results
    res.json({ success: true, duplicates: duplicateResults });
  } catch (error) {
    console.error('Error processing photos:', error);
    res.status(500).json({ error: 'Failed to process photos' });
  }
});

// Helper function to generate mock duplicate results for testing
function generateMockResults(photos) {
  const results = [];
  
  // Only create mock results if we have enough photos
  if (photos.length < 2) {
    return results;
  }
  
  // Create 1-3 mock duplicate pairs
  const numPairs = Math.min(3, Math.floor(photos.length / 2));
  
  for (let i = 0; i < numPairs; i++) {
    const idx1 = i * 2;
    const idx2 = i * 2 + 1;
    
    if (idx2 < photos.length) {
      results.push({
        image1Id: photos[idx1].id,
        image2Id: photos[idx2].id,
        image1Url: photos[idx1].url + '=w400-h300',
        image2Url: photos[idx2].url + '=w4  00-h300',
        image1Name: photos[idx1].filename,
        image2Name: photos[idx2].filename,
        similarity: 0.75 + (Math.random() * 0.2) // Random similarity between 75-95%
      });
    }
  }
  
  return results;
}

app.listen(port, () => {
  console.log(`Server listening at http://localhost:${port}`);
});