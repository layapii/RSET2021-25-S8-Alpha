import { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { api } from '@/api';
import { Textarea } from "@/components/ui/textarea";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue, } from "@/components/ui/select"
import { Button } from "@/components/ui/button";
import { FaWhatsapp, FaFacebook, FaLink} from "react-icons/fa";
import { FaXTwitter } from "react-icons/fa6";
import { ToastContainer, toast } from 'react-toastify';
import 'react-toastify/dist/ReactToastify.css';
import './VideoPage.css';

const VideoPage = () => {
  const location = useLocation();
  const { text: initialText, type } = location.state || { text: '', type: 'notDemo' };
  const [text, setText] = useState(initialText);
  const [language, setLanguage] = useState('');
  const [showReelPlayer, setShowReelPlayer] = useState(false);
  const [reelUrl, setReelUrl] = useState('');

  const handleGenerateClick = async () => {
    //const cacheBuster = new Date().getTime();
    let loadingToast;
    if (language === "") {
      toast.error("Please select a language!");
      return;
    }
    try {
      if (type === 'demo') {
        if (language === 'en')
          setReelUrl(`https://res.cloudinary.com/news-to-reel/video/upload/v1743757100/reel_en.mp4`);
        else if (language === 'hi')
          setReelUrl(`https://res.cloudinary.com/news-to-reel/video/upload/v1743185164/reel_hi.mp4`);
        else if (language === 'ml')
          setReelUrl(`https://res.cloudinary.com/news-to-reel/video/upload/v1743757440/reel_c54k0k.mp4`);
      }
      else {
        loadingToast = toast.info('Generating Reel. Please wait...', { autoClose: 80000 }); // 80 seconds
        const response = await api.post('/news/text', { text, language },);
        setReelUrl(response.data.reel_url);
      }
      toast.dismiss(loadingToast);
      toast.success('Reel Generated!'); 
      setShowReelPlayer(true);
    }
    catch (error) {
        toast.dismiss(loadingToast);
        toast.error('ERROR');
        console.error('Error fetching video:', error);
    }
  };


  return (
    <div id="vp-container">

      <div className="side">
        <div className="grid w-full gap-2">
          <h2 className='headingg'>Preview the News Article</h2>
          <Textarea id="article"
            placeholder="Paste an article here."
            value={text}
            onChange={(event) => setText(event.target.value)}
          />
          
          <Select value={language} onValueChange={setLanguage}>
            <SelectTrigger className="w-2/3 ml-auto">
              <SelectValue placeholder="Reel Language 🔊" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="en">English</SelectItem>
              <SelectItem value="hi">हिन्दी</SelectItem>
              <SelectItem value="ml">മലയാളം</SelectItem>
            </SelectContent>
          </Select>

          <Button onClick={handleGenerateClick} className="w-1/3 ml-auto">Generate</Button>
        </div>
      </div>

      <div className="side">
        {showReelPlayer && (
          <div className="grid">

            <h2 className='headingg'>Generated News Reel</h2>

            <video key={reelUrl} src={reelUrl} controls>
              <source src={reelUrl} type="video/mp4" />
            </video>

            <div id='socials'>
              {/* Facebook Button */}
              <button
                onClick={() => window.open(`https://www.facebook.com/sharer/sharer.php?u=${reelUrl}`, "_blank")}
                style={{background: "white",border: "none",borderRadius: "50%",cursor: "pointer",fontSize: "40px",color: "#4267B2",}}
              >
              <FaFacebook />
              </button>

              {/* WhatsApp Button */}
              <button
                onClick={() => window.open(`https://wa.me/?text=Check out this AI powered video generated using NewsToReel: ${reelUrl}`, "_blank")}
                style={{background: "none",border: "none",cursor: "pointer",fontSize: "40px",color: "#25D366",}}
              >
              <FaWhatsapp />
              </button>

              {/* Twitter Button */}
              <button
                onClick={() => window.open(`https://twitter.com/intent/tweet?url=${reelUrl}&text=Check out this AI powered video generated using NewsToReel!`, "_blank")}
                style={{background: "none",border: "none",cursor: "pointer",fontSize: "40px",color: "#000",}}
              >
              <FaXTwitter />
              </button>

              {/* Copy Link Button */}
              <button
                onClick={() => { navigator.clipboard.writeText(reelUrl); toast.info('Reel share link copied!'); }}
                style={{background: "white", border: "none", borderRadius: "50%", cursor: "pointer", fontSize: "25px", color: "#000", width: "40px", height: "40px", display: "flex", justifyContent: "center", alignItems: "center"}}
              >
              <FaLink />
              </button>
            </div>

          </div>
        )}
      </div>

      <ToastContainer />
    </div>
  );

};

export default VideoPage;