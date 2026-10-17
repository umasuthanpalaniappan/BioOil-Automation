import { useRef, useState } from "react";
import { Header } from "./components/Header";
import { Hero } from "./components/Hero";
import { WorkflowTabs } from "./components/WorkflowTabs";
import { FeaturesSection } from "./components/FeaturesSection";
import { HumanControlSection } from "./components/HumanControlSection";
import { FAQ } from "./components/FAQ";
import { FinalCTA } from "./components/FinalCTA";
import { Footer } from "./components/Footer";
import { DemoModal } from "./components/DemoModal";

function App() {
  const [demoOpen, setDemoOpen] = useState(false);
  const lastTriggerRef = useRef<HTMLElement | null>(null);

  const openDemo = () => {
    lastTriggerRef.current = document.activeElement as HTMLElement | null;
    setDemoOpen(true);
  };

  const closeDemo = () => setDemoOpen(false);

  return (
    <>
      <Header onLaunchDemo={openDemo} />
      <main>
        <Hero onLaunchDemo={openDemo} />
        <WorkflowTabs />
        <FeaturesSection />
        <HumanControlSection />
        <FAQ />
        <FinalCTA onLaunchDemo={openDemo} />
      </main>
      <Footer />
      {demoOpen && <DemoModal onClose={closeDemo} triggerRef={lastTriggerRef} />}
    </>
  );
}

export default App;
