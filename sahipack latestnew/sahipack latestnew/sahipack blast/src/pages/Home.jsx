import Navbar from "../components/Navbar.jsx";
import Hero from "../components/Hero.jsx";
import Problem from "../components/Problem.jsx";
import Workflow from "../components/Workflow.jsx";
import Capabilities from "../components/Capabilities.jsx";
import InspectionPreview from "../components/InspectionPreview.jsx";
import TrustSection from "../components/TrustSection.jsx";
import CTA from "../components/CTA.jsx";
import Footer from "../components/Footer.jsx";

export default function Home() {
  return (
    <div className="bg-navy">
      <Navbar />
      <main>
        <Hero />
        <Problem />
        <Workflow />
        <Capabilities />
        <InspectionPreview />
        <TrustSection />
        <CTA />
      </main>
      <Footer />
    </div>
  );
}
