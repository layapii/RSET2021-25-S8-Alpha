import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from "react-router-dom";

const ContactUs = () => {
  const [mousePosition, setMousePosition] = useState({ x: 50, y: 50 });
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    message: ''
  });
  const [showSuccessPopup, setShowSuccessPopup] = useState(false);
  const [submitStatus, setSubmitStatus] = useState('');
  const navigate = useNavigate();

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

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    
    const formDataToSend = new FormData(event.target);
    // Add the access key
    formDataToSend.append("access_key", "YOUR_ACCESS_KEY_HERE");
    
    try {
      const response = await fetch("https://api.web3forms.com/submit", {
        method: "POST",
        body: formDataToSend
      });

      const data = await response.json();

      if (data.success) {
        setSubmitStatus("Form Submitted Successfully");
        setShowSuccessPopup(true);
        // Clear the form
        setFormData({ name: '', email: '', message: '' });
      } else {
        console.log("Error", data);
        setSubmitStatus(data.message || "Something went wrong");
      }
    } catch (error) {
      console.error("Error submitting form:", error);
      setSubmitStatus("Failed to submit. Please try again.");
    }
  };

  const handleGoHome = () => {
    navigate('/home');
  };

  const handleClose = () => {
    setShowSuccessPopup(false);
  };

  return (
    <div className="relative h-screen w-full overflow-hidden">
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

      {/* ✅ Contact Form - Positioned lower */}
      <div className="relative z-10 flex justify-center items-end pt-5">
        <div 
          className="w-full max-w-md p-8 rounded-xl"
          style={{
            background: 'rgba(255, 255, 255, 0.1)',
            backdropFilter: 'blur(10px)',
            boxShadow: '0 8px 32px rgba(0, 0, 0, 0.2)'
          }}
        >
          <h2 className="text-white text-2xl font-bold mb-6 text-center">Get In Touch</h2>
          
          <form onSubmit={handleSubmit} className="box-left">
            {/* Web3Forms access key (replace with your actual key) */}
            <input type="hidden" name="access_key" value="d5b03d29-6cf5-4dad-b7e1-0a0336217699" />
            
            <div className="mb-4">
              <label htmlFor="name" className="block text-white text-sm font-medium mb-2">Name</label>
              <input
                type="text"
                id="name"
                name="name"
                value={formData.name}
                onChange={handleChange}
                className="w-full px-4 py-2 bg-white bg-opacity-20 rounded-lg border border-white border-opacity-30 text-white placeholder-white placeholder-opacity-70 focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="Your name"
                required
              />
            </div>
            
            <div className="mb-4">
              <label htmlFor="email" className="block text-white text-sm font-medium mb-2">Email</label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                className="w-full px-4 py-2 bg-white bg-opacity-20 rounded-lg border border-white border-opacity-30 text-white placeholder-white placeholder-opacity-70 focus:outline-none focus:ring-2 focus:ring-teal-500"
                placeholder="your.email@example.com"
                required
              />
            </div>
            
            <div className="mb-6">
              <label htmlFor="message" className="block text-white text-sm font-medium mb-2">Message</label>
              <textarea
                id="message"
                name="message"
                value={formData.message}
                onChange={handleChange}
                rows="5"
                className="w-full px-4 py-2 bg-white bg-opacity-20 rounded-lg border border-white border-opacity-30 text-white placeholder-white placeholder-opacity-70 focus:outline-none focus:ring-2 focus:ring-teal-500 resize-none"
                placeholder="Tell us about your issue..."
                required
              ></textarea>
            </div>

            {/* Honeypot field to prevent spam */}
            <input type="checkbox" name="botcheck" className="hidden" style={{ display: 'none' }} />
            
            <button
              type="submit"
              className="w-full py-3 px-6 text-white font-medium rounded-lg transition-all duration-300"
              style={{
                background: 'linear-gradient(135deg, rgba(0, 128, 128, 0.8) 0%, rgba(255, 0, 255, 0.8) 100%)',
                boxShadow: '0 4px 15px rgba(0, 0, 0, 0.2)'
              }}
            >
              Send Message
            </button>
            
            {/* Submission status message */}
            {submitStatus && !showSuccessPopup && (
              <p className="mt-4 text-center text-white">{submitStatus}</p>
            )}
          </form>
        </div>
      </div>

      {/* ✅ Success Popup */}
      {showSuccessPopup && (
        <div className="fixed inset-0 flex items-center justify-center z-50">
          {/* Overlay */}
          <div 
            className="absolute inset-0 bg-black bg-opacity-50 backdrop-blur-sm"
            onClick={handleClose}
          ></div>
          
          {/* Popup */}
          <div className="relative z-10 w-full max-w-md p-8 rounded-2xl transform transition-all duration-300 scale-100 opacity-100"
            style={{
              background: 'rgba(255, 255, 255, 0.15)',
              backdropFilter: 'blur(12px)',
              boxShadow: '0 25px 50px -12px rgba(0, 0, 0, 0.25), 0 0 0 1px rgba(255, 255, 255, 0.1) inset',
              border: '1px solid rgba(255, 255, 255, 0.2)'
            }}
          >
            {/* Success Icon */}
            <div className="flex justify-center mb-6">
              <div className="rounded-full p-4 bg-green-500 bg-opacity-20">
                <svg 
                  className="w-12 h-12 text-green-500" 
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24" 
                  xmlns="http://www.w3.org/2000/svg"
                >
                  <path 
                    strokeLinecap="round" 
                    strokeLinejoin="round" 
                    strokeWidth="2" 
                    d="M5 13l4 4L19 7"
                  ></path>
                </svg>
              </div>
            </div>
            
            <h3 className="text-white text-2xl font-bold text-center mb-2">Message Sent Successfully!</h3>
            <p className="text-white text-opacity-80 text-center mb-6">Thank you for reaching out. We'll get back to you soon.</p>
            
            <div className="flex space-x-4">
              <button
                onClick={handleGoHome}
                className="flex-1 py-3 text-white font-medium rounded-lg transition-all duration-300"
                style={{
                  background: 'rgba(0, 128, 128, 0.6)',
                  boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)'
                }}
              >
                Go Home
              </button>
              <button
                onClick={handleClose}
                className="flex-1 py-3 text-white font-medium rounded-lg transition-all duration-300"
                style={{
                  background: 'rgba(255, 255, 255, 0.1)',
                  boxShadow: '0 4px 15px rgba(0, 0, 0, 0.1)',
                  border: '1px solid rgba(255, 255, 255, 0.2)'
                }}
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

export default ContactUs;