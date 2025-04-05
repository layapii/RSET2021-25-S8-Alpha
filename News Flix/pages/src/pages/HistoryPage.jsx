import { useState } from 'react';
import { api } from '@/api';
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group"
import { Button } from "@/components/ui/button";
import { Combobox } from '@/components/ui/Combobox';
import { ToastContainer, toast } from "react-toastify";
import Reel from '@/components/ui/Reel';
import './HistoryPage.css';

const HistoryPage = () => {
    const [languages, setLanguages] = useState([]);
    const [category, setCategory] = useState('');
    const [showReelPlayer, setShowReelPlayer] = useState(false);
    const [reels, setReels] = useState([]);

    const handleLanguageToggle = (value) => {
        setLanguages((prev) => prev.includes(value) ? prev.filter((lang) => lang !== value) : [...prev, value]);
    };

    const handleCategorySelect = (category) => {
        setCategory(category);
    };

    const handleSearchClick = async () => {
        try {
            const response = await api.post('/news/history', { languages, category, });
            console.log(response.data);
            setReels(response.data.reels);
            setShowReelPlayer(true);
        } catch (error) {
            toast.error('ERROR');
            console.error('Error fetching video:', error);
        }    
    }   
    
    return (
    <div>
        <div id="top">
            <div className="filter">
                <h2>Filter by Language</h2>
                <ToggleGroup type="multiple" variant="outline">
                    <ToggleGroupItem value="en" onClick={() => handleLanguageToggle("en")}>English</ToggleGroupItem>
                    <ToggleGroupItem value="hi" onClick={() => handleLanguageToggle("hi")}>हिन्दी</ToggleGroupItem>
                    <ToggleGroupItem value="ml" onClick={() => handleLanguageToggle("ml")}>മലയാളം</ToggleGroupItem>
                </ToggleGroup>
            </div>

            <div className="filter">
                <h2>Filter by Category</h2>
                <Combobox onSelect={handleCategorySelect} />
            </div>

            <Button id="searchButton" onClick={handleSearchClick}>Search 🔍</Button>
        </div>

        {showReelPlayer && (
        <div id="bottom">
            {reels.map((reel, index) => (
                <Reel key={index} reelUrl={reel.reel_url} />
            ))}
        </div>
        )}

        <ToastContainer />

      </div>
    );
}

export default HistoryPage;