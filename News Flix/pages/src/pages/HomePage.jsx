import { useNavigate } from 'react-router-dom';
import Threed from '@/components/ui/Threed';
import Rondo from '@/components/ui/Rondo';

import './HomePage.css'

const HomePage = () => {

  const navigate = useNavigate();

  const handleDemoClick = () => {
    const demoArticle = "US nixes 2,000 visa appointments. The U.S. Embassy in India announced on Wednesday that it had canceled more than 2,000 visa appointments made using automated bots. The embassy issued a statement emphasizing that such actions violate its scheduling policies and reiterated its commitment to upholding the integrity of the visa process. The Consular Team stressed its zero-tolerance policy towards fraud, warning agents and individuals against exploiting the system. 'Consular Team India is canceling about 2,000 visa appointments made by bots. We have zero tolerance for agents and fixers who violate our scheduling policies,' the U.S. Embassy posted on X (formerly Twitter). Visa appointments in India, particularly for B1 and B2 visas (business and tourism), have long been in high demand. This has led to extensive delays, with applicants often waiting over two years for an appointment. In an effort to alleviate the backlog, the U.S. has been offering visa appointments in other countries, such as Frankfurt and Bangkok.";
    navigate('/video', { state: { text: demoArticle, type: 'demo' } });
  };

  return ( 
    <div>
    
      <div id="HomePage">

        <div id="Heading">
          {/* <h1>NewsFlix</h1> */}
          <img src="heading.webp" alt="NewsFlix" />
        </div>

        <div id="Demo">
          <Threed handleDemoClick={handleDemoClick} />
        </div>

        <div id="Left">
          <Rondo />
        </div>

      </div>
  
    </div>
  )
};

export default HomePage;
