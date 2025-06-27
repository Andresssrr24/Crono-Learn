import { BrowserRouter, Routes, Route } from "react-router-dom";
import { HomePage } from "./pages/Homepage";
import { PomodoroPage } from "./pages/PomodoroPage";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<HomePage/>} />
        <Route path="/pomodoro" element={<PomodoroPage/>} />
        <Route path="/other-route" element={<HomePage/>} />
      </Routes>
    </BrowserRouter>
  )
}

export default App;