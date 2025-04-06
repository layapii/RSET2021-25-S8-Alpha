import React, { useState, useEffect } from 'react';
import SplitText from "./SplitText";
import BlurText from "./BlurText";
import { CButton } from '@coreui/react';
import { Link } from "react-router-dom";

const HomePage = () => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [accessToken, setAccessToken] = useState(localStorage.getItem('googleAccessToken') || '');
  const [isProcessing, setIsProcessing] = useState(false);
  const [processResult, setProcessResult] = useState(null);
  const [processingError, setProcessingError] = useState(null);
  const [folders, setFolders] = useState([]);


  const handleAnimationComplete = () => {
    console.log('Animation completed!');
  };
  const handleShowGalleryClick = async () => {
    if (!accessToken) {
      alert('Please login with Google first');
      return;
    }
  
    const folderName = prompt("Enter the folder name you want to open:");
  
    if (!folderName) {
      alert("You must enter a folder name!");
      return;
    }
  
    try {
      const response = await fetch('http://localhost:5000/list-folders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`,
        },
        body: JSON.stringify({ accessToken, folderName }),
      });
  
      const result = await response.json();
  
      if (response.ok && result.folderId) {
        // Open the Google Drive folder in a new tab
        window.open(`https://drive.google.com/drive/folders/${result.folderId}`, '_blank');
      } else {
        alert('Folder not found or an error occurred.');
      }
    } catch (err) {
      console.error('Fetch failed:', err.message);
      alert('Failed to open the folder. Try again.');
    }
  };
  

  const handleDeduplicationClick = async () => {
    if (!accessToken) {
      alert('Please login with Google first');
      return;
    }
    
    setIsProcessing(true);
    setProcessResult(null);
    setProcessingError(null);
    
    try {
      const response = await fetch('http://localhost:5000/run-deduplication', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`
        },
        body: JSON.stringify({ accessToken }),
      });
  
      const result = await response.json();
      
      if (response.ok) {
        setProcessResult({
          message: result.message,
          duplicates_found: result.duplicates_found || 0
        });
      } else {
        const errorMsg = result.details || result.error || 'Unknown error occurred';
        setProcessingError(errorMsg);
        console.error('Deduplication failed:', errorMsg);
      }
    } catch (error) {
      const errorMsg = error.message || 'Network error occurred';
      setProcessingError(errorMsg);
      console.error('Request failed:', error);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCategorizeClick = async () => {
    if (!accessToken) {
      alert('Please login with Google first');
      return;
    }
  
    const folderName = prompt("Enter the folder name to categorize images:");
  
    if (!folderName) {
      alert("You must enter a folder name!");
      return;
    }
  
    try {
      const response = await fetch('http://localhost:5000/categorize', {

        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${accessToken}`  // ✅ Include token in headers
        },
        body: JSON.stringify({ accessToken, folderName }),  // ✅ Also send in body
      });
  
      const result = await response.json();
  
      if (response.ok) {
        alert('Categorization Completed ');
      } else {
        alert('Categorization failed: ' + result.error);
      }
    } catch (err) {
      console.error('Categorization failed:', err.message);
      alert('Failed to categorize images.');
    }
  };
  

  
  
  useEffect(() => {
    const handleMouseMove = (e) => {
      setMousePosition({
        x: (e.clientX / window.innerWidth) * 100,
        y: (e.clientY / window.innerHeight) * 100,
      });
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, []);

  // Listen for token changes from other components
  useEffect(() => {
    const storedToken = localStorage.getItem('googleAccessToken');
    if (storedToken !== accessToken) {
      setAccessToken(storedToken || '');
    }
  }, [accessToken]);

  return (
    <div className="relative h-screen w-full overflow-hidden">
      {/* Dynamic Background */}
      <div 
        className="absolute inset-0 transition-all duration-1000 ease-in-out"
        style={{
          background: `
            radial-gradient(circle at ${mousePosition.x}% ${mousePosition.y}%, 
              rgba(0, 128, 128, 0.4) 0%, /* Teal */
              transparent 40%),
            radial-gradient(circle at ${100 - mousePosition.x}% ${mousePosition.y}%, 
              rgba(255, 0, 255, 0.4) 0%, /* Magenta */
              transparent 40%),
            radial-gradient(circle at ${mousePosition.y}% ${mousePosition.x}%, 
              rgba(255, 215, 0, 0.4) 0%, /* Gold */
              transparent 40%),
            linear-gradient(
              180deg,
              rgba(10, 10, 30, 0.95) 0%,
              rgba(10, 10, 30, 1) 100%
            )
          `,
          filter: 'blur(8px)',
        }}
      />

      {/* Main Content */}
      <div className="h-screen w-full relative flex flex-col items-center justify-center">
        <div className="relative z-10 mt-8">
          <div 
            className="px-12 py-4 rounded-full shadow-lg flex items-center justify-center space-x-12"
            style={{
              background: 'rgba(0, 0, 0, 0.3)',
              backdropFilter: 'blur(10px)',
              boxShadow: '0 4px 30px rgba(0, 0, 0, 0.1)'
            }}
          >
            <Link to="/home" className="text-white text-lg font-medium">Home</Link>
            <Link to="/about-us" className="text-white text-lg font-medium">About Us</Link>
            <Link to="/contact-us" className="text-white text-lg font-medium">Contact Us</Link>
          </div>
        </div>

        <div className="flex-1 flex -mt-40 flex-col items-center justify-center space-y-4">
          <SplitText
            text="DUPFREE"
            className="text-8xl md:text-9xl lg:text-[12rem] xl:text-[15rem] font-bold text-white font-doodle"
            delay={200}
            animationFrom={{ opacity: 0, transform: 'translate3d(0,50px,0)' }}
            animationTo={{ opacity: 1, transform: 'translate3d(0,0,0)' }}
            easing="easeOutCubic"
          />
          <BlurText
            text="Because Every Memory Deserves Space"
            delay={150}
            animateBy="words"
            direction="top"
            onAnimationComplete={handleAnimationComplete}
            className="text-5xl mb-8 text-white"
          />
          
          {!accessToken && (
            <div className="text-white text-xl mb-6">
              <p>Please log in with Google to use duplicate detection</p>
            </div>
          )}
      
          <div className="absolute bottom-20 flex gap-10 items-center justify-center z-30">
            <CButton 
              color="primary" 
              variant="ghost" 
              onClick={handleDeduplicationClick}
              disabled={isProcessing}
              className="text-xl px-8 py-3 text-white border-2 border-white-400 rounded-full 
              bg-gradient-to-r from-pink-400 via-rose-500 to-fuchsia-500
              hover:from-pink-500 hover:via-rose-600 hover:to-fuchsia-600 hover:border-pink-500 
              transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed">
              {isProcessing ? 'Processing...' : 'Find Duplicates'}
            </CButton>
            <CButton 
              color="secondary" 
              variant="ghost" 
              onClick={handleShowGalleryClick}
              className="text-xl px-8 py-3 text-white border-2 border-white-400 rounded-full
              bg-gradient-to-r from-pink-400 to-orange-500
              hover:from-pink-500 hover:to-orange-600 hover:border-pink-500
              transition-all duration-300">
              Show Gallery
            </CButton>
            <CButton 
              color="secondary" 
              variant="ghost" 
              onClick={handleCategorizeClick}
              className="text-xl px-8 py-3 text-white border-2 border-white-400 rounded-full 
              bg-gradient-to-r from-violet-400 via-purple-500 to-indigo-600
              hover:from-violet-500 hover:via-purple-600 hover:to-indigo-700 hover:border-violet-500 
              transition-all duration-300">
              Categories
            </CButton>
          </div>
        </div>
      </div>
      
      {/* Success Results Modal */}
      {processResult && !processingError && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black/70">
          <div className="bg-white p-6 rounded-xl max-w-lg w-full">
            <h3 className="text-2xl font-bold mb-4">Deduplication Results</h3>
            <p className="mb-4">Found {processResult.duplicates_found} duplicate image pairs!</p>
            <p className="mb-6">Results have been saved to a folder named "Duplicates" in your Google Drive.</p>
            <div className="flex justify-end">
              <button 
                onClick={() => setProcessResult(null)}
                className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Error Modal */}
      {processingError && (
        <div className="fixed inset-0 flex items-center justify-center z-50 bg-black/70">
          <div className="bg-white p-6 rounded-xl max-w-lg w-full">
            <h3 className="text-2xl font-bold mb-4 text-red-600">Error</h3>
            <p className="mb-6">{processingError}</p>
            <div className="flex justify-end">
              <button 
                onClick={() => setProcessingError(null)}
                className="px-4 py-2 bg-red-500 text-white rounded-md hover:bg-red-600"
              >
                Close
              </button>
            </div>
          </div>
        </div>
      )}
    </div>   
  );
};

export default HomePage;