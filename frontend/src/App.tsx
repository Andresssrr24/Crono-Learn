import { BrowserRouter, Routes, Route, useLocation } from "react-router-dom";
import { HomePage } from "./pages/Homepage";
import { PomodoroPage } from "./pages/PomodoroPage";
import { SideNav } from "./components/partials/SideNav";
import { SignInPage } from "./pages/SignIn";
import { SignUpPage } from "./pages/SignUp";
import { StudiesPage } from "./pages/StudiesPage";
import { Toaster } from "react-hot-toast";
import { AgentPage } from "./pages/AgentPage";

function AppContent() {
  const location = useLocation();
  const hideSideNavRoutes = ["/sign-in", "/sign-up"];

  const hideSideNav = hideSideNavRoutes.includes(location.pathname);

  return (
    <div className="flex">
      {!hideSideNav && <SideNav />}
      <div className="flex-1">
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/pomodoro" element={<PomodoroPage />} />
          <Route path="/my-studies" element={<StudiesPage />} />
          <Route path="/sign-in" element={<SignInPage />} />
          <Route path="/sign-up" element={<SignUpPage />} />
          <Route path="/agent" element={<AgentPage />} />
        </Routes>
      </div>

      <Toaster />
    </div>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AppContent />
    </BrowserRouter>
  );
}