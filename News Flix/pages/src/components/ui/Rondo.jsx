import { useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { api } from '@/api';
import styled from "styled-components";
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const Rondo = () => {
  const navigate = useNavigate();
  const fileInputRef = useRef(null);

  const handleFileInput = async (event) => {
    try {
      const file = event.target.files[0];

      if (file.type.startsWith('image/')) {
        toast.info('Processing image. Please wait...', { autoClose: 15000 });
        const formData = new FormData();
        formData.append('image', file);
        const response = await api.post('/news/image', formData, { headers: {'Content-Type': 'multipart/form-data',}, });
        const ocrText = response.data.text; // contains the text in a field named 'text'
        navigate('/video', { state: { text: ocrText, type: 'notDemo' } });
      } 
      else if (file.type === 'application/pdf') {
        const reader = new FileReader();
        reader.onload = (e) => {
          const pdfData = e.target.result;
          navigate('/pdf', { state: { pdfData, fileName: file.name } });
        };
        reader.readAsArrayBuffer(file);
      }
      else {
        throw new Error('Unsupported file type');
      }
    } catch (error) {
      toast.error('ERROR');
      console.error('Error uploading file:', error);
    }
  };

  const handleTextInput = () => {
    navigate('/video', { state: { text: '', type: 'notDemo'} });
  };

  return (
    <StyledWrapper>
      <div className="rondo">

        <p onClick={() => fileInputRef.current.click()}>
          <span>News File 📰</span>
        </p>
        <input
          type="file"
          accept="image/*,application/pdf"
          ref={fileInputRef}
          style={{ display: 'none' }}
          onChange={handleFileInput}
        />

        <p onClick={handleTextInput}>
          <span>Article Text 📝</span>
        </p>

        <p onClick={() => navigate('/history')}>
          <span>Reel History 💾</span>
        </p>
        
      </div>
      <ToastContainer />
    </StyledWrapper>
  );
};

const StyledWrapper = styled.div`
  .rondo {
    width: 320px;
    height: 254px;
    border-radius: 14px;
    background: rgba(33, 33, 33, 0.3); /* Set transparency here */
    display: flex;
    gap: 8px;
    padding: 0.4em;
  }

  .rondo p {
    height: 100%;
    flex: 1;
    overflow: hidden;
    cursor: pointer;
    border-radius: 10px;
    transition: all 0.5s;
    background: rgba(33, 33, 33, 0.01); /* Set transparency here */
    border: 8px solid rgba(255, 255, 255, 0.8); /* Set transparency here */
    display: flex;
    justify-content: center;
    align-items: center;
  }

  .rondo p:hover {
    flex: 4;
  }

  .rondo p span {
    min-width: 14em;
    padding: 0.5em;
    text-align: center;
    transform: rotate(-90deg);
    transition: all 0.5s;
    text-transform: none;
    font-weight: 400;
    font-size: 1.1em;
    color: rgba(255, 255, 255, 0.8); /* Set transparency here */
    letter-spacing: 0.1em;
  }

  .rondo p:hover span {
    transform: rotate(0);
  }
`;

export default Rondo;
