
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import IcsExplanation from "@/components/IcsExplanation";
import HowItWorks from "@/components/HowItWorks";
import AdditionalValues from "@/components/AdditionalValues";
import CTA from "@/components/CTA";
import Footer from "@/components/Footer";

const Index = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50">
      <Hero />
      <Features />
      <IcsExplanation />
      <HowItWorks />
      <AdditionalValues />
      <CTA />
      <Footer />
    </div>
  );
};

export default Index;
