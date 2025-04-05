import { useState } from 'react';
import { api } from '@/api';
import { useNavigate } from 'react-router-dom';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';

const Auth = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    try {
      const formData = new FormData();
      formData.append('username', username);
      formData.append('password', password);

      const response = await api.post('/users/login', formData, {
        headers: {'Content-Type': 'multipart/form-data',},
      });

      localStorage.setItem('token', response.data.access_token);
      navigate('/home');
    } catch (error) {
      toast.error('ERROR');
      console.error('Error logging in:', error);
    }
  };

  const handleSignUp = async (e) => {
    e.preventDefault();
    try {
      const response = await api.post('/users', { email: username, password });
      toast.success('Sign-Up successful');
    } catch (error) {
      toast.error('ERROR');
      console.error('Error signing up:', error);
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen">
    <form className="flex flex-col w-full max-w-sm space-y-4 px-10">
      {/* <h1 className="flex justify-center  text-white text-4xl">NewsFlix</h1> */}
      <img src="heading.webp" alt="NewsFlix" />
      <Input type="text" value={username} onChange={e => setUsername(e.target.value)} placeholder="Email" required />
      <Input type="password" value={password} onChange={e => setPassword(e.target.value)} placeholder="Password" required />
      <div className="flex justify-center space-x-4">
        <Button type="submit" onClick={handleLogin}>Sign In</Button>
        <Button variant="secondary" onClick={handleSignUp}>Sign Up</Button>
      </div>
    </form>
    <ToastContainer position="top-center" autoClose={1000}/>
    </div>
  );
};

export default Auth;
