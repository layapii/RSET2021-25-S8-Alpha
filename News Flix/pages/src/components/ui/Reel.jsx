import { FaWhatsapp, FaFacebook, FaLink } from "react-icons/fa";
import { FaXTwitter } from "react-icons/fa6";
import { ToastContainer, toast } from "react-toastify";

const Reel = ({ reelUrl }) => {
  return (
    <div className="reel">
      <video key={reelUrl} src={reelUrl} controls>
        <source src={reelUrl} type="video/mp4" />
      </video>

      <div id="socials">
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
      
      <ToastContainer />
    </div>
  );
};

export default Reel;
