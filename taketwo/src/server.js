const express = require('express');
const cors = require('cors');
const path = require('path');
const mysql = require('mysql2/promise');
const authRoutes = require('./routes/auth');
const mediaContentRoutes = require('./routes/mediaContent');

const app = express();
const port = 5000;

// Database configuration
const pool = mysql.createPool({
  host: 'localhost',
  user: 'Taketwo_user',
  password: 'Anitta',
  database: 'taketwo'
});

// Middleware
app.use(cors({
  origin: 'http://localhost:3000',
  credentials: true
}));
app.use(express.json());

// Serve static files
app.use('/thumbnails', express.static(path.join(__dirname, '../public/thumbnails')));
app.use('/audio_cache', express.static(path.join(__dirname, '../public/audio_cache')));
app.use('/videos', express.static(path.join(__dirname, '../public/videos')));

// Routes
app.use('/api', authRoutes);
app.use('/api', mediaContentRoutes);

// Media content endpoint
app.get('/api/media-content', async (req, res) => {
  try {
    const connection = await pool.getConnection();
    const [rows] = await connection.execute(
      'SELECT content_id, title, description, duration, thumbnail_image FROM media_content'
    );
    connection.release();

    // Transform the data to ensure proper URL formatting
    const transformedData = rows.map(row => ({
      ...row,
      thumbnail_image: row.thumbnail_image.startsWith('/') 
        ? row.thumbnail_image 
        : `/thumbnails/${row.thumbnail_image}`
    }));

    res.json(transformedData);
  } catch (error) {
    console.error('Error fetching media content:', error);
    res.status(500).json({ message: 'Failed to fetch media content' });
  }
});

// Test database connection
app.get('/api/test', async (req, res) => {
  try {
    const [rows] = await pool.execute('SELECT 1');
    res.json({ message: 'Database connection successful', data: rows });
  } catch (error) {
    console.error('Database connection error:', error);
    res.status(500).json({ message: 'Database connection failed', error: error.message });
  }
});

// Error handling middleware
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ message: 'Something broke!', error: err.message });
});

app.listen(port, () => {
  console.log(`Server running on port ${port}`);
}); 