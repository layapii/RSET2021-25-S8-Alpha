import { GoogleOAuthProvider } from "@react-oauth/google";
import { BrowserRouter as Router, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./components/LoginPage";
import HomePage from "./components/home";
import AboutUsPage from "./components/aboutus";
import ContactUs from "./components/contactus";
// ✅ Redirect to login if user is not authenticated
const ProtectedRoute = ({ element }) => {
  const accessToken = localStorage.getItem("googleAccessToken");
  return accessToken ? element : <Navigate to="/" replace />;
};

function App() {
  return (
    <GoogleOAuthProvider clientId="262796229480-barh86ehugq8vjos2tk43t6ini00jtha.apps.googleusercontent.com">
      <Router>
        <Routes>
          <Route path="/" element={<LoginPage />} />
          <Route path="/home" element={<ProtectedRoute element={<HomePage />} />} />
          <Route path="/about-us" element={<AboutUsPage />} />
          <Route path="/contact-us" element={<ContactUs />} />
          

        </Routes>
      </Router>
    </GoogleOAuthProvider>
  );
}

export default App;
