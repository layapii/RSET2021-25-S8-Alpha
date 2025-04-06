import React, { useState, useEffect } from 'react';
import { Link } from "react-router-dom";

const AboutUsPage = () => {
  const [mousePosition, setMousePosition] = useState({ x: 50, y: 50 });

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

  return (
    <div className="relative min-h-screen w-full overflow-hidden flex flex-col">
      {/* ✅ Dynamic Background */}
      <div 
        className="absolute inset-0 transition-all duration-1000 ease-in-out"
        style={{
          background: `
            radial-gradient(circle at ${mousePosition.x}% ${mousePosition.y}%, rgba(0, 128, 128, 0.4) 0%, transparent 40%),
            radial-gradient(circle at ${100 - mousePosition.x}% ${mousePosition.y}%, rgba(255, 0, 255, 0.4) 0%, transparent 40%),
            radial-gradient(circle at ${mousePosition.y}% ${mousePosition.x}%, rgba(255, 215, 0, 0.4) 0%, transparent 40%),
            linear-gradient(180deg, rgba(10, 10, 30, 0.95) 0%, rgba(10, 10, 30, 1) 100%)
          `,
          filter: 'blur(8px)',
        }}
      />

      {/* ✅ Navigation Section */}
      <div className="relative z-10 mt-8 flex justify-center">
        <div 
          className="px-12 py-4 rounded-full shadow-lg flex items-center space-x-12"
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
      
      {/* ✅ About Us Content Box - Main Container with Scroll */}
      <div className="relative z-10 flex-1 flex justify-center items-center p-4 overflow-auto">
        <div 
          className="w-full max-w-6xl mx-auto p-6 rounded-xl flex flex-col md:flex-row gap-6 md:gap-8 overflow-auto max-h-full"
          style={{
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}
        >
          {/* Left Side - Text Content */}
          <div className="w-full md:w-1/2 text-white">
            <h1 className="text-3xl md:text-4xl font-bold mb-4 text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-purple-500">
              About Us
            </h1>
            
            <p className="text-lg md:text-xl mb-6 leading-relaxed">
              DupFree is an advanced solution for organizing Google Drive photos with precision. 
              Using machine learning, we help users <span className="font-bold">visualize photos, detect fine duplicates, 
              and categorize images</span> into meaningful groups like Vehicles, Animals, and Flowers.
            </p>
            
            <h2 className="text-xl md:text-2xl font-bold mb-3 text-cyan-300">What We Do</h2>
            <div className="space-y-2 mb-6">
              <div className="flex items-start gap-2">
                <div className="text-green-400 text-lg">✅</div>
                <div>
                  <span className="font-bold">Visualize:</span> Easily browse your Google Drive photos.
                </div>
              </div>
              <div className="flex items-start gap-2">
                <div className="text-green-400 text-lg">✅</div>
                <div>
                  <span className="font-bold">Detect Duplicates:</span> Identify near-duplicate images with AI.
                </div>
              </div>
              <div className="flex items-start gap-2">
                <div className="text-green-400 text-lg">✅</div>
                <div>
                  <span className="font-bold">Categorize:</span> Organize images into predefined categories.
                </div>
              </div>
            </div>
            
            <h2 className="text-xl md:text-2xl font-bold mb-3 text-cyan-300">Our Team</h2>
            <p className="mb-3">
              Developed as a <span className="font-bold">B.Tech final-year project</span> at 
              <span className="font-bold"> Rajagiri School of Engineering, Kakkanad</span>, by:
            </p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 mb-6">
              <div className="flex items-center gap-2">
                <div className="text-blue-400 text-base">🔹</div>
                <div>Alan Anu Sam</div>
              </div>
              <div className="flex items-center gap-2">
                <div className="text-blue-400 text-base">🔹</div>
                <div>Allwyn Antony Rodrigues</div>
              </div>
              <div className="flex items-center gap-2">
                <div className="text-blue-400 text-base">🔹</div>
                <div>Adithyan Darshan Kidav</div>
              </div>
              <div className="flex items-center gap-2">
                <div className="text-blue-400 text-base">🔹</div>
                <div>Aedna Mary Regi</div>
              </div>
            </div>
            
            <p className="text-lg font-bold text-center py-3 bg-gradient-to-r from-purple-500 to-cyan-500 rounded-lg">
              Stay organized effortlessly with <span className="font-bold">DupFree</span>! 🚀
            </p>
          </div>
          
          {/* Right Side - Image and Visual Elements */}
          <div className="w-full md:w-1/2 flex flex-col items-center justify-between gap-4">
            {/* Main Image - Team Photo (Updated) */}
            <div 
              className="rounded-xl overflow-hidden shadow-xl w-full h-52 md:h-64 relative"
            >
              <img 
                src="src/assets/team.png" 
                alt="DupFree Team Members" 
                className="w-full h-full object-cover"
              />
              {/* Caption overlay */}
              
            </div>
            
            {/* Feature Icons */}
            <div className="grid grid-cols-3 gap-3 w-full">
              <div className="flex flex-col items-center p-3 rounded-lg" style={{
                background: 'rgba(0, 0, 0, 0.3)',
                backdropFilter: 'blur(5px)',
              }}>
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center mb-2">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 4.5C7 4.5 2.73 7.61 1 12C2.73 16.39 7 19.5 12 19.5C17 19.5 21.27 16.39 23 12C21.27 7.61 17 4.5 12 4.5ZM12 17C9.24 17 7 14.76 7 12C7 9.24 9.24 7 12 7C14.76 7 17 9.24 17 12C17 14.76 14.76 17 12 17ZM12 9C10.34 9 9 10.34 9 12C9 13.66 10.34 15 12 15C13.66 15 15 13.66 15 12C15 10.34 13.66 9 12 9Z" fill="white"/>
                  </svg>
                </div>
                <span className="text-white text-center text-sm font-medium">Visualize</span>
              </div>
              
              <div className="flex flex-col items-center p-3 rounded-lg" style={{
                background: 'rgba(0, 0, 0, 0.3)',
                backdropFilter: 'blur(5px)',
              }}>
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-purple-500 to-pink-600 flex items-center justify-center mb-2">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M15 3L17 5L19 3L21 5V7L19 9L21 11V13L19 15L17 13L15 15V13L13 11L15 9V7L13 5L15 3ZM16 10C16.5523 10 17 9.55228 17 9C17 8.44772 16.5523 8 16 8C15.4477 8 15 8.44772 15 9C15 9.55228 15.4477 10 16 10Z" fill="white"/>
                    <path d="M3 15L5 17L7 15L9 17V19L7 21L9 23H7L5 21L3 23H1L3 21L1 19V17L3 15ZM4 18C4.55228 18 5 17.5523 5 17C5 16.4477 4.55228 16 4 16C3.44772 16 3 16.4477 3 17C3 17.5523 3.44772 18 4 18Z" fill="white"/>
                    <path d="M8 3L9 5H15L16 3H18L17 5L18 7H16L15 9H9L8 7H6L7 5L6 3H8Z" fill="white"/>
                  </svg>
                </div>
                <span className="text-white text-center text-sm font-medium">Detect Duplicates</span>
              </div>
              
              <div className="flex flex-col items-center p-3 rounded-lg" style={{
                background: 'rgba(0, 0, 0, 0.3)',
                backdropFilter: 'blur(5px)',
              }}>
                <div className="w-12 h-12 rounded-full bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center mb-2">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M3 5H9V11H3V5ZM3 13H9V19H3V13ZM11 5H17V11H11V5ZM11 13H17V19H11V13ZM19 5H21V11H19V5ZM19 13H21V19H19V13Z" fill="white"/>
                  </svg>
                </div>
                <span className="text-white text-center text-sm font-medium">Categorize</span>
              </div>
            </div>
            
            {/* Tech Stack */}
            <div className="w-full p-4 rounded-lg" style={{
              background: 'rgba(0, 0, 0, 0.3)',
              backdropFilter: 'blur(5px)',
            }}>
              <h3 className="text-lg font-semibold mb-3 text-cyan-300">Technology Stack</h3>
              <div className="grid grid-cols-2 gap-2">
                <div className="flex items-center gap-2 bg-gradient-to-r from-gray-800 to-gray-900 p-2 rounded-lg">
                  <div className="w-6 h-6 rounded-full bg-blue-500 flex items-center justify-center text-xs font-bold text-white">ML</div>
                  <span className="text-white text-sm">Machine Learning</span>
                </div>
                <div className="flex items-center gap-2 bg-gradient-to-r from-gray-800 to-gray-900 p-2 rounded-lg">
                  <div className="w-6 h-6 rounded-full bg-green-500 flex items-center justify-center text-xs font-bold text-white">GD</div>
                  <span className="text-white text-sm">Google Drive API</span>
                </div>
                <div className="flex items-center gap-2 bg-gradient-to-r from-gray-800 to-gray-900 p-2 rounded-lg">
                  <div className="w-6 h-6 rounded-full bg-purple-500 flex items-center justify-center text-xs font-bold text-white">CV</div>
                  <span className="text-white text-sm">Computer Vision</span>
                </div>
                <div className="flex items-center gap-2 bg-gradient-to-r from-gray-800 to-gray-900 p-2 rounded-lg">
                  <div className="w-6 h-6 rounded-full bg-red-500 flex items-center justify-center text-xs font-bold text-white">RE</div>
                  <span className="text-white text-sm">React</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AboutUsPage;