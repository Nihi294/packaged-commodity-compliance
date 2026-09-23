import { Routes, Route } from "react-router-dom";
import Home from "./pages/Home.jsx";
import Inspection from "./pages/Inspection.jsx";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/inspection" element={<Inspection />} />
    </Routes>
  );
}
